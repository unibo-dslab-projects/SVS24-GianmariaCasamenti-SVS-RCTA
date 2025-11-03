import paho.mqtt.client as mqtt
import json
import sys
import os

# --- Hack per importare 'config' dalla directory principale ---
# Questo aggiunge la directory genitore (la root del progetto) al Python Path
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
try:
    import config
except ImportError:
    print("ERROR: Config not found.")
    sys.exit(1)


def _on_connect(client, userdata, flags, reason_code, propertie):
    """
    Callback when a connection is established.
    """
    if reason_code == 0:
        print(f"HMI Display: Connected to the broker {config.MQTT_BROKER}")
        #topic
        client.subscribe(config.MQTT_TOPIC_ALERTS)
        print(f"HMI Display: Subscribed at the topic'{config.MQTT_TOPIC_ALERTS}'")
    else:
        print(f"HMI Display: Connection failed {reason_code}")


def _on_message(client, userdata, msg):
    """
    Callback when a message is received.
    """
    # print(f"Ricevuto messaggio raw: {msg.payload.decode()}")
    try:
        # Decodifica JSON
        data = json.loads(msg.payload.decode())

        if data.get("alert") == True:
            objects = data.get("objects", [])
            print(f" Detected danger: {', '.join(objects)}")
            print("\n")

        #elif data.get("alert") == False:
        #    print("--- RCTA: safe ---")

    except json.JSONDecodeError:
        print(f"HMI Display: message received (not JSON): {msg.payload.decode()}")
    except Exception as e:
        print(f"HMI Display: Elaboration error: {e}")

#to launch client HMI
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = _on_connect
    client.on_message = _on_message

    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        print("Run HMI Display... Wait a message...")
        # loop_forever() blocca l'esecuzione e attende i messaggi
        client.loop_forever()

    except ConnectionRefusedError:
        print("\nERRORE: Impossible to connect at MQTT broker.")
    except KeyboardInterrupt:
        print("\nHMI Display shutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()