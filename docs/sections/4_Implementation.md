---
layout: default
title: Implementation
nav_order: 4
---

# Solution implementation

## Perception Module

osa scrivere: Descrivi il cuore del sistema.

4.1.1 Rilevamento Oggetti (object_detector.py): Spiega l'uso di YOLOv8n (dettagliato nel Capitolo 5). 
Menziona che il modello è pre-addestrato (su COCO) e filtrato per le classi di interesse (target_classes). 
Spiega l'uso del tracking (model.track) per assegnare un ID a ogni oggetto.

4.1.2 Elaborazione della Profondità: Descrivi la funzione _decode_depth_to_meters. Spiega come converte 
l'immagine di profondità grezza di CARLA (in 3 canali uint8) in metri. Menziona l'uso di @numba.jit per l'ottimizzazione.

4.1.3 Fusione Sensoriale (RGB+D): Spiega la funzione _fuse_results. Descrivi come il bounding box (da YOLO)
viene usato per estrarre una ROI (Region of Interest) dalla mappa di profondità (in metri) per calcolare 
la distanza dell'oggetto (usando np.percentile per robustezza).

4.1.4 Tracking e Calcolo TTC: Spiega la funzione _update_tracks_and_calc_ttc. Descrivi come usi il dizionario 
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

Cosa scrivere: Descrivi come le informazioni vengono comunicate.

4.3.1 Pubblicazione degli Avvisi (mqtt_publisher.py): Spiega la classe MqttPublisher. Descrivi la funzione publish_status e il formato del payload JSON che viene inviato (sia per alert: True che alert: False).

4.3.2 Visualizzazione HMI (hmi_display.py): Spiega che questo è uno script Pygame separato che agisce da client MQTT.

Callback Messaggi: Descrivi la funzione _on_message e come aggiorna lo stato globale radar_data.

Interfaccia Grafica: Descrivi le funzioni draw_sector e draw_labels, spiegando come lo stato (SAFE, WARNING, DANGER) viene tradotto nei colori (verde, giallo, rosso) sull'interfaccia.