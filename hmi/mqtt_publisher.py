import paho.mqtt.client as mqtt
import json
import config


class MqttPublisher:
    """
    Manage the connection to MQTT broker and publish data.
    """
    def __init__(self, broker_address=config.MQTT_BROKER, port=config.MQTT_PORT):
        self.broker_address = broker_address
        self.port = port
        self.topic = config.MQTT_TOPIC_ALERTS

        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self.is_connected = False

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print(f"HMI_PUBLISHER [Connected to the broker {self.broker_address}]")
            self.is_connected = True
        else:
            print(f"HMI_PUBLISHER [Connection failed: {reason_code}]")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        self.is_connected = False
        if reason_code != 0:
            print(f"HMI_PUBLISHER [Unexpected error: {reason_code}")
        else:
            print("HMI_PUBLISHER [Disconnected to the broker]")

    def connect(self):
        """Try to connect to the broker."""
        try:
            print(f"HMI_PUBLISHER [connection attempt  {self.broker_address}:{self.port}]")
            self.client.connect(self.broker_address, self.port, 60)
            self.client.loop_start()  # Gestisce la riconnessione e il traffico in background
        except ConnectionRefusedError:
            print(f"HMI_PUBLISHER [ERROR: Rejected connection to broker {self.broker_address}]")
        except Exception as e:
            print(f"HMI_PUBLISHER [ERROR: Impossible to connect: {e}]")

    def disconnect(self):
        """Disconnect from the broker."""
        self.client.loop_stop()
        self.client.disconnect()

    def publish_status(self, dangerous_objects_list):
        """
        Publish status to MQTT broker (alert or safe).
        :param dangerous_objects_list: List of dangerous objects.
        """
        if not self.is_connected:
            # Non tentare di pubblicare se non siamo connessi
            return

        if dangerous_objects_list:
            payload = {
                "alert": True,
                "objects": dangerous_objects_list
            }
        else:
            payload = {
                "alert": False,
                "objects": []
            }

        payload_str = json.dumps(payload)
        result = self.client.publish(self.topic, payload_str)

        #Debug
        if result[0] != 0:
            print(f"HMI_PUBLISHER [Publishing error: {result[0]}]")
        # else:
        #     if payload['alert']:
        #         print(f"HMI Publisher: Messaggio di ALLARME pubblicato.")
        #     else:
        #         print(f"HMI Publisher: Messaggio 'Libero' pubblicato.")