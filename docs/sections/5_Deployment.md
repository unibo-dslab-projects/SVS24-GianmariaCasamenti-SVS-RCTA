---
layout: default
title: Deployment
nav_order: 5
---

# Deployment

 Please refer to the Readme file in the GitHub repository, where you can find the requirements
 and all the instructions to setup the simulator and the virtual environment

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