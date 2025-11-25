import numpy as np
import time
from rcta_system.perception import Perception
from rcta_system.decision_making import DecisionMaker
from hmi.mqtt_publisher import MQTTPublisher

# Initialize perception system (one instance for all zones)
perception = Perception()

# Initialize decision makers (one per zone)
decision_maker_rear = DecisionMaker("rear")
decision_maker_left = DecisionMaker("left")
decision_maker_right = DecisionMaker("right")

# Initialize MQTT publisher
mqtt_publisher = MQTTPublisher()

print("RCTA_CALLBACKS [Initialized: Perception, DecisionMakers, MQTT Publisher]")

# System state
rcta_system_active = False


def rear_zone_callback(rgb_image, depth_image):
    if not rcta_system_active:
        return

    rgb_np = perception.to_numpy_rgb(rgb_image)
    depth_meters = perception.to_depth_meters(depth_image)
    timestamp = depth_image.timestamp
    detections = perception.detector_rear.detect(rgb_np)
    """
    detections = [
    {
        'id': 3,
        'class': 'bicycle',
        'confidence': 0.82,
        'bbox': [120, 200, 280, 450]
    }
    ]
    """
    fused_objects = perception.fuse_results(detections, depth_meters)
    """
    fused_objects = [
    {
        'id': 3,
        'class': 'bicycle',
        'confidence': 0.82,
        'bbox': [120, 200, 280, 450],
        'dist': 5.2,         
        'ttc_obj': float('inf')
    }
    ]
    """
    if timestamp - perception.last_cleanup_time_rear > perception.STALE_TRACK_THRESHOLD_SEC:
        perception.cleanup_stale_tracks(timestamp, perception.tracked_objects_rear)
        perception.last_cleanup_time_rear = timestamp

    perception.update_tracks_and_calc_ttc(fused_objects, timestamp, perception.tracked_objects_rear)
    """
    fused_objects = [
    {
        'id': 3,
        'class': 'bicycle',
        'confidence': 0.82,
        'bbox': [120, 200, 280, 450],
        'dist': 5.2,
        'ttc_obj': 3.25
    }
    ]
    """
    dangerous_objects = decision_maker_rear.evaluate(fused_objects)
    """
    dangerous_objects = [
    {
        'zone': 'left',
        'alert_level': 'danger',
        'class': 'bicycle',
        'distance': 5.2,
        'ttc': 3.25
    }
    ]
    """
    if dangerous_objects:
        mqtt_publisher.publish_alerts(dangerous_objects)
        print(f"REAR_CALLBACK [ALERT] {dangerous_objects}")


def left_zone_callback(rgb_image, depth_image):
    if not rcta_system_active:
        return

    rgb_np = perception.to_numpy_rgb(rgb_image)
    depth_meters = perception.to_depth_meters(depth_image)
    timestamp = depth_image.timestamp

    detections = perception.detector_left.detect(rgb_np)

    fused_objects = perception.fuse_results(detections, depth_meters)

    if timestamp - perception.last_cleanup_time_left > perception.STALE_TRACK_THRESHOLD_SEC:
        perception.cleanup_stale_tracks(timestamp, perception.tracked_objects_left)
        perception.last_cleanup_time_left = timestamp

    perception.update_tracks_and_calc_ttc(fused_objects, timestamp, perception.tracked_objects_left)
    dangerous_objects = decision_maker_left.evaluate(fused_objects)

    if dangerous_objects:
        mqtt_publisher.publish_alerts(dangerous_objects)
        print(f"LEFT_CALLBACK [ALERT] {dangerous_objects}")


def right_zone_callback(rgb_image, depth_image):
    if not rcta_system_active:
        return

    rgb_np = perception.to_numpy_rgb(rgb_image)
    depth_meters = perception.to_depth_meters(depth_image)
    timestamp = depth_image.timestamp

    detections = perception.detector_right.detect(rgb_np)

    fused_objects = perception.fuse_results(detections, depth_meters)

    if timestamp - perception.last_cleanup_time_right > perception.STALE_TRACK_THRESHOLD_SEC:
        perception.cleanup_stale_tracks(timestamp, perception.tracked_objects_right)
        perception.last_cleanup_time_right = timestamp

    perception.update_tracks_and_calc_ttc(fused_objects, timestamp, perception.tracked_objects_right)
    dangerous_objects = decision_maker_right.evaluate(fused_objects)

    # MQTT Notification
    if dangerous_objects:
        mqtt_publisher.publish_alerts(dangerous_objects)
        print(f"RIGHT_CALLBACK [ALERT] {dangerous_objects}")


def update_vehicle_state(vehicle):
    global rcta_system_active
    control = vehicle.get_control()
    rcta_system_active = control.reverse


# Temporary storage for synchronizing RGB + Depth
rear_rgb_data = None
rear_depth_data = None

left_rgb_data = None
left_depth_data = None

right_rgb_data = None
right_depth_data = None


def sync_and_callback(zone, sensor_type, image):
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
