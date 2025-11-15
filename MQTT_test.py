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
    Script di test per simulare scenari RCTA inviando
    il NUOVO formato JSON strutturato.
    """
    print("--- Starting MQTT HMI Test (Formato JSON v2) ---")
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
            print("Scenario [SAFE]: Nessun rilevamento")
            publisher.publish_status([]) # Invia una lista vuota
            time.sleep(3)

            # SCENARIO 2: Avvicinamento statico da dietro (WARNING)
            alert_rear_static = [
                {"zone": "rear", "alert_level": "warning", "class": "person", "distance": 2.8, "ttc": float('inf')}
            ]
            print(f"Scenario [WARNING]: Oggetto 'person' a 2.8m (rear)")
            publisher.publish_status(alert_rear_static)
            time.sleep(4)

            # SCENARIO 3: Pericolo imminente da sinistra + Warning posteriore (DANGER+WARNING)
            alert_left_fast = [
                {"zone": "rear", "alert_level": "warning", "class": "person", "distance": 2.5, "ttc": float('inf')},
                {"zone": "left", "alert_level": "danger", "class": "car", "distance": 8.0, "ttc": 1.5}
            ]
            print(f"Scenario [DANGER+WARNING]: 'car' (left, 1.5s TTC) + 'person' (rear, 2.5m)")
            publisher.publish_status(alert_left_fast)
            time.sleep(5)

            # SCENARIO 4: Oggetto statico a destra (WARNING)
            alert_right_static = [
                {"zone": "right", "alert_level": "warning", "class": "truck", "distance": 3.1, "ttc": float('inf')}
            ]
            print(f"Scenario [WARNING]: Oggetto 'truck' a 3.1m (right)")
            publisher.publish_status(alert_right_static)
            time.sleep(4)

            # SCENARIO 5: Multi-direzione danger (DANGER)
            alert_multi = [
                {"zone": "right", "alert_level": "danger", "class": "car", "distance": 7.0, "ttc": 1.4}
            ]
            print(f"Scenario [MULTI-DANGER]: Due oggetti in avvicinamento rapido")
            publisher.publish_status(alert_multi)
            time.sleep(4)

    except KeyboardInterrupt:
        print("\n\n--- Test interrotto dall'utente ---")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nSi è verificato un errore inatteso: {e}")
    finally:
        if publisher:
            if publisher.is_connected:
                publisher.disconnect()
            time.sleep(0.5)
            print("Publisher disconnesso correttamente.")


if __name__ == '__main__':
    main()