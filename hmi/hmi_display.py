import paho.mqtt.client as mqtt
import json
import sys
import os
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
try:
    import config
except ImportError:
    print("HMI_DISPLAY [ERROR: Config not found]")
    sys.exit(1)


def _on_connect(client, userdata, flags, reason_code, propertie):
    """
    Callback when a connection is established.
    """
    if reason_code == 0:
        print(f"HMI_DISPLAY [Connected to the broker {config.MQTT_BROKER}]")
        #topic
        client.subscribe(config.MQTT_TOPIC_ALERTS)
        print(f"HMI_DISPLAY [Subscribed at the topic'{config.MQTT_TOPIC_ALERTS}]'")
    else:
        print(f"HMI_DISPLAY [Connection failed {reason_code}]")


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
            print(f"DANGER [{', '.join(objects)}]")
            print("\n")

    except json.JSONDecodeError:
        print(f"HMI_DISPLAY [message received (not JSON): {msg.payload.decode()}]")
    except Exception as e:
        print(f"HMI_DISPLAY [Error: {e}")

#to launch client HMI
def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = _on_connect
    client.on_message = _on_message

    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        print("HMI_DISPLAY [Wait a message]")
        # loop_forever() blocca l'esecuzione e attende i messaggi
        client.loop_forever()

    except ConnectionRefusedError:
        print("HMI_DISPLAY [ERROR: Impossible to connect at MQTT broker.]")
    except KeyboardInterrupt:
        print("HMI_DISPLAY [shutting down]")
        client.disconnect()


if __name__ == "__main__":
    main()