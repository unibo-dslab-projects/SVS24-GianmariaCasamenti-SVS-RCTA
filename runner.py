"""
Unified RCTA System - Main Entry Point

Combines notebook-style simple callbacks with RCTA detection logic.
Each camera has its own YOLO model instance for tracking.
Uses asynchronous mode like the notebook.
"""

import carla
import time
import cv2
import pygame
import numpy as np
import config

from carla_bridge.carla_manager import CarlaManager
from carla_bridge.spawner import Spawner
from scenarios.parking_lot_scenario import (
    scenario_vehicle,
    scenario_bicycle,
    scenario_pedestrian_adult,
    scenario_pedestrian_child,
    setup_rcta_base_scenario
)
from rcta_system.object_detector import ObjectDetector
from rcta_system.decision_making import DecisionMaker
from hmi.mqtt_publisher import MqttPublisher
from controller.keyboard_controller import KeyboardController


# ============================================================================
# GLOBAL STATE (like notebook approach)
# ============================================================================

# Frame buffers for each camera zone
latest_frames = {
    'rear': {'rgb': None, 'depth': None},
    'left': {'rgb': None, 'depth': None},
    'right': {'rgb': None, 'depth': None}
}

# Detection results for each zone
detection_results = {
    'rear': {'objects': [], 'min_dist': float('inf'), 'min_ttc': float('inf')},
    'left': {'objects': [], 'min_dist': float('inf'), 'min_ttc': float('inf')},
    'right': {'objects': [], 'min_dist': float('inf'), 'min_ttc': float('inf')}
}

# Tracking state for each zone (like pipeline's tracked_objects)
tracked_objects = {
    'rear': {},
    'left': {},
    'right': {}
}

# Last processing time for each zone (for throttling detection)
last_analysis_time = {
    'rear': 0.0,
    'left': 0.0,
    'right': 0.0
}

# Detection interval (in seconds) - process frames every N seconds
ANALYSIS_INTERVAL = 0.1  # 10 Hz detection rate per zone


# ============================================================================
# YOLO DETECTORS AND DECISION MAKERS (one per zone)
# ============================================================================

detectors = {
    'rear': None,
    'left': None,
    'right': None
}

decision_makers = {
    'rear': None,
    'left': None,
    'right': None
}


# ============================================================================
# HELPER FUNCTIONS (from pipeline)
# ============================================================================

def decode_depth_to_meters(carla_img):
    """Convert CARLA depth image to meters"""
    array_uint8 = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
    array_uint8 = np.reshape(array_uint8, (carla_img.height, carla_img.width, 4))
    
    # Simple vectorized version (faster than numba for small images)
    R = array_uint8[:, :, 2].astype(np.float32)
    G = array_uint8[:, :, 1].astype(np.float32)
    B = array_uint8[:, :, 0].astype(np.float32)
    
    normalized = (R + G * 256.0 + B * 256.0 * 256.0) / (256.0 * 256.0 * 256.0 - 1.0)
    depth_meters = normalized * 1000.0
    
    return depth_meters


def to_numpy_rgb(carla_img):
    """Convert CARLA image to numpy RGB array"""
    array = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
    array = np.reshape(array, (carla_img.height, carla_img.width, 4))
    return array[:, :, :3]


def fuse_detections_with_depth(detections, depth_map):
    """Fuse YOLO detections with depth map to get distance"""
    h, w = depth_map.shape
    fused = []
    
    for det in detections:
        x1, y1, x2, y2 = map(int, det['bbox'])
        # Clipping
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


def update_tracking_and_calc_ttc(zone_name, current_objects, current_time):
    """Update object tracking and calculate TTC"""
    MIN_VELOCITY_FOR_TTC = 0.5  # m/s
    
    for obj in current_objects:
        track_id = obj['id']
        
        if track_id in tracked_objects[zone_name]:
            prev_state = tracked_objects[zone_name][track_id]
            delta_t = current_time - prev_state['time']
            delta_d = prev_state['dist'] - obj['dist']
            
            if delta_t > 0.0:
                rel_velocity = delta_d / delta_t
                if rel_velocity > MIN_VELOCITY_FOR_TTC:
                    ttc = obj['dist'] / rel_velocity
                    obj['ttc_obj'] = ttc
        
        tracked_objects[zone_name][track_id] = {
            'dist': obj['dist'],
            'time': current_time,
            'class': obj['class']
        }


def cleanup_stale_tracks(zone_name, current_time):
    """Remove objects that haven't been seen for too long"""
    STALE_THRESHOLD = 1.0  # seconds
    
    stale_ids = [
        track_id for track_id, state in tracked_objects[zone_name].items()
        if current_time - state['time'] > STALE_THRESHOLD
    ]
    for track_id in stale_ids:
        del tracked_objects[zone_name][track_id]


# ============================================================================
# CAMERA CALLBACKS (notebook style - simple and direct)
# ============================================================================

def create_rgb_callback(zone_name):
    """Factory function to create RGB callback for a specific zone"""
    def callback(image):
        latest_frames[zone_name]['rgb'] = image
    return callback


def create_depth_callback(zone_name):
    """Factory function to create depth callback for a specific zone"""
    def callback(image):
        latest_frames[zone_name]['depth'] = image
    return callback


# ============================================================================
# DETECTION PROCESSING (called periodically from main loop)
# ============================================================================

def process_zone_detection(zone_name, current_time):
    """
    Process detection for a single zone.
    Called periodically from main loop (not continuously like pipeline thread).
    """
    # Check if enough time has passed since last analysis
    if current_time - last_analysis_time[zone_name] < ANALYSIS_INTERVAL:
        return
    
    # Check if we have frames
    rgb_img = latest_frames[zone_name]['rgb']
    depth_img = latest_frames[zone_name]['depth']
    
    if rgb_img is None or depth_img is None:
        return
    
    # Update last analysis time
    last_analysis_time[zone_name] = current_time
    
    try:
        # Convert to numpy
        rgb_np = to_numpy_rgb(rgb_img)
        depth_meters = decode_depth_to_meters(depth_img)
        timestamp = depth_img.timestamp
        
        # YOLO detection
        detections = detectors[zone_name].detect(rgb_np)
        
        # Fuse with depth
        fused_objects = fuse_detections_with_depth(detections, depth_meters)
        
        # Cleanup stale tracks
        cleanup_stale_tracks(zone_name, timestamp)
        
        # Update tracking and calculate TTC
        update_tracking_and_calc_ttc(zone_name, fused_objects, timestamp)
        
        # Calculate minimums
        min_dist = min((obj['dist'] for obj in fused_objects), default=float('inf'))
        min_ttc = min((obj['ttc_obj'] for obj in fused_objects), default=float('inf'))
        
        # Update global detection results
        detection_results[zone_name] = {
            'objects': fused_objects,
            'min_dist': min_dist,
            'min_ttc': min_ttc
        }
        
    except Exception as e:
        print(f"DETECTION [{zone_name.upper()}] Error: {e}")


# ============================================================================
# DECISION MAKING AND MQTT (called periodically from main loop)
# ============================================================================

def evaluate_and_publish_alerts(mqtt_publisher):
    """
    Evaluate all zones and publish alerts if needed.
    Called from main loop.
    """
    all_dangerous_objects = []
    
    for zone_name in ['rear', 'left', 'right']:
        perception_data = {
            'dist': detection_results[zone_name]['min_dist'],
            'ttc': detection_results[zone_name]['min_ttc'],
            'objects': detection_results[zone_name]['objects']
        }
        
        dangerous_objects = decision_makers[zone_name].evaluate(perception_data)
        if dangerous_objects:
            all_dangerous_objects.extend(dangerous_objects)
    
    # Publish to MQTT
    if all_dangerous_objects:
        print(all_dangerous_objects)
        mqtt_publisher.publish_status(all_dangerous_objects)


# ============================================================================
# CAMERA SETUP
# ============================================================================

def setup_cameras(world, vehicle, actor_list):
    """
    Setup 6 cameras (3 RGB + 3 Depth) with callbacks.
    Similar to notebook's camera setup.
    """
    blueprint_library = world.get_blueprint_library()
    
    # RGB camera blueprint
    rgb_bp = blueprint_library.find('sensor.camera.rgb')
    rgb_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
    rgb_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
    rgb_bp.set_attribute('fov', config.CAMERA_FOV)
    rgb_bp.set_attribute('sensor_tick', '0.05')  # 20 Hz like notebook
    
    # Depth camera blueprint
    depth_bp = blueprint_library.find('sensor.camera.depth')
    depth_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
    depth_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
    depth_bp.set_attribute('fov', config.CAMERA_FOV)
    depth_bp.set_attribute('sensor_tick', '0.05')  # 20 Hz
    
    cameras = {}
    
    # Setup each zone
    zones = {
        'rear': config.REAR_CAMERA_TRANSFORM,
        'left': config.LEFT_CAMERA_TRANSFORM,
        'right': config.RIGHT_CAMERA_TRANSFORM
    }
    
    for zone_name, transform in zones.items():
        print(f"CAMERA_SETUP [Spawning {zone_name.upper()} cameras]")
        
        # Spawn RGB camera
        rgb_cam = world.spawn_actor(rgb_bp, transform, attach_to=vehicle)
        rgb_cam.listen(create_rgb_callback(zone_name))
        
        # Spawn depth camera
        depth_cam = world.spawn_actor(depth_bp, transform, attach_to=vehicle)
        depth_cam.listen(create_depth_callback(zone_name))
        
        cameras[zone_name] = {'rgb': rgb_cam, 'depth': depth_cam}
        actor_list.extend([rgb_cam, depth_cam])
        
        print(f"CAMERA_SETUP [{zone_name.upper()} cameras spawned and callbacks registered]")
    
    return cameras


# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((200, 100), pygame.NOFRAME)
    pygame.display.set_caption('CARLA RCTA Control')
    clock = pygame.time.Clock()
    
    try:
        with CarlaManager() as manager:
            # Setup scenario
            print("MAIN [Initializing scenario]")
            spawner = Spawner(manager.world, manager.actor_list)
            ego_vehicle = setup_rcta_base_scenario(manager.world, spawner, True, False)
            if not ego_vehicle:
                print("MAIN [Failed to spawn ego vehicle]")
                return
            
            # Initialize MQTT
            print("MAIN [Initializing MQTT Publisher]")
            mqtt_publisher = MqttPublisher()
            mqtt_publisher.connect()
            
            # Initialize detectors and decision makers (one per zone)
            print("MAIN [Initializing YOLO detectors and decision makers]")
            for zone_name in ['rear', 'left', 'right']:
                detectors[zone_name] = ObjectDetector()
                decision_makers[zone_name] = DecisionMaker(zone_name)
            
            # Setup cameras with callbacks
            print("MAIN [Setting up cameras]")
            cameras = setup_cameras(manager.world, ego_vehicle, manager.actor_list)
            
            # Wait for sensors to initialize
            print("MAIN [Waiting for sensors to warm up...]")
            time.sleep(2.0)
            
            # Initialize controller and spectator
            print("MAIN [Initializing controller and spectator]")
            controller = KeyboardController()
            spectator = manager.world.get_spectator()
            
            # Spawn scenario
            print("MAIN [Spawning scenario]")
            # scenario_vehicle(spawner)
            scenario_bicycle(spawner)
            # scenario_pedestrian_adult(spawner)
            # scenario_pedestrian_child(spawner)
            
            print("MAIN [Starting main loop]")
            time.sleep(1.0)
            
            running = True
            frame_count = 0
            start_time = time.time()
            last_detection_time = 0.0
            last_alert_time = 0.0
            
            # Detection and alert intervals
            DETECTION_RATE = 0.1  # Process detections every 100ms
            ALERT_RATE = 0.1  # Evaluate and publish alerts every 100ms
            
            while running:
                try:
                    current_time = time.time()
                    
                    # NO world.tick() - asynchronous mode!
                    
                    # Update spectator position
                    ego_transform = ego_vehicle.get_transform()
                    spectator_location = (
                        ego_transform.location +
                        ego_transform.get_forward_vector() * (-10) +
                        carla.Location(z=5)
                    )
                    spectator_rotation = carla.Rotation(
                        pitch=-30,
                        yaw=ego_transform.rotation.yaw
                    )
                    spectator.set_transform(
                        carla.Transform(spectator_location, spectator_rotation)
                    )
                    
                    # Handle pygame events
                    pygame.event.pump()
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                    
                    # Apply vehicle control
                    keys = pygame.key.get_pressed()
                    control = controller.parse_input(keys)
                    ego_vehicle.apply_control(control)
                    
                    # Process detections periodically (not every frame!)
                    if current_time - last_detection_time >= DETECTION_RATE:
                        last_detection_time = current_time
                        for zone_name in ['rear', 'left', 'right']:
                            process_zone_detection(zone_name, current_time)
                    
                    # Evaluate and publish alerts periodically
                    if current_time - last_alert_time >= ALERT_RATE:
                        last_alert_time = current_time
                        evaluate_and_publish_alerts(mqtt_publisher)
                    
                    # FPS counter
                    frame_count += 1
                    if frame_count % 100 == 0:
                        elapsed = current_time - start_time
                        fps = frame_count / elapsed
                        print(f"MAIN [FPS: {fps:.1f}]")
                    
                    # Maintain framerate
                    pygame.display.flip()
                    clock.tick(40)  # 40 FPS main loop
                    
                except RuntimeError as e:
                    if "rpc" in str(e).lower():
                        print(f"MAIN [Warning: RPC error, continuing...]")
                        time.sleep(0.01)
                        continue
                    else:
                        raise
                        
                except Exception as e:
                    print(f"MAIN [Loop error: {e}]")
                    import traceback
                    traceback.print_exc()
                    time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\nMAIN [Script interrupted from keyboard]")
    except Exception as e:
        print(f"\nMAIN [Exception: {e}]")
        import traceback
        traceback.print_exc()
    finally:
        print("MAIN [Starting cleanup...]")
        
        # Disconnect MQTT
        try:
            if 'mqtt_publisher' in locals():
                mqtt_publisher.disconnect()
        except Exception as e:
            print(f"MAIN [Error disconnecting MQTT: {e}]")
        
        # Cleanup pygame
        try:
            pygame.quit()
            cv2.destroyAllWindows()
        except Exception as e:
            print(f"MAIN [Error in pygame cleanup: {e}]")
        
        print("MAIN [Cleanup completed]")


if __name__ == '__main__':
    main()