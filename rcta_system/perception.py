# perception.py
"""
Perception module for RCTA system.
Handles image processing, object detection, tracking, and TTC calculation.
"""

import numpy as np
import numba
import time
from rcta_system.object_detector import ObjectDetector


@numba.jit(nopython=True, fastmath=True)
def _decode_depth_to_meters(array_uint8):
    """
    Fast depth decoding using Numba JIT compilation.

    Args:
        array_uint8: Raw depth image as uint8 array (H, W, 4)

    Returns:
        Depth map in meters as float32 array (H, W)
    """
    h, w, _ = array_uint8.shape
    depth_meters = np.empty((h, w), dtype=np.float32)
    inv_max_val = 1.0 / (256.0 * 256.0 * 256.0 - 1.0)

    for y in range(h):
        for x in range(w):
            B = float(array_uint8[y, x, 0])
            G = float(array_uint8[y, x, 1])
            R = float(array_uint8[y, x, 2])
            normalized = (R + G * 256.0 + B * 256.0 * 256.0) * inv_max_val
            depth_meters[y, x] = normalized * 1000.0

    return depth_meters


class Perception:
    """
    Perception system for RCTA.
    Manages object detection, tracking, and TTC calculation for all three zones.
    """

    def __init__(self):
        """Initialize perception system with detectors for each zone"""
        print("PERCEPTION [Initializing YOLO detectors for all zones]")

        # One detector per zone (independent)
        self.detector_rear = ObjectDetector()
        self.detector_left = ObjectDetector()
        self.detector_right = ObjectDetector()

        # Tracking state for each zone
        self.tracked_objects_rear = {}
        self.tracked_objects_left = {}
        self.tracked_objects_right = {}

        # Cleanup timestamps
        self.last_cleanup_time_rear = 0.0
        self.last_cleanup_time_left = 0.0
        self.last_cleanup_time_right = 0.0

        # Constants
        self.STALE_TRACK_THRESHOLD_SEC = 1.0
        self.MIN_VELOCITY_FOR_TTC_MPS = 0.5

        print("PERCEPTION [Initialized successfully]")

    def to_numpy_rgb(self, carla_img):
        """
        Convert CARLA RGB image to numpy array.

        Args:
            carla_img: CARLA camera image

        Returns:
            RGB numpy array (H, W, 3)
        """
        array = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_img.height, carla_img.width, 4))
        return array[:, :, :3]  # Remove alpha channel

    def to_depth_meters(self, carla_img):
        """
        Convert CARLA depth image to meters.

        Args:
            carla_img: CARLA depth camera image

        Returns:
            Depth map in meters as float32 array (H, W)
        """
        array_uint8 = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
        array_uint8 = np.reshape(array_uint8, (carla_img.height, carla_img.width, 4))
        return _decode_depth_to_meters(array_uint8)

    def fuse_results(self, detections, depth_map):
        """
        Fuse YOLO detections with depth map to get distance.

        Args:
            detections: List of YOLO detections
            depth_map: Depth map in meters (H, W)

        Returns:
            List of detections with distance information added
        """
        h, w = depth_map.shape
        fused = []

        for det in detections:
            x1, y1, x2, y2 = map(int, det['bbox'])

            # Clipping to avoid out of bounds
            x1, x2 = max(0, x1), min(w, x2)
            y1, y2 = max(0, y1), min(h, y2)

            obj_dist = float('inf')
            if x1 < x2 and y1 < y2:
                roi = depth_map[y1:y2, x1:x2]
                if roi.size > 0:
                    # Use 10th percentile to avoid outliers
                    obj_dist = np.percentile(roi, 10)

            det['dist'] = obj_dist
            det['ttc_obj'] = float('inf')  # Will be calculated in tracking
            fused.append(det)

        return fused

    def update_tracks_and_calc_ttc(self, current_objects, current_time, tracked_objects):
        """
        Update object tracking and calculate TTC (Time To Collision).

        Args:
            current_objects: List of current frame detections with distance
            current_time: Current timestamp
            tracked_objects: Dictionary of tracked objects for this zone
        """
        for obj in current_objects:
            track_id = obj['id']

            if track_id in tracked_objects:
                # Object was seen before, calculate velocity and TTC
                prev_state = tracked_objects[track_id]
                delta_t = current_time - prev_state['time']
                delta_d = prev_state['dist'] - obj['dist']  # Positive if approaching

                if delta_t > 0.0:
                    rel_velocity = delta_d / delta_t  # m/s

                    # Only calculate TTC if object is approaching fast enough
                    if rel_velocity > self.MIN_VELOCITY_FOR_TTC_MPS:
                        ttc = obj['dist'] / rel_velocity
                        obj['ttc_obj'] = ttc

            # Update tracking state
            tracked_objects[track_id] = {
                'dist': obj['dist'],
                'time': current_time,
                'class': obj['class']
            }

    def cleanup_stale_tracks(self, current_time, tracked_objects):
        """
        Remove objects that haven't been seen for too long.

        Args:
            current_time: Current timestamp
            tracked_objects: Dictionary of tracked objects for this zone
        """
        stale_ids = [
            track_id for track_id, state in tracked_objects.items()
            if current_time - state['time'] > self.STALE_TRACK_THRESHOLD_SEC
        ]

        for track_id in stale_ids:
            del tracked_objects[track_id]

        if stale_ids:
            print(f"PERCEPTION [Cleaned {len(stale_ids)} stale tracks]")

    def extract_zone_status(self, fused_objects):
        """
        Extract minimum distance and TTC from fused objects.

        Args:
            fused_objects: List of objects with dist and ttc_obj

        Returns:
            Dict with 'dist', 'ttc', 'objects'
        """
        if not fused_objects:
            return {
                'dist': float('inf'),
                'ttc': float('inf'),
                'objects': []
            }

        min_dist = min((obj['dist'] for obj in fused_objects), default=float('inf'))
        min_ttc = min((obj['ttc_obj'] for obj in fused_objects), default=float('inf'))

        return {
            'dist': min_dist,
            'ttc': min_ttc,
            'objects': fused_objects
        }