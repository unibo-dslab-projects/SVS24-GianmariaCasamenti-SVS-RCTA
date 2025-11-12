---
layout: default
title: Requirements
nav_order: 2
---

# Chapter 2: Requirements

The requirements for the RCTA system are divided into two main categories: functional requirements that describe what 
the system must do, and non-functional requirements that specify how well the system must perform.

---

## 2.1 Functional Requirements

### Object Detection and Classification

**Description**: The system shall detect and classify objects in the rear and side detection zones.

**Target Classes**:
- Vehicles (cars, trucks, vans, motorcycles)
- Pedestrians
- Bicycles
- Other moving obstacles

**Acceptance Criteria**:
- Detection accuracy ≥ 90% for objects within 10 meters
- Classification confidence threshold ≥ 0.5
- Support for simultaneous multi-object detection

---

### Distance Measurement

**Description**: The system shall measure the distance from the ego vehicle to detected objects using depth sensor data.

**Specifications**:
- Range: 0.5 to 50 meters
- Accuracy: ±0.5 meters within 10 meters
- Update rate: Synchronized with camera frame rate (20 Hz)

**Method**:
- Fusion of RGB detection with depth map information
- Percentile-based depth calculation within bounding boxes

---

### Velocity Estimation and Time-to-Collision

**Description**: The system shall estimate the relative velocity of detected objects and calculate time-to-collision (TTC).

**Calculations**:
```
Relative Velocity = Δdistance / Δtime
TTC = current_distance / relative_velocity
```

**Thresholds**:
- Minimum velocity for TTC calculation: 0.5 m/s
- TTC warning threshold: 2.5 seconds
- Distance warning threshold: 3.0 meters

---

### Alert Generation

**Description**: The system shall generate graduated alerts based on threat assessment.

**Alert Levels**:

| Level | Condition | Action |
|-------|-----------|--------|
| **SAFE** | No threats detected | Green sector display |
| **WARNING** | Object distance < 3.0m<br>TTC > 2.5s | Yellow sector display<br>Object class and distance shown |
| **DANGER** | TTC < 2.5s | Red flashing sector display<br>Object class, distance, and TTC shown |

---

### Multi-Zone Monitoring

**Description**: The system shall monitor three distinct zones simultaneously.

**Zone Configuration**:
- **Left zone**: 190° to 250° (60° FOV)
- **Rear zone**: 250° to 290° (40° FOV)
- **Right zone**: 290° to 350° (60° FOV)

**Coverage**: Total 160° rear coverage with overlapping regions for continuity.

---

### MQTT Communication

**Description**: The system shall publish alerts and status information via MQTT protocol.

**Topics**:
- `rcta/alerts`: JSON-formatted alert messages

**Message Format**:
```json
{
  "alert": true/false,
  "objects": [
    {
      "zone": "left|rear|right",
      "alert_level": "warning|danger",
      "class": "person|car|bicycle",
      "distance": 2.5,
      "ttc": 1.8
    }
  ]
}
```

---

### Visual Feedback

**Description**: The system shall provide visual feedback to the driver through multiple interfaces.

**Components**:
1. **Camera views**: Display RGB images with bounding boxes and annotations
2. **Radar display**: Top-down view showing detection zones and threat levels
3. **Terminal output**: Text-based alert notifications

---

### Object Tracking

**Description**: The system shall maintain consistent tracking of detected objects across frames.

**Features**:
- Persistent object IDs using YOLO tracking
- Velocity smoothing using temporal information
- Stale track cleanup after 1.0 second of no detection

---

## 2.2 Non-Functional Requirements

### Real-Time Performance

**Description**: The system shall operate in real-time with minimal latency.

**Specifications**:
- Target frame rate: 20 FPS (50ms per frame)
- Maximum end-to-end latency: 100ms
- Processing time budget:
  - Image acquisition: 5ms
  - Object detection: 30ms (per camera)
  - Decision making: 5ms
  - Alert publishing: 5ms

**Implementation**:
- Asynchronous camera callbacks
- Parallel processing of multiple camera streams
- Optimized YOLO inference with GPU acceleration

---

### Robustness

**Description**: The system shall maintain reliable operation under various environmental conditions.

**Test Conditions**:
- **Weather**: Clear, rainy, foggy
- **Lighting**: Daylight, dusk, night
- **Traffic density**: Low, medium, high
- **Scenario complexity**: Simple (1-2 objects) to complex (5+ objects)

**Reliability Target**: ≥ 95% accuracy across all test conditions.

---

### Scalability

**Description**: The system architecture shall support easy extension and modification.

**Design Principles**:
- Modular component structure
- Configuration-based parameter tuning
- Clear separation of concerns:
  - Perception (object detection)
  - Decision making (risk assessment)
  - Actuation (alert generation)
  - Communication (MQTT publishing)

---

### Configurability

**Description**: System parameters shall be easily adjustable without code modification.

**Configurable Parameters** (in `config.py`):
- Camera positions and orientations
- Detection thresholds (TTC, distance)
- Sensor tick rates
- MQTT broker settings
- Target FPS and simulation mode
- Vehicle and scenario selection

---

### Maintainability

**Description**: The codebase shall be well-structured and documented for easy maintenance.

**Standards**:
- Clear module organization
- Descriptive function and variable names
- Inline comments for complex logic
- Print statements for debugging and monitoring
- Consistent error handling

---

### Resource Efficiency

**Description**: The system shall make efficient use of computational resources.

**Optimization Techniques**:
- YOLOv8 nano model for lightweight inference
- Numba JIT compilation for depth decoding
- Threading locks to prevent race conditions
- Efficient numpy operations for image processing

**Resource Targets**:
- GPU memory usage: < 2GB
- CPU usage: < 50% on quad-core processor
- RAM usage: < 4GB

---

### Integration with CARLA

**Description**: The system shall seamlessly integrate with the CARLA simulator.

**Requirements**:
- Compatible with CARLA 0.9.13+
- Support for both synchronous and asynchronous modes
- Proper actor cleanup on shutdown
- Spectator camera following ego vehicle

---

### User Experience

**Description**: The system shall provide clear and intuitive feedback to users.

**HMI Requirements**:
- Color-coded alert levels (green/yellow/red)
- Clear visual and textual information
- Non-intrusive warning displays
- Responsive graphical interface (60 FPS for HMI)
