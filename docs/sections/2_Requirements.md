---
layout: default
title: Requirements
nav_order: 2
---

# Requirements

The requirements for the RCTA system are divided into two main categories: functional requirements that describe what 
the system must do, and non-functional requirements that specify how well the system must perform.

---
## Business requirements

1) Develop a functional Rear Cross Traffic Alert (RCTA) system to improve 
safety during reversing maneuvers. 

2) Provide a complete demonstration system using the CARLA simulator. 

## Functional requirements
1) Detect vehicles, pedestrians, and bicycles approaching from the side 
during reversing maneuvers.

3) Calculate the distance of detected objects from the vehicle

4) Track objects over time to calculate relative speed and TTC

5) Generate WARNING alerts when an object is within the distance threshold 

6) Generate DANGER level alerts when the TTC is below the critical threshold 

7) Monitor three detection zones: rear, left side, right side 

8) Publish alert statuses via MQTT protocol 

9) Deactivate the system when the vehicle is not reversing

## User requirements
1) Display graphical alerts on the HMI interface with colored sectors (green/yellow/red)

2) Display real-time information on object class, distance, and TTC 

3) Control the ego vehicle via keyboard during simulation 

## Not Functional requirements
1) The system must operate at 20 FPS in the CARLA simulator. 

2) Detection latency must be less than 100 ms. 

4) Cameras must have a resolution of 416x416 pixels with a FOV of 60°.

5) The system must be modular and easily extensible. 

6) The code must be documented and maintainable. 

## Implementation requirements
1) **Technology**: 
    - Python 3.7, CARLA, YOLOv8, MQTT to develop
    - Github, GitHub Pages to manage project
   
2) **Testing**: Implement different test scenarios with vehicles, pedestrians, 
and bicycles to coverage as much as possible cases

## Optional requirements
1) Support for asynchronous and synchronous simulation modes.

2) Debug mode to display windows with all tracked object.