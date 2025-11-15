---
layout: default
title: Test
nav_order: 7
---

# Test and Result

Introdurre articolo scientifico.

## Scenarios of test

Cosa scrivere: Riferisciti di nuovo ai 4 scenari di parking_lot_scenario.py. 
Spiega che hai testato ognuno di essi in due condizioni ambientali:

Meteo Sereno (bad_weather=False)

Meteo Avverso (bad_weather=True)

## Evaluation Metrics (Qualitative)

Cosa scrivere: Visto che non hai un ground truth automatico, la valutazione sarà qualitativa.

Correttezza Rilevamento: Il sistema ha rilevato l'attore in avvicinamento?

Tempestività Allarme: L'allarme "warning" e "danger" sono scattati al momento opportuno?

Robustezza HMI: L'HMI ha rispecchiato correttamente lo stato inviato via MQTT?

## Analysis of results

Cosa scrivere: Riporta eventuali osservazioni.

Impatto Meteo Avverso: Il meteo avverso ha ridotto l'accuratezza di YOLO o la precisione della mappa di profondità?

Occlusioni: Come si è comportato il sistema quando l'attore era parzialmente nascosto dalle blocking_cars?

6.4 Analisi degli Errori

Cosa scrivere: Descrivi i problemi riscontrati.

Falsi Positivi: Il sistema ha generato allarmi per oggetti fermi o non pericolosi?

Falsi Negativi: Il sistema ha mancato un attore in avvicinamento? (Es. un pedone piccolo o un ciclista veloce).

Stabilità del TTC: Il valore del TTC era stabile o fluttuava molto a causa di errori nella stima della distanza?

# scenarios 
## Testing

Ogni scenario deve richiedere BlockingCar=True/False e BadWether=Ture/False

- 1️⃣ Scenario Veicolo
Target: Veicolo che attraversa dietro al veicolo in test (VUT)
Velocità: 20 km/h
Configurazione:

VUT in retromarcia, stazionario
Due veicoli parcheggiati ai lati (ostacoli che creano "blind spot")
Distanza laterale tra VUT e ostacoli: 0,7m
Distanza longitudinale: 0,5m

- 2️⃣ Scenario Ciclista
Target: Ciclista adulto che attraversa
Velocità testate: 10 km/h e 15 km/h
Configurazione: Identica allo scenario veicolo

- 3️⃣ Scenario Pedone Adulto
Target: Pedone adulto che attraversa
Velocità: 5 km/h
Configurazione: Identica agli scenari precedenti

- 4️⃣ Scenario Pedone Bambino
Target: Pedone bambino
Velocità testate: 5 km/h e 10 km/h
Configurazione: Identica agli scenari precedenti

- 5 Scenario complesso, multipli attraversamen