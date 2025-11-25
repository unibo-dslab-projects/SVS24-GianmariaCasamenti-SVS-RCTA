---
layout: default
title: Architecture
nav_order: 3
---

# System Architecture

## Architecture overview

The RCTA system is designed with a modular architecture, which is orchestrated by the main simulation script (main.py). 
The data flows from the CARLA simulator's sensors through perception, decision-making, and finally to the Human-Machine 
Interface (HMI). This high-level architecture is depicted in the block diagram below.

```mermaid
graph LR
    subgraph CARLA["CARLA Simulator"]
        S1[Rear RGB + Depth]
        S2[Left RGB + Depth]
        S3[Right RGB + Depth]
    end

    subgraph REAR["Rear Pipeline"]
        P1[YOLO Detection] --> F1[Depth Fusion] --> T1[Tracking + TTC] --> D1[Decision Making]
    end

    subgraph LEFT["Left Pipeline"]
        P2[YOLO Detection] --> F2[Depth Fusion] --> T2[Tracking + TTC] --> D2[Decision Making]
    end

    subgraph RIGHT["Right Pipeline"]
        P3[YOLO Detection] --> F3[Depth Fusion] --> T3[Tracking + TTC] --> D3[Decision Making]
    end

    S1 --> P1
    S2 --> P2
    S3 --> P3

    D1 & D2 & D3 --> MQTT[(MQTT Broker)]
    MQTT --> HMI[HMI Display]
```

## Sensor configuration

The system's perception relies on a carefully configured set of sensors designed to provide full coverage of the rear 
cross-traffic zones. The setup is designed to mimic real-world RCTA systems, which need to monitor the blind spots 
obscured by adjacent parked vehicles.

<div class="carousel-container">
  <div class="carousel">
    <div class="carousel-slide active">
      <img src="../img/position1.png" alt="Camera mounting position">
    </div>
    <div class="carousel-slide">
      <img src="../img/position2.png" alt="Field of view coverage">
    </div>
    <div class="carousel-slide">
      <img src="../img/position3.png" alt="Detection zones">
    </div>
    <div class="carousel-slide">
      <img src="../img/position4.png" alt="Sensor configuration">
    </div>
    <div class="carousel-slide">
      <img src="../img/position5.png" alt="Coverage diagram">
    </div>
  </div>
  
  <button class="carousel-btn prev" onclick="moveSlide(-1)">&#10094;</button>
  <button class="carousel-btn next" onclick="moveSlide(1)">&#10095;</button>
  
  <div class="carousel-dots">
    <span class="dot active" onclick="currentSlide(0)"></span>
    <span class="dot" onclick="currentSlide(1)"></span>
    <span class="dot" onclick="currentSlide(2)"></span>
    <span class="dot" onclick="currentSlide(3)"></span>
    <span class="dot" onclick="currentSlide(4)"></span>
  </div>
</div>

<style>
.carousel-container {
  position: relative;
  max-width: 800px;
  margin: 2rem auto;
  background: #f5f5f5;
  border-radius: 8px;
  overflow: hidden;
}

.carousel {
  position: relative;
  width: 100%;
  height: 500px;
}

.carousel-slide {
  display: none;
  width: 100%;
  height: 100%;
  text-align: center;
  padding: 20px;
}

.carousel-slide.active {
  display: block;
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.carousel-slide img {
  max-width: 100%;
  max-height: 450px;
  object-fit: contain;
}

.carousel-caption {
  margin-top: 10px;
  font-style: italic;
  color: #555;
}

.carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: rgba(0, 0, 0, 0.5);
  color: white;
  border: none;
  font-size: 24px;
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.3s;
}

.carousel-btn:hover {
  background: rgba(0, 0, 0, 0.8);
}

.carousel-btn.prev {
  left: 10px;
}

.carousel-btn.next {
  right: 10px;
}

.carousel-dots {
  text-align: center;
  padding: 15px;
  background: #e0e0e0;
}

.dot {
  height: 12px;
  width: 12px;
  margin: 0 5px;
  background-color: #bbb;
  border-radius: 50%;
  display: inline-block;
  cursor: pointer;
  transition: background-color 0.3s;
}

.dot.active,
.dot:hover {
  background-color: #333;
}
</style>

<script>
let currentIndex = 0;

function showSlide(index) {
  const slides = document.querySelectorAll('.carousel-slide');
  const dots = document.querySelectorAll('.dot');
  
  if (index >= slides.length) currentIndex = 0;
  if (index < 0) currentIndex = slides.length - 1;
  
  slides.forEach(slide => slide.classList.remove('active'));
  dots.forEach(dot => dot.classList.remove('active'));
  
  slides[currentIndex].classList.add('active');
  dots[currentIndex].classList.add('active');
}

function moveSlide(direction) {
  currentIndex += direction;
  showSlide(currentIndex);
}

function currentSlide(index) {
  currentIndex = index;
  showSlide(currentIndex);
}

// Auto-advance ogni 5 secondi (opzionale)
setInterval(() => moveSlide(1), 5000);
</script>

### Sensor used

The primary sensors for this project are three RGBD cameras. 
This sensor type was chosen for its efficiency in fusing two critical data streams:
- RGB (Color) Stream: Provides the visual data necessary for the YOLOv8 object detection model to 
identify and classify relevant actors.

- Depth Stream: Provides a per-pixel distance map. This data is essential for accurately calculating the 
distance to a detected object, which is a crucial input for Time-to-Collision (TTC) calculations.

### Cameras positioning

The three cameras are placed at a common mounting point on the rear of the vehicle.
They are positioned to cover three distinct zones: Rear-Left, Rear-Center, and Rear-Right.

Their yaw angles are set to create a wide field of view, minimizing blind spots. 
The specific parameters, derived from config.py, are detailed in the following table.

| Camera    | Position (X, Y, Z)  | Resolution   | FPS   | FOV (deg)   | Rotation (Pitch, Yaw)   |
|:----------|:--------------------|:-------------|:------|:------------|:------------------------|
| **Rear**  | `(-2.0, 0.0, 0.9)`  | 416x416      | 20    | 60          | `(0, 180)`              |
| **Left**  | `(-2.0, 0.0, 0.9)`  | 416x416      | 20    | 60          | `(0, 240)`              |
| **Right** | `(-2.0, 0.0, 0.9)`  | 416x416      | 20    | 60          | `(0, 120)`              |

### Cameras view

The combined output of the three cameras provides the system with a comprehensive view of the area 
behind the vehicle. The image below shows the three camera feeds as processed by the 
perception module. 
These views are what the system uses to detect and track potential hazards.

![image](../img/view3.png)
