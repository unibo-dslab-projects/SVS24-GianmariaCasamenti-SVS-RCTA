# rcta_callbacks.py
"""
RCTA Callbacks for unified zone processing.
Each callback receives both RGB and Depth images synchronously.
"""

import numpy as np
import time
from rcta_system.perception import Perception
from rcta_system.decision_making import DecisionMaker
from hmi.mqtt_publisher import MQTTPublisher

# ============================================
# GLOBAL INSTANCES (shared)
# ============================================

# Initialize perception system (one instance for all zones)
perception = Perception()

# Initialize decision makers (one per zone)
decision_maker_rear = DecisionMaker("rear")
decision_maker_left = DecisionMaker("left")
decision_maker_right = DecisionMaker("right")

# Initialize MQTT publisher
mqtt_publisher = MQTTPublisher()

print("RCTA_CALLBACKS [Initialized: Perception, DecisionMakers, MQTT Publisher]")

# ============================================
# GLOBAL STATE (shared between callbacks and main loop)
# ============================================

# Zone status dictionaries
rear_zone_status = {
    "vehicles_detected": 0,
    "closest_distance": None,
    "threat_level": "none",
    "alert_active": False,
    "time_to_collision": None,
    "last_update": 0.0
}

left_zone_status = {
    "vehicles_detected": 0,
    "closest_distance": None,
    "threat_level": "none",
    "alert_active": False,
    "time_to_collision": None,
    "last_update": 0.0
}

right_zone_status = {
    "vehicles_detected": 0,
    "closest_distance": None,
    "threat_level": "none",
    "alert_active": False,
    "time_to_collision": None,
    "last_update": 0.0
}

# System state
rcta_system_active = False
vehicle_in_reverse = False


# ============================================
# UNIFIED ZONE CALLBACKS
# ============================================

def rear_zone_callback(rgb_image, depth_image):
    """
    Unified callback for REAR zone.
    Processes RGB + Depth together for:
    - Vehicle detection (YOLO on RGB)
    - Distance measurement (Depth analysis)
    - Threat evaluation
    - MQTT notification
    - Global state update

    Args:
        rgb_image: CARLA RGB camera image
        depth_image: CARLA Depth camera image
    """
    global rear_zone_status

    # FASE 1: Preprocessing - Convert CARLA images to numpy
    rgb_np = perception.to_numpy_rgb(rgb_image)
    depth_meters = perception.to_depth_meters(depth_image)
    timestamp = depth_image.timestamp

    # FASE 2: Object Detection (YOLO on RGB)
    detections = perception.detector_rear.detect(rgb_np)

    # FASE 3: Distance Measurement (Fuse detections with depth)
    fused_objects = perception.fuse_results(detections, depth_meters)

    # Cleanup stale tracks periodically
    if timestamp - perception.last_cleanup_time_rear > perception.STALE_TRACK_THRESHOLD_SEC:
        perception.cleanup_stale_tracks(timestamp, perception.tracked_objects_rear)
        perception.last_cleanup_time_rear = timestamp

    # Update tracking and calculate TTC
    perception.update_tracks_and_calc_ttc(fused_objects, timestamp, perception.tracked_objects_rear)

    # Extract zone status (min distance, min TTC, objects list)
    perception_data = perception.extract_zone_status(fused_objects)

    # FASE 4: Threat Evaluation
    dangerous_objects = decision_maker_rear.evaluate(perception_data)

    # FASE 5: MQTT Notification
    if dangerous_objects:
        mqtt_publisher.publish_alerts(dangerous_objects)
        print(f"REAR_CALLBACK [ALERT] {dangerous_objects}")

    # FASE 6: Update Global State
    rear_zone_status["vehicles_detected"] = len(fused_objects)
    rear_zone_status["closest_distance"] = perception_data['dist']
    rear_zone_status["time_to_collision"] = perception_data['ttc']
    rear_zone_status["alert_active"] = len(dangerous_objects) > 0
    rear_zone_status["threat_level"] = dangerous_objects[0]["alert_level"] if dangerous_objects else "none"
    rear_zone_status["last_update"] = timestamp


def left_zone_callback(rgb_image, depth_image):
    """
    Unified callback for LEFT zone.
    Processes RGB + Depth together for:
    - Vehicle detection (YOLO on RGB)
    - Distance measurement (Depth analysis)
    - Threat evaluation
    - MQTT notification
    - Global state update

    Args:
        rgb_image: CARLA RGB camera image
        depth_image: CARLA Depth camera image
    """
    global left_zone_status

    # FASE 1: Preprocessing - Convert CARLA images to numpy
    rgb_np = perception.to_numpy_rgb(rgb_image)
    depth_meters = perception.to_depth_meters(depth_image)
    timestamp = depth_image.timestamp

    # FASE 2: Object Detection (YOLO on RGB)
    detections = perception.detector_left.detect(rgb_np)

    # FASE 3: Distance Measurement (Fuse detections with depth)
    fused_objects = perception.fuse_results(detections, depth_meters)

    # Cleanup stale tracks periodically
    if timestamp - perception.last_cleanup_time_left > perception.STALE_TRACK_THRESHOLD_SEC:
        perception.cleanup_stale_tracks(timestamp, perception.tracked_objects_left)
        perception.last_cleanup_time_left = timestamp

    # Update tracking and calculate TTC
    perception.update_tracks_and_calc_ttc(fused_objects, timestamp, perception.tracked_objects_left)

    # Extract zone status (min distance, min TTC, objects list)
    perception_data = perception.extract_zone_status(fused_objects)

    # FASE 4: Threat Evaluation
    dangerous_objects = decision_maker_left.evaluate(perception_data)

    # FASE 5: MQTT Notification
    if dangerous_objects:
        mqtt_publisher.publish_alerts(dangerous_objects)
        print(f"LEFT_CALLBACK [ALERT] {dangerous_objects}")

    # FASE 6: Update Global State
    left_zone_status["vehicles_detected"] = len(fused_objects)
    left_zone_status["closest_distance"] = perception_data['dist']
    left_zone_status["time_to_collision"] = perception_data['ttc']
    left_zone_status["alert_active"] = len(dangerous_objects) > 0
    left_zone_status["threat_level"] = dangerous_objects[0]["alert_level"] if dangerous_objects else "none"
    left_zone_status["last_update"] = timestamp


def right_zone_callback(rgb_image, depth_image):
    """
    Unified callback for RIGHT zone.
    Processes RGB + Depth together for:
    - Vehicle detection (YOLO on RGB)
    - Distance measurement (Depth analysis)
    - Threat evaluation
    - MQTT notification
    - Global state update

    Args:
        rgb_image: CARLA RGB camera image
        depth_image: CARLA Depth camera image
    """
    global right_zone_status

    # FASE 1: Preprocessing - Convert CARLA images to numpy
    rgb_np = perception.to_numpy_rgb(rgb_image)
    depth_meters = perception.to_depth_meters(depth_image)
    timestamp = depth_image.timestamp

    # FASE 2: Object Detection (YOLO on RGB)
    detections = perception.detector_right.detect(rgb_np)

    # FASE 3: Distance Measurement (Fuse detections with depth)
    fused_objects = perception.fuse_results(detections, depth_meters)

    # Cleanup stale tracks periodically
    if timestamp - perception.last_cleanup_time_right > perception.STALE_TRACK_THRESHOLD_SEC:
        perception.cleanup_stale_tracks(timestamp, perception.tracked_objects_right)
        perception.last_cleanup_time_right = timestamp

    # Update tracking and calculate TTC
    perception.update_tracks_and_calc_ttc(fused_objects, timestamp, perception.tracked_objects_right)

    # Extract zone status (min distance, min TTC, objects list)
    perception_data = perception.extract_zone_status(fused_objects)

    # FASE 4: Threat Evaluation
    dangerous_objects = decision_maker_right.evaluate(perception_data)

    # FASE 5: MQTT Notification
    if dangerous_objects:
        mqtt_publisher.publish_alerts(dangerous_objects)
        print(f"RIGHT_CALLBACK [ALERT] {dangerous_objects}")

    # FASE 6: Update Global State
    right_zone_status["vehicles_detected"] = len(fused_objects)
    right_zone_status["closest_distance"] = perception_data['dist']
    right_zone_status["time_to_collision"] = perception_data['ttc']
    right_zone_status["alert_active"] = len(dangerous_objects) > 0
    right_zone_status["threat_level"] = dangerous_objects[0]["alert_level"] if dangerous_objects else "none"
    right_zone_status["last_update"] = timestamp


# ============================================
# SYNCHRONIZATION HELPER
# ============================================

# Temporary storage for synchronizing RGB + Depth
rear_rgb_data = None
rear_depth_data = None

left_rgb_data = None
left_depth_data = None

right_rgb_data = None
right_depth_data = None


def sync_and_callback(zone, sensor_type, image):
    """
    Synchronization helper that collects RGB and Depth images,
    then calls the unified zone callback when both are available.

    This is needed because CARLA sends RGB and Depth separately,
    but we want to process them together.

    Args:
        zone: "rear", "left", or "right"
        sensor_type: "rgb" or "depth"
        image: CARLA sensor image data
    """
    global rear_rgb_data, rear_depth_data
    global left_rgb_data, left_depth_data
    global right_rgb_data, right_depth_data

    if zone == "rear":
        if sensor_type == "rgb":
            rear_rgb_data = image
            # If depth is already available, call callback
            if rear_depth_data is not None:
                rear_zone_callback(rear_rgb_data, rear_depth_data)
                # Reset after processing
                rear_rgb_data = None
                rear_depth_data = None

        elif sensor_type == "depth":
            rear_depth_data = image
            # If RGB is already available, call callback
            if rear_rgb_data is not None:
                rear_zone_callback(rear_rgb_data, rear_depth_data)
                # Reset after processing
                rear_rgb_data = None
                rear_depth_data = None

    elif zone == "left":
        if sensor_type == "rgb":
            left_rgb_data = image
            if left_depth_data is not None:
                left_zone_callback(left_rgb_data, left_depth_data)
                left_rgb_data = None
                left_depth_data = None

        elif sensor_type == "depth":
            left_depth_data = image
            if left_rgb_data is not None:
                left_zone_callback(left_rgb_data, left_depth_data)
                left_rgb_data = None
                left_depth_data = None

    elif zone == "right":
        if sensor_type == "rgb":
            right_rgb_data = image
            if right_depth_data is not None:
                right_zone_callback(right_rgb_data, right_depth_data)
                right_rgb_data = None
                right_depth_data = None

        elif sensor_type == "depth":
            right_depth_data = image
            if right_rgb_data is not None:
                right_zone_callback(right_rgb_data, right_depth_data)
                right_rgb_data = None
                right_depth_data = None

    else:
        print(f"SYNC_ERROR [Unknown zone: {zone}]")