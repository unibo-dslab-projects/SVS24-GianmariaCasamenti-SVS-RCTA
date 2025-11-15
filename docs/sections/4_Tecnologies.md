---
layout: default
title: Technologies
nav_order: 5
---

# Technologies used


## YOLOv8n (Ultralytics)
[YOLOv8n Docs](https://docs.ultralytics.com/it/models/yolov8/)

For the object detection task, we selected the YOLOv8n (nano) model from Ultralytics. 
This choice was driven by the system's strict real-time requirement. The 'nano' version provides an excellent balance
between high detection accuracy and very fast inference speed, which is critical 
for calculating an up-to-date Time-to-Collision (TTC).

The model is used with its weights pre-trained on the COCO (Common Objects in Context) dataset. 
This is highly advantageous as COCO already includes all of our system's target classes, eliminating the need for 
custom training and allowing for robust detection out-of-the-box.

The ObjectDetector class in our code (object_detector.py) loads this model and 
filters detections for these specific target classes.

## Paho-MQTT
[Paho-MQTT Docs](https://pypi.org/project/paho-mqtt/)

The Paho-MQTT library is used as the communication backbone of the system.
We chose MQTT to create a decoupled architecture, cleanly separating the core RCTA system (running in main.py) 
from the Human-Machine Interface (HMI, running in hmi_display.py).

- This publish/subscribe pattern is highly flexible:

- The MqttPublisher class (mqtt_publisher.py) in the main simulation publishes JSON-formatted status messages
- (containing alerts or an "all clear" signal) to the rcta/alerts topic.

- The hmi_display.py script runs as a completely separate process, subscribing to that topic to receive
and visualize the alerts. This allows the HMI to run on a different machine (like a tablet or secondary 
monitor) with no code changes.

## Mosquitto Eclipse - Docker
[Mosquitto Eclipse Docs](https://mosquitto.org/)

While Paho-MQTT provides the client-side libraries, Eclipse Mosquitto serves as the central MQTT broker (the server).
It is a lightweight, open-source, and reliable broker that implements the MQTT protocol.

All communication between the CARLA simulation and the HMI display is routed through the Mosquitto broker.
For this project, it is deployed as a Docker container, which simplifies setup and ensures a consistent,
isolated environment for the messaging service.

