import numpy as np
import numba
import time
from rcta_system.object_detector import ObjectDetector


@numba.jit(nopython=True, fastmath=True)
def _decode_depth_to_meters(array_uint8):
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
        array = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_img.height, carla_img.width, 4))
        return array[:, :, :3]  # Remove alpha channel

    def to_depth_meters(self, carla_img):
        array_uint8 = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
        array_uint8 = np.reshape(array_uint8, (carla_img.height, carla_img.width, 4))
        return _decode_depth_to_meters(array_uint8)

    def fuse_results(self, detections, depth_map):
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
        stale_ids = [
            track_id for track_id, state in tracked_objects.items()
            if current_time - state['time'] > self.STALE_TRACK_THRESHOLD_SEC
        ]

        for track_id in stale_ids:
            del tracked_objects[track_id]
