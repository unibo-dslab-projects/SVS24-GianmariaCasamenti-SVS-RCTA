---
layout: default
title: Test
nav_order: 7
---

# Test and Result
The testing methodology is adapted from the scientific article "Study on Test and Evaluation Method 
of Rear Cross Traffic Alert System". 

Following this standard, we established a baseline geometric 
setup where the Vehicle Under Test (VUT) is placed in a parking spot, in reverse gear, and kept stationary.


## Scenarios of test
To simulate real-world blind spots, two blocking vehicles are parked immediately adjacent to the VUT. 

This configuration forces the sensors to detect targets emerging from occlusion,
testing the system's reaction time and field of view.

![image](../img/paper.png)

We implemented four distinct dynamic scenarios, defined in ```parking_lot_scenario.py```, 
to cover different target sizes and speeds:

- **Vehicle Crossing**: A target vehicle crosses behind the VUT at 15 km/h. 
This tests the system's ability to track large, fast-moving objects.

- **Cyclist Crossing**: An adult cyclist crosses at speeds of 10 km/h . 
This represents a medium-speed target with a smaller radar/visual cross-section.

- **Pedestrian Adult**: An adult pedestrian walks across the path at 5 km/h.

- **Pedestrian Child**: A child pedestrian model crosses at 7. 
This is the most critical scenario due to the target's small size and potential to be 
completely obscured by the blocking vehicles.

<div class="carousel-container">
  <div class="carousel">
    <div class="carousel-slide active">
      <img src="../img/scenario1.png" alt="Camera mounting position">
    </div>
    <div class="carousel-slide">
      <img src="../img/scenario2.png" alt="Field of view coverage">
    </div>
    <div class="carousel-slide">
      <img src="../img/scenario3.png" alt="Detection zones">
    </div>
    <div class="carousel-slide">
      <img src="../img/scenario4.png" alt="Sensor configuration">
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


### Environmental Variables
To evaluate the robustness of the perception module (YOLO + Depth), 
each of the four scenarios above was tested under two distinct environmental conditions:

- Ideal Conditions (bad_weather=False): Clear noon weather with optimal lighting and visibility.

- Adverse Conditions (bad_weather=True): Heavy rain and fog. This tests the degradation of 
the RGB camera's visibility and the depth camera's clarity, simulating a worst-case real-world situation.

## Evaluation Metrics 

The primary quantitative metric for evaluation is the Time-to-Collision (TTC) at the moment of the first alarm.
According to the reference study, a successful RCTA system must trigger an alarm while the TTC is
greater than 1.7 seconds. Our system uses a more conservative safety threshold of 2.5 seconds 
(defined in config.py) to ensure an adequate safety margin.

In the absence of an automated ground-truth validation suite, the system performance is 
further evaluated using the following qualitative metrics:

Detection Correctness: Verifying if the specific class (Car vs. Person) 
was correctly identified by YOLO despite the occlusion caused by the blocking cars.

False Positive Rate: Monitoring if the system incorrectly triggers an 
alarm on the stationary blocking vehicles or background objects.
This aligns with the "False Trigger" test method described in the literature, 
where the system must remain silent if a target stops before entering the collision path.

Alert Timeliness: Assessing if the "Danger" status (Red) on the HMI appears immediately when the
calculated TTC drops below the threshold, validating the low latency of the MQTT communication.

## Analysis of results

Cosa scrivere: Riporta eventuali osservazioni.

Impatto Meteo Avverso: Il meteo avverso ha ridotto l'accuratezza di YOLO o la precisione della mappa di profondità?

Occlusioni: Come si è comportato il sistema quando l'attore era parzialmente nascosto dalle blocking_cars?

6.4 Analisi degli Errori

Cosa scrivere: Descrivi i problemi riscontrati.

Falsi Positivi: Il sistema ha generato allarmi per oggetti fermi o non pericolosi?

Falsi Negativi: Il sistema ha mancato un attore in avvicinamento? (Es. un pedone piccolo o un ciclista veloce).

Stabilità del TTC: Il valore del TTC era stabile o fluttuava molto a causa di errori nella stima della distanza?
