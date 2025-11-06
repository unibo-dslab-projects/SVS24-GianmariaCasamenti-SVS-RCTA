import time
import sys
import os

# Aggiungi la root del progetto al path per poter importare i moduli
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    import config
    from hmi.mqtt_publisher import MqttPublisher
except ImportError as e:
    print(f"Errore di importazione: {e}")
    print("Assicurati di eseguire lo script dalla root del progetto o che i percorsi siano corretti.")
    sys.exit(1)


def main():
    """
    Script di test per simulare scenari RCTA e verificare la risposta dell'HMI grafica.
    """
    print("--- Starting MQTT HMI Test ---")
    publisher = None
    try:
        publisher = MqttPublisher(
            broker_address=config.MQTT_BROKER,
            port=config.MQTT_PORT
        )
        publisher.connect()

        # Attesa attiva della connessione
        print("Waiting for broker connection...", end='', flush=True)
        for _ in range(5):
            if publisher.is_connected:
                break
            time.sleep(1)
            print(".", end='', flush=True)
        print("")

        if not publisher.is_connected:
            print("ERROR: Could not connect to MQTT Broker.")
            return

        print("Connection established. Starting scenario simulation loop.\n")

        while True:
            # SCENARIO 1: Tutto tranquillo (SAFE)
            # L'HMI dovrebbe mostrare settori grigi/verdi trasparenti
            print("Scenario [SAFE]: Nessun rilevamento")
            publisher.publish_status([])
            time.sleep(3)

            # SCENARIO 2: Avvicinamento statico da dietro (WARNING)
            # L'HMI dovrebbe mostrare il settore posteriore in GIALLO fisso
            alert_rear_static = ["rear:person_near"]
            print(f"Scenario [WARNING]: {alert_rear_static}")
            publisher.publish_status(alert_rear_static)
            time.sleep(4)

            # SCENARIO 3: Pericolo imminente da sinistra (DANGER)
            # L'HMI dovrebbe mostrare il settore sinistro LAMPEGGIANTE ROSSO
            # Il settore posteriore potrebbe rimanere giallo se l'oggetto è ancora lì
            alert_left_fast = ["rear:person_near", "left:approaching_fast"]
            print(f"Scenario [DANGER+WARNING]: {alert_left_fast}")
            publisher.publish_status(alert_left_fast)
            time.sleep(5)

            # SCENARIO 4: Pericolo passato, rimane solo un'auto parcheggiata a destra (WARNING)
            # Settore destro GIALLO, gli altri SAFE
            alert_right_static = ["right:car_near"]
            print(f"Scenario [WARNING]: {alert_right_static}")
            publisher.publish_status(alert_right_static)
            time.sleep(4)

            # SCENARIO 5: Multi-direzione danger (DANGER)
            # Sinistra e Destra lampeggiano ROSSO
            alert_multi = ["left:approaching_fast", "right:approaching_fast"]
            print(f"Scenario [MULTI-DANGER]: {alert_multi}")
            publisher.publish_status(alert_multi)
            time.sleep(4)

    except KeyboardInterrupt:
        print("\n\n--- Test interrotto dall'utente ---")
    except Exception as e:
        # Stampa l'intero stack trace per debug migliore
        import traceback
        traceback.print_exc()
        print(f"\nSi è verificato un errore inatteso: {e}")
    finally:
        if publisher:
            if publisher.is_connected:
                publisher.disconnect()
            # Attendiamo un attimo che il thread di loop si chiuda
            time.sleep(0.5)
            print("Publisher disconnesso correttamente.")


if __name__ == '__main__':
    main()