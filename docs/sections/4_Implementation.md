---
layout: default
title: Implementation
nav_order: 4
---

# Solution implementation

## Perception Module

osa scrivere: Descrivi il cuore del sistema.

### Rilevamento Oggetti (object_detector.py): 
Spiega l'uso di YOLOv8n (dettagliato nel Capitolo 5). 
Menziona che il modello è pre-addestrato (su COCO) e filtrato per le classi di interesse (target_classes). 
Spiega l'uso del tracking (model.track) per assegnare un ID a ogni oggetto.

### Elaborazione della Profondità: 
Descrivi la funzione _decode_depth_to_meters. Spiega come converte 
l'immagine di profondità grezza di CARLA (in 3 canali uint8) in metri. Menziona l'uso di @numba.jit per l'ottimizzazione.

### Fusione Sensoriale (RGB+D): 
Spiega la funzione _fuse_results. Descrivi come il bounding box (da YOLO)
viene usato per estrarre una ROI (Region of Interest) dalla mappa di profondità (in metri) per calcolare 
la distanza dell'oggetto (usando np.percentile per robustezza).

### Tracking e Calcolo TTC: 
Spiega la funzione _update_tracks_and_calc_ttc. Descrivi come usi il dizionario 
tracked_objects_* per memorizzare lo stato precedente (distanza, tempo) e calcolare la velocità relativa 
(delta_d / delta_t) e, infine, il TTC (obj['dist'] / rel_velocity).

## Decision module 
Cosa scrivere: Descrivi la logica di allerta.

Logica di Valutazione: Spiega la funzione evaluate. Prima controlla is_reversing.

Generazione Allarmi: Spiega la doppia soglia:

Se il TTC di un oggetto è inferiore a TTC_THRESHOLD (da config.py), genera un allarme di livello "danger".

Altrimenti, se la distanza è inferiore a DIST_THRESHOLD, genera un allarme di livello "warning".

Formato Output: Mostra la struttura dati della lista dangerous_objects_list che viene restituita.

## Comunicazione e HMI (MQTT)

This module handles the communication of alerts from the main simulation to the end-user interface. 
This is achieved using an MQTT (Message Queuing Telemetry Transport) broker, 
which decouples the perception system from the display.

### MQTT Publisher
The MqttPublisher class, defined in mqtt_publisher.py, manages the connection to the MQTT broker 
specified in the config.py file. It handles connection establishment (connect) and runs a background network loop
(self.client.loop_start()) to manage publishing messages asynchronously.

The primary function is publish_status(dangerous_objects_list). This method receives the 
list of threats directly from the DecisionMaker module. It then constructs a JSON
payload to be sent to the MQTT_TOPIC_ALERTS topic.

The payload format is binary, based on whether any threats are present:

- If no threats are found (the list is empty), it publishes a "safe" message:

```JSON
{"alert": false, "objects": []}
```

- If threats are detected, it publishes an "alert" message containing the list of dangerous objects:

```JSON
{"alert": true, "objects": [...]}
```

The objects list contains detailed dictionaries for each object, including its zone, alert_level, class, distance, and ttc.

### HMI Display

The hmi_display.py script is a standalone Pygame application that functions as the 
MQTT client for the driver's interface. It runs as a completely separate process 
from the main CARLA simulation. It initializes its own MQTT client and subscribes
to the same MQTT_TOPIC_ALERTS topic, listening for the JSON messages published by
the MqttPublisher.

![image](../img/hmi.png)

Message Callback (_on_message) When a new message arrives from the broker,
the _on_message callback function is triggered. This function is responsible 
for parsing the incoming JSON payload.

- It first creates a new_data dictionary, resetting all zones to 'SAFE' by default.

- If the payload's "alert" key is True, it iterates through the "objects" list.

- For each object, it updates the corresponding zone (left, rear, or right) in new_data with its state (alert level), label (class), dist, and ttc.

- The logic correctly prioritizes 'DANGER' over 'WARNING'.

- Finally, it atomically updates the global radar_data variable, which the main Pygame loop uses for drawing.
