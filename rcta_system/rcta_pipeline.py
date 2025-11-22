import threading
import numpy as np
import time
import config
import numba
from rcta_system.object_detector import ObjectDetector
from rcta_system.decision_making import DecisionMaker

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

class RCATPipeline(threading.Thread):
    """
        Independent thread-based pipeline for RCTA detection.
        Each pipeline handles its own camera zone (rear, left, right).

        Zero synchronization with other pipelines - completely autonomous.
        """

    def __init__(self, zone_name, mqtt_publisher):
        """
        Args:
            zone_name: "rear", "left", or "right"
            mqtt_publisher: Shared MQTT publisher (thread-safe)
        """
        super().__init__(name=f"Pipeline-{zone_name.upper()}", daemon=True)

        self.zone_name = zone_name
        self.mqtt_publisher = mqtt_publisher

        # Each pipeline has its OWN detector (no sharing)
        print(f"PIPELINE-{zone_name.upper()} [Initializing independent YOLO detector]")
        self.detector = ObjectDetector()

        # Each pipeline has its OWN decision maker
        self.decision_maker = DecisionMaker(zone_name)

        # Local frame buffers (thread-local, no locks needed)
        self.latest_rgb = None
        self.latest_depth = None
        self.display_frame = None

        # Local tracking state (thread-local, no locks needed)
        self.tracked_objects = {}
        self.last_cleanup_time = 0.0

        # Constants
        self.STALE_TRACK_THRESHOLD_SEC = 1.0
        self.MIN_VELOCITY_FOR_TTC_MPS = 0.5

        # Control flag
        self.running = False

        print(f"PIPELINE-{zone_name.upper()} [Initialized successfully]")

        def set_camera_callbacks(self, rgb_sensor, depth_sensor):
            """
            Register callbacks for this pipeline's cameras.

            Args:
                rgb_sensor: CARLA RGB camera sensor
                depth_sensor: CARLA depth camera sensor
            """
            rgb_sensor.listen(self._rgb_callback)
            depth_sensor.listen(self._depth_callback)
            print(f"PIPELINE-{self.zone_name.upper()} [Camera callbacks registered]")

        def _rgb_callback(self, image):
            """Callback for RGB frames (thread-local, no lock needed)"""
            self.latest_rgb = image

        def _depth_callback(self, image):
            """Callback for depth frames (thread-local, no lock needed)"""
            self.latest_depth = image

        def _to_numpy_rgb(self, carla_img):
            """Convert CARLA image to numpy RGB array"""
            array = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
            array = np.reshape(array, (carla_img.height, carla_img.width, 4))
            return array[:, :, :3]

        def _to_depth_meters(self, carla_img):
            """Convert CARLA depth image to meters"""
            array_uint8 = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
            array_uint8 = np.reshape(array_uint8, (carla_img.height, carla_img.width, 4))
            return _decode_depth_to_meters(array_uint8)

        def _fuse_results(self, detections, depth_map):
            """
            Fuse YOLO detections with depth map to get distance.

            Args:
                detections: List of YOLO detections
                depth_map: Depth map in meters

            Returns:
                List of detections with distance information
            """
            h, w = depth_map.shape
            fused = []

            for det in detections:
                x1, y1, x2, y2 = map(int, det['bbox'])
                # Clipping (avoid out of bounds)
                x1, x2 = max(0, x1), min(w, x2)
                y1, y2 = max(0, y1), min(h, y2)

                obj_dist = float('inf')
                if x1 < x2 and y1 < y2:
                    roi = depth_map[y1:y2, x1:x2]
                    if roi.size > 0:
                        obj_dist = np.percentile(roi, 10)

                det['dist'] = obj_dist
                det['ttc_obj'] = float('inf')
                fused.append(det)

            return fused

        def _update_tracks_and_calc_ttc(self, current_objects, current_time):
            """
            Update object tracking and calculate TTC (Time To Collision).

            Args:
                current_objects: List of current frame detections
                current_time: Current timestamp
            """
            for obj in current_objects:
                track_id = obj['id']

                if track_id in self.tracked_objects:
                    prev_state = self.tracked_objects[track_id]
                    delta_t = current_time - prev_state['time']
                    delta_d = prev_state['dist'] - obj['dist']

                    if delta_t > 0.0:
                        rel_velocity = delta_d / delta_t
                        if rel_velocity > self.MIN_VELOCITY_FOR_TTC_MPS:
                            ttc = obj['dist'] / rel_velocity
                            obj['ttc_obj'] = ttc

                self.tracked_objects[track_id] = {
                    'dist': obj['dist'],
                    'time': current_time,
                    'class': obj['class']
                }

        def _cleanup_stale_tracks(self, current_time):
            """Remove objects that haven't been seen for too long"""
            stale_ids = [
                track_id for track_id, state in self.tracked_objects.items()
                if current_time - state['time'] > self.STALE_TRACK_THRESHOLD_SEC
            ]
            for track_id in stale_ids:
                del self.tracked_objects[track_id]

        def process_frame(self):
            """
            Process current frame: detection, tracking, TTC calculation, decision making, MQTT publish.

            Returns:
                Dict with perception data or None if no frames available
            """
            # Check if we have new frames
            if self.latest_rgb is None or self.latest_depth is None:
                return None

            # Get frames (local copies)
            rgb_carla = self.latest_rgb
            depth_carla = self.latest_depth

            # Convert to numpy
            rgb_np = self._to_numpy_rgb(rgb_carla)
            depth_meters = self._to_depth_meters(depth_carla)
            timestamp = depth_carla.timestamp

            # YOLO Detection
            detections = self.detector.detect(rgb_np)

            # Fuse with depth
            fused_objects = self._fuse_results(detections, depth_meters)

            # Cleanup stale tracks periodically
            if timestamp - self.last_cleanup_time > self.STALE_TRACK_THRESHOLD_SEC:
                self._cleanup_stale_tracks(timestamp)
                self.last_cleanup_time = timestamp

            # Update tracking and calculate TTC
            self._update_tracks_and_calc_ttc(fused_objects, timestamp)

            # Calculate minimums for this zone
            min_dist = min((obj['dist'] for obj in fused_objects), default=float('inf'))
            min_sector_ttc = min((obj['ttc_obj'] for obj in fused_objects), default=float('inf'))

            # Save display frame for OpenCV visualization
            self.display_frame = rgb_np.copy()

            # Prepare perception data
            perception_data = {
                'dist': min_dist,
                'ttc': min_sector_ttc,
                'objects': fused_objects
            }

            return perception_data

        def run(self):
            """
            Main thread loop - runs independently from other pipelines.

            Loop:
            1. Wait for new frames
            2. Process frame (detection + tracking + TTC)
            3. Decision making
            4. MQTT publish if alert
            5. Brief sleep to avoid CPU spinning
            """
            print(f"PIPELINE-{self.zone_name.upper()} [Thread started]")
            self.running = True

            while self.running:
                try:
                    # Process current frame
                    perception_data = self.process_frame()

                    if perception_data is None:
                        # No frames yet, wait a bit
                        time.sleep(0.01)
                        continue

                    # Decision making (local to this zone)
                    dangerous_objects = self.decision_maker.evaluate(perception_data)

                    # MQTT publish if there are alerts
                    if dangerous_objects:
                        self.mqtt_publisher.publish_status(dangerous_objects)

                    # Small sleep to avoid CPU spinning
                    time.sleep(0.01)

                except Exception as e:
                    print(f"PIPELINE-{self.zone_name.upper()} [ERROR: {e}]")
                    import traceback
                    traceback.print_exc()
                    time.sleep(0.1)  # Avoid rapid error loop

            print(f"PIPELINE-{self.zone_name.upper()} [Thread stopped]")

        def stop(self):
            """Stop the pipeline thread gracefully"""
            print(f"PIPELINE-{self.zone_name.upper()} [Stopping...]")
            self.running = False

        def get_display_frame(self):
            """Get current frame for OpenCV display (thread-safe read)"""
            return self.display_frame

        def get_perception_data(self):
            """Get latest perception data (for debug purposes)"""
            if self.display_frame is None:
                return {
                    'dist': float('inf'),
                    'ttc': float('inf'),
                    'objects': []
                }

            # Return last processed data
            # Note: This is a snapshot, might be slightly outdated
            return {
                'dist': min((obj['dist'] for obj in self.tracked_objects.values()), default=float('inf')),
                'ttc': float('inf'),  # Simplified for debug
                'objects': []  # Simplified for debug
            }