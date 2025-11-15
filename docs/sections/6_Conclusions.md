---
layout: default
title: Conclusions
nav_order: 8
---

# Conclusions

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

- 5 Scenario complesso, multipli attraversamento

