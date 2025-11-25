import paho.mqtt.client as mqtt
import json
import time
import sys
import os

# Import config
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)

try:
    import config
except ImportError:
    print("MQTT_PUBLISHER [ERROR: Config not found, using defaults]")


class MQTTPublisher:
    def __init__(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        self.connected = False
        self.broker = config.MQTT_BROKER
        self.port = config.MQTT_PORT
        self.topic = config.MQTT_TOPIC_ALERTS

        # Try to connect
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()  # Start background thread
            print(f"MQTT_PUBLISHER [Connecting to {self.broker}:{self.port}...]")
        except Exception as e:
            print(f"MQTT_PUBLISHER [ERROR: Could not connect to broker: {e}]")

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            self.connected = True
            print(f"MQTT_PUBLISHER [Connected successfully to {self.broker}]")
        else:
            print(f"MQTT_PUBLISHER [Connection failed: {reason_code}]")

    def _on_disconnect(self, client, userdata, reason_code, properties):
        self.connected = False
        print(f"MQTT_PUBLISHER [Disconnected: {reason_code}]")

    def publish_alerts(self, dangerous_objects):
        if not self.connected:
            # Not connected, skip publishing (but don't block)
            return

        if not dangerous_objects:
            # No alerts, skip
            return

        # Prepare MQTT message
        message = {
            "alert": True,
            "timestamp": time.time(),
            "objects": dangerous_objects
        }

        # Publish (non-blocking, async)
        try:
            result = self.client.publish(
                self.topic,
                json.dumps(message),
                qos=1  # At least once delivery
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                pass  # Success, no need to log every message
            else:
                print(f"MQTT_PUBLISHER [ERROR: Publish failed with code {result.rc}]")

        except Exception as e:
            print(f"MQTT_PUBLISHER [ERROR: {e}]")

    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            print("MQTT_PUBLISHER [Disconnected]")