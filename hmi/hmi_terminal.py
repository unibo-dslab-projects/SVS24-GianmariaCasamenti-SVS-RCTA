import paho.mqtt.client as mqtt
import json
import sys
import os

# --- CONFIGURAZIONE PATH ---
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
try:
    import config
except ImportError:
    print("HMI_TERMINAL [ERROR: Config not found]")
    sys.exit(1)


def _on_connect(client, userdata, flags, reason_code, propertie):
    """
    Callback when a connection is established.
    """
    if reason_code == 0:
        print(f"HMI_TERMINAL [Connected to the broker {config.MQTT_BROKER}]")
        client.subscribe(config.MQTT_TOPIC_ALERTS)
        print(f"HMI_TERMINAL [Subscribed at the topic'{config.MQTT_TOPIC_ALERTS}]'")
    else:
        print(f"HMI_TERMINAL [Connection failed {reason_code}]")


def _on_message(client, userdata, msg):
    """
    Callback when a message is received (Versione aggiornata per JSON strutturato).
    """
    try:
        # Decodifica JSON
        data = json.loads(msg.payload.decode())

        if data.get("alert") == True:
            objects = data.get("objects", [])

            if not objects:
                # Questo non dovrebbe accadere se alert=True, ma lo gestiamo
                print("HMI_TERMINAL [ALERT: TRUE, ma lista oggetti vuota]")
                return

            # Stampa un'intestazione chiara per il gruppo di alert
            print("\n" + "=" * 46)
            print(f"--- RCTA ALERT (Timestamp: {data.get('timestamp', 'N/A')}) ---")
            print("=" * 46)

            # Itera gli oggetti e stampa i dettagli
            for obj in objects:
                zone = obj.get('zone', '???').upper()
                level = obj.get('alert_level', '???').upper()
                label = obj.get('class', '???').upper()
                dist = obj.get('distance', float('inf'))
                ttc = obj.get('ttc', float('inf'))

                # Formattazione per stampa pulita
                dist_str = f"{dist:.1f}m" if dist != float('inf') else "---m"
                ttc_str = f"{ttc:.1f}s" if ttc != float('inf') else "---s"

                print(f"[{level:<7}] Zona: {zone:<5} | Classe: {label:<8} | Dist: {dist_str:<5} | TTC: {ttc_str:<5}")

            print("-" * 46)

        else:
            # Opzionale: stampa messaggi di "SAFE" per debug
            # print("HMI_TERMINAL [SAFE]")
            pass

    except json.JSONDecodeError:
        print(f"HMI_TERMINAL [message received (not JSON): {msg.payload.decode()}]")
    except Exception as e:
        print(f"HMI_TERMINAL [Error processing message: {e}]")


def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = _on_connect
    client.on_message = _on_message

    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        print("\nHMI_TERMINAL [Waiting for messages... (Press Ctrl+C to exit)]")
        client.loop_forever()

    except ConnectionRefusedError:
        print("HMI_TERMINAL [ERROR: Impossible to connect at MQTT broker.]")
    except KeyboardInterrupt:
        print("\nHMI_TERMINAL [shutting down...]")
        client.disconnect()


if __name__ == "__main__":
    main()