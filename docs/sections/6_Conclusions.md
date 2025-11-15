---
layout: default
title: Conclusions
nav_order: 8
---

# Conclusions

## Bilancio del Progetto (Punti di Forza e Debolezza)

Punti di Forza: Design modulare (Perception/Decision/HMI), utilizzo di sensori avanzati (RGBD), stima del TTC 
(più efficace della sola distanza), HMI chiara e intuitiva.

Limitazioni: Dipendenza dalla qualità della depth camera simulata (può avere artefatti), tracker basato solo
su ID (può fallire se l'oggetto viene perso e ri-rilevato), nessuna azione correttiva (solo allarmi).

## Sviluppi Futuri

Cosa scrivere: Proponi miglioramenti.

- Watch DOG

- Frenata Automatica (AEB-R): Aggiungere un modulo di "Attuazione" che applichi automaticamente i freni 
(ego_vehicle.apply_control) se viene emesso un allarme "danger" e il conducente non reagisce.


## Considerazioni Finali

Cosa scrivere: Una breve frase di chiusura sull'importanza di questi sistemi per la sicurezza veicolare e 
su come il prototipo abbia raggiunto gli obiettivi prefissati.

