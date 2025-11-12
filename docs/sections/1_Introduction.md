---
layout: default
title: Introduction
nav_order: 1
---

# Chapter 1: Introduction

## 1.1 RCTA - Rear Cross Traffic Alert


---

## 1.2 Motivations

The development of this RCTA system was driven by several factors:

### 1.2.1 Real-World Safety Concerns

Reversing accidents represent a significant portion of vehicle collisions, particularly in parking lots and 
residential areas. According to traffic safety statistics:

- **Backing accidents** account for approximately 25% of all vehicle collisions in parking lots
- **Pedestrian injuries** from reversing vehicles are particularly common, with children and elderly individuals at highest risk
- **Limited visibility** during reversing maneuvers creates blind spots that traditional mirrors cannot fully cover

### 1.2.2 Technological Advancement

Modern vehicles increasingly incorporate ADAS features to compensate for human limitations:

- **Sensor technology** has become more affordable and reliable
- **Computer vision algorithms** have achieved real-time performance
- **Legislative requirements** in many regions now mandate reversing cameras and warning systems

---

## 1.3 System Scope

This RCTA implementation focuses on:

1. **Detection zone coverage**: Monitoring a 180-degree area behind the vehicle, with extended coverage to the sides
2. **Multi-object tracking**: Simultaneously tracking multiple potential hazards
3. **Distance and velocity estimation**: Calculating time-to-collision for risk assessment
4. **Alert generation**: Providing graduated warnings based on threat level
5. **Simulation validation**: Testing in diverse CARLA scenarios

---