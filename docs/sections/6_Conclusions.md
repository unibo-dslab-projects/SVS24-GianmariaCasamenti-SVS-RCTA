---
layout: default
title: Conclusions
nav_order: 8
---

# Conclusions

## Strengths and Weaknesses

The developed RCTA prototype demonstrates a solid foundation for ADAS development in simulated environments,
characterized by several **key strengths**:

- Modular Architecture: The decoupling of the perception system from the visualization via MQTT 
is a significant design advantage. 

- Advanced Sensor Fusion: the use of RGBD  sensors provides a deterministic measurement of the environment. 

- Intuitive HMI: The sector-based user interface provides immediate data.


However, the current implementation is subject to specific **limitations**:

- Tracking Volatility: If an object is momentarily occluded by a blocking vehicle and re-emerges with a new ID,
the tracking history is reset.

- Passive Operation: The system is currently designed as a "alert" system only.

## Future upgrade

To bridge the gap between this prototype and a production-ready safety system, the following enhancements are proposed:

- System Watchdog: A system that checks camera status. If a camera is damaged sends a message to HMI display.

- Automatic Emergency Braking: Extending the system from passive monitoring to active intervention. 