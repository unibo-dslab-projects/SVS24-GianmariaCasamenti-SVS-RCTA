---
layout: default
title: Implementation
nav_order: 4
---
# Solution implementation

## Perception Module

This module serves as the core system, tasked with understanding the 
environment through sensor data.

### Object Detection 
Object detector is YOLO wrapper with a filter on  specific target classes: 
person, bicycle, car, bus, and truck. 

The system utilizes the ```model.track()``` method with ```persist=True```,
which assigns and maintains a unique numerical ID for every detected 
object across frames, enabling the calculation of velocity and trajectory.

### Depth processing 
Distance estimation relies on the depth camera stream. 

CARLA outputs depth information encoded in a standard 3-channel RGB image.
The ```_decode_depth_to_meters()``` function converts this raw data into a metric
float matrix. 

It applies the standard decoding formula:
```normalized = (R + G * 256 + B * 256 * 256) / (256^3 - 1) * 1000```.

### Sensor fusion 
The ```_fuse_results``` function bridges the gap between the 2D 
detections and 3D depth map. 

For each bounding box identified by object detector:

- The coordinates are used to extract a corresponding Region of Interest 
(ROI) from the decoded depth map.

- To estimate the distance robustly, the system calculates the 
10th percentile of the depth values within that ROI.
This approach is significantly more reliable than using the mean or 
median, as it correctly identifies the closest point of the 
object (e.g., the bumper of a car) while filtering out background 
pixels that might be included in the bounding box.

### Tracking and TTC calculo 
To assess danger, the system must know how fast an object is approaching.
The ```_update_tracks_and_calc_ttc``` function manages this by storing the 
history of every object ID in dictionaries (e.g., tracked_objects_rear). 

By comparing the object's current distance and timestamp against its 
previous state, the system calculates the ```Relative velocity (delta_d / delta_t)```.

--- 

## Decision module 
This module processes the fused perception data to determine if an
alert is necessary.

### Evaluation Logic
The core logic resides in the evaluate method of the DecisionMaker class.
The system works with fused objects to find the detection with:
```
fused_objects = [
    {'id': 3, 'class': 'bicycle', 'confidence': 0.82, 'bbox': [120, 200, 280, 450], 'dist': 5.2, 'ttc_obj': 3.25},
    {'id': 5, 'class': 'car', 'confidence': 0.89, 'bbox': [130, 210, 290, 460], 'dist': 8.2, 'ttc_obj': 7.00}, 
    .
    .
]
```

- Danger Level (TTC): If an object's projected Time-to-Collision is 
lower than the TTC_THRESHOLD, the system triggers a "danger" alert. 
In this scenario, it prioritizes the object with the lowest TTC.

- Warning Level (Distance): If no TTC violation is detected, 
the system checks the physical distance. 
If an object is closer than the DIST_THRESHOLD, a "warning" alert is triggered.

### Output Format
The function returns a dangerous_objects_list, which is a list of dictionaries ready 
for MQTT transmission. 
The structure ensures the HMI receives all necessary context:

```
{
        'zone': 'left',
        'alert_level': 'danger',
        'class': 'bicycle',
        'distance': 5.2,
        'ttc': 3.25
}
```

--- 


## Communication & HMI (MQTT)

This module handles the communication of alerts from the main simulation to the end-user interface. 
This is achieved using an MQTT (Message Queuing Telemetry Transport) broker, 
which decouples the perception system from the display.

### MQTT Publisher
The MqttPublisher class, defined in ```mqtt_publisher.py```, manages the connection to 
the MQTT broker specified in the config.py file.

The primary function is ```publish_status(dangerous_objects_list)```.
This method receives the list of threats directly from the DecisionMaker module. 
It then constructs a JSON payload to be sent to the MQTT_TOPIC_ALERTS topic.

### HMI Display

The hmi_display.py script is a standalone Pygame application that functions as the 
MQTT client for the driver's interface. It runs as a completely separate process 
from the main CARLA simulation. 

It initializes its own MQTT client and subscribes to the same MQTT_TOPIC_ALERTS 
topic, listening for the JSON messages published by the MqttPublisher.

![image](../img/hmi.png)

Message Callback (_on_message) When a new message arrives from the broker,
the _on_message callback function is triggered. This function is responsible 
for parsing the incoming JSON payload drawing the specific zone with the 
right alert Danger (red) or Warning (yellow).