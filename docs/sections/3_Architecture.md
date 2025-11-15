---
layout: default
title: Architecture
nav_order: 3
---

# System Architecture

## Panoramica dell'Architettura

Cosa scrivere: Inizia con un diagramma a blocchi di alto livello.

(CARLA Simulator) -> (Sensori: 3x RGBD Cam) -> (Perception Module) -> (Decision Making Module) -> (MQTT Broker) -> (HMI Display)

## Sensor configuration

Cosa scrivere: Spiega la configurazione dei sensori (simile alle sezioni 3.1-3.3 del PDF).

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

Sensori Utilizzati: Spiega che hai usato 3 telecamere RGBD (RGB + Depth). Motiva la scelta: RGB per 
il rilevamento (YOLO) e Depth per la stima della distanza.

### Cameras positioning

Posizionamento delle Telecamere: Usa una tabella (come la 3.1 del PDF) per descrivere i parametri delle 
3 telecamere (Rear, Left, Right) presi da config.py (es. REAR_CAMERA_TRANSFORM, LEFT_CAMERA_TRANSFORM, CAMERA_FOV, ecc.).

### RCTA Sensor Configuration


| Camera    | Position (X, Y, Z)  | Resolution   | FPS   | FOV (deg)   | Rotation (Pitch, Yaw)   |
|:----------|:--------------------|:-------------|:------|:------------|:------------------------|
| **Rear**  | `(-2.0, 0.0, 0.9)`  | 416x416      | 20    | 60          | `(0, 180)`              |
| **Left**  | `(-2.0, 0.0, 0.9)`  | 416x416      | 20    | 60          | `(0, 240)`              |
| **Right** | `(-2.0, 0.0, 0.9)`  | 416x416      | 20    | 60          | `(0, 120)`              |

### Cameras view
Viste delle Telecamere: Includi screenshot delle 3 viste della telecamera (generate da cv2.imshow in main.py) 
per mostrare cosa "vede" il sistema.

![image](../img/view3.png)
