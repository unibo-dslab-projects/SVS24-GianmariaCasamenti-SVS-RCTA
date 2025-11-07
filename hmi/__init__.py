"""
Questo package gestisce tutta la comunicazione e la visualizzazione degli avvisi per l'utente.

mqtt_publisher.py: Una classe che si occupa di inviare i comandi di allerta (generati da decision_making) a un broker
 MQTT.

hmi_terminal.py: Uno script indipendente e separato che l'utente avvierà per visualizzare gli allarmi. Si iscrive al
topic MQTT e mostra a schermo gli avvisi ricevuti, simulando il cruscotto del veicolo.
"""