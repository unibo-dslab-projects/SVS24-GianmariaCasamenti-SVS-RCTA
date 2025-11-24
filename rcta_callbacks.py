# rcta_callbacks.py
"""
RCTA Callbacks for unified zone processing.
Each callback receives both RGB and Depth images synchronously.
"""

import numpy as np
import time

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

# MQTT flags (prevent spam)
rear_alert_sent = False
left_alert_sent = False
right_alert_sent = False

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
    global rear_zone_status, rear_alert_sent

    print("REAR_CALLBACK [Called]")

    # TODO: FASE 1 - Preprocessing

    # TODO: FASE 2 - Object Detection (YOLO on RGB)

    # TODO: FASE 3 - Distance Measurement (Depth analysis)


    # TODO: FASE 4 - Threat Evaluation

    # TODO: FASE 5 - MQTT Notification

    # TODO: FASE 6 - Update Global State

    print(f"REAR_CALLBACK [Status: {rear_zone_status}]")


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
    global left_zone_status, left_alert_sent

    print("LEFT_CALLBACK [Called]")

    # TODO: FASE 1 - Preprocessing

    # TODO: FASE 2 - Object Detection (YOLO on RGB)

    # TODO: FASE 3 - Distance Measurement (Depth analysis)

    # TODO: FASE 4 - Threat Evaluation

    # TODO: FASE 5 - MQTT Notification

    # TODO: FASE 6 - Update Global State

    print(f"LEFT_CALLBACK [Status: {left_zone_status}]")


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
    global right_zone_status, right_alert_sent

    print("RIGHT_CALLBACK [Called]")

    # TODO: FASE 1 - Preprocessing

    # TODO: FASE 2 - Object Detection (YOLO on RGB)

    # TODO: FASE 3 - Distance Measurement (Depth analysis)

    # TODO: FASE 4 - Threat Evaluation

    # TODO: FASE 5 - MQTT Notification

    # TODO: FASE 6 - Update Global State

    print(f"RIGHT_CALLBACK [Status: {right_zone_status}]")


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
