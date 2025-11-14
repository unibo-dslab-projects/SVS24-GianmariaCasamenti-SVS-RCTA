import carla

"""
Configuration constants for the CARLA simulation.
"""

#Server connection
HOST = 'localhost'
PORT = 2000
TIMEOUT = 10

#_____________________________________MQTT SETTING________________________
MQTT_BROKER = HOST
MQTT_PORT = 1883
MQTT_TOPIC_ALERTS = "rcta/alerts"

#_____________________________________SCENARIO SETTING________________________
MAP_NAME = 'Town05'
EGO_VEHICLE_MODEL = 'vehicle.audi.tt'
EGO_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-31.0, y=-30, z=0.5),
    carla.Rotation(yaw=0)
)
BLOCKING_VEHICLE_MODELS = [
    'vehicle.toyota.prius',
    'vehicle.nissan.patrol',
    'vehicle.ford.mustang',
    'vehicle.chevrolet.impala'
]

#scenario 1
BLOCKING_VEHICLE_TRANSFORMS = [
    carla.Transform(
        carla.Location(x=-30.0, y=-27.0, z=0.5),
        carla.Rotation(yaw=0)
    ),
    carla.Transform(
        carla.Location(x=-30.0, y=-32.8, z=0.5),
        carla.Rotation(yaw=0)
    ),
     carla.Transform(
        carla.Location(x=-30.0, y=-35.5, z=0.5),
        carla.Rotation(yaw=0)
    )
]
#scenario1
TARGET_VEHICLE_MODEL = 'vehicle.tesla.model3'
TARGET_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-35.0, y=-15.0, z=0.5),
    carla.Rotation(yaw=270)
)
TARGET_VELOCITY= carla.Vector3D(x=0, y=-5.56, z=0)  # 20 km/h = 5.56 m/s

#scenario2
BICYCLE_MODEL = 'vehicle.diamondback.century'
# Spawn da SINISTRA
BICYCLE_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-35.0, y=-15.0, z=0.5),
    carla.Rotation(yaw=270)
)
BICYCLE_VELOCITY= carla.Vector3D(x=0, y=-2.78, z=0)  # 10 km/h = 2.78 m/s

#scenario 3 and 4
PEDESTRIAN_MODEL = 'walker.pedestrian.0038'
PEDESTRIAN_CHILD_MODEL = 'walker.pedestrian.0048'
PEDESTRIAN_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-33, y=-25.0, z=0.5),
    carla.Rotation(yaw =270)
)

PEDESTRIAN_DESTINATION = carla.Location(x=-31.5, y=-37.0, z=0.5)
PEDESTRIAN_WALK_SPEED = 1.39  # 5 km/h = 1.39 m/s
PEDESTRIAN_CHILD_WALK_SPEED = 2.0  # 7 km/h

#_____________________________________CAMERAS SETTING________________________
CAMERA_IMAGE_WIDTH = 416 #640
CAMERA_IMAGE_HEIGHT = 416 #384
CAMERA_FOV = "60"
COMMON_REAR_LOCATION = carla.Location(x=-2.0, y=0.0, z=0.9)
#FOV 60° centrato a 180° -> Copre da 150° a 210°
REAR_CAMERA_TRANSFORM = carla.Transform(
    COMMON_REAR_LOCATION,
    carla.Rotation(yaw =180)
)
#FOV 60° centrato a 240° (180° + 60°) -> Copre da 210° a 270°
LEFT_CAMERA_TRANSFORM = carla.Transform(
    COMMON_REAR_LOCATION,
    carla.Rotation(yaw =240)
)
# FOV 60° centrato a 120° (180° - 60°) -> Copre da 90° a 150°
RIGHT_CAMERA_TRANSFORM = carla.Transform(
    COMMON_REAR_LOCATION,
    carla.Rotation(yaw=120)
)
YOLO_MODEL_PATH = 'models/yolov8n.pt'

#_____________________________________RCTA SETTING________________________
TTC_THRESHOLD = 2.5 #secondi
DIST_THRESHOLD = 3.0 #metri
DEBUG = True

# True = asincrono (più stile notebook), False = sincrono (originale)
ASYNC_MODE = True

# Target FPS per il main loop (usato con clock.tick())
TARGET_FPS = 20  # Deve corrispondere a 1/fixed_delta_seconds se sincrono
DELTA_SECONDS = 0.05
# Sensor tick per le camere (in secondi)
# 0.0 = aggiorna ogni tick, >0.0 = aggiorna ogni N secondi
SENSOR_TICK = 0.0  # Imposta a 0.05 per 20 Hz se vuoi rate ridotto
# ================================================