# Smart Vehicular Systems Project: Rear Cross Traffic Alert (RCTA)

[![Python Version](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/)
[![CARLA](https://img.shields.io/badge/CARLA-0.9.15-orange.svg)](https://carla.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00FFFF.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/license-Academic-green.svg)]()
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen.svg)](https://giammacode.github.io/SVS-RCTA/)

📖 **[Full Documentation](https://giammacode.github.io/SVS-RCTA/)**

---

## Overview
This project implements a **Rear Cross Traffic Alert (RCTA)** system that detects vehicles and pedestrians approaching from the sides while a vehicle is reversing. The system provides real-time visual and audio alerts to enhance driver safety during reversing maneuvers.

The RCTA system uses:
- **CARLA Simulator** for realistic vehicle and environment simulation
- **YOLOv8** for object detection (vehicles, pedestrians, bicycles)
- **RGB-D cameras** for perception (rear, left, and right coverage)
- **MQTT protocol** for alert communication
- **Time-to-Collision (TTC)** and distance-based threat assessment

---

## Requirements

### Software Dependencies
- **Python**: 3.7 (recommended for CARLA compatibility)
- **CARLA Simulator**: 0.9.15
- **Conda** (recommended for environment management)
- **Docker** (for MQTT broker)

### Python Libraries
Key dependencies include:
- `carla` (CARLA Python API)
- `ultralytics` (YOLOv8)
- `opencv-python` (cv2)
- `pygame`
- `paho-mqtt`
- `numpy`
- `numba`

See `requirements.txt` for the complete list.

---

## Installation

### 1. Create and Activate Conda Environment
```bash
conda create -n rcta python=3.7
conda activate rcta
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up MQTT Broker (Using Docker)
The system uses Eclipse Mosquitto as the MQTT broker for communication between components.

**First-time setup:**
```bash
docker run -d -p 1883:1883 -p 9001:9001 --name mosquitto eclipse-mosquitto mosquitto -c /mosquitto-no-auth.conf
```

**Subsequent runs:**
```bash
docker start mosquitto
```

**To stop the broker:**
```bash
docker stop mosquitto
```

### 4. Install CARLA
Download and install CARLA simulator from the [official website](https://carla.org/).

Ensure the CARLA Python API is accessible:
```bash
export PYTHONPATH=$PYTHONPATH:/path/to/carla/PythonAPI/carla
```
--- 

## Usage

### 1. Start CARLA Simulator
```bash
cd /path/to/CARLA_Simulator
./CarlaUE4.sh
```

Or on Windows:
```cmd
CarlaUE4.exe
```

### 2. Start MQTT Broker
```bash
docker start mosquitto
```

### 3. Run the Main RCTA System
```bash
python main.py
```

**Controls:**
- **WASD Keys**: Control vehicle movement

### 4. Launch HMI Displays
**Graphical HMI:**
```bash
python hmi/hmi_display.py
```

---

## License

This project was developed as part of the Smart Vehicular Systems course.

---

## Acknowledgments

- **CARLA Team** for the open-source autonomous driving simulator
- **Ultralytics** for the YOLOv8 framework
- **Eclipse Mosquitto** for the MQTT broker

---