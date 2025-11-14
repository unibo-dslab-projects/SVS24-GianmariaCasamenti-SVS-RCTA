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

# SCENARIO 1: VEHICLE CROSSING (20 km/h)
TARGET_VEHICLE_MODEL = 'vehicle.tesla.model3'
TARGET_SPAWN_TRANSFORM_VEHICLE = carla.Transform(
    carla.Location(x=-37.0, y=-40.0, z=0.5),
    carla.Rotation(yaw=270)
)
TARGET_VELOCITY_20 = carla.Vector3D(x=0, y=5.56, z=0)  # 20 km/h = 5.56 m/s


# SCENARIO 2: BICYCLE CROSSING (10 e 15 km/h)
BICYCLE_MODEL = 'vehicle.diamondback.century'
BICYCLE_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-37.0, y=-40.0, z=0.5),
    carla.Rotation(yaw=270)
)
BICYCLE_VELOCITY_10 = carla.Vector3D(x=0, y=2.78, z=0)  # 10 km/h = 2.78 m/s
BICYCLE_VELOCITY_15 = carla.Vector3D(x=0, y=4.17, z=0)  # 15 km/h = 4.17 m/s


# SCENARIO 3: PEDESTRIAN ADULT (5 km/h)
PEDESTRIAN_ADULT_MODEL = 'walker.pedestrian.0002'
PEDESTRIAN_ADULT_SPEED = 1.39  # 5 km/h = 1.39 m/s

# Pedone attraversa da DESTRA verso SINISTRA
PEDESTRIAN_ADULT_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-35.0, y=-35.0, z=0.5),
    carla.Rotation(yaw=90)
)
PEDESTRIAN_ADULT_DESTINATION = carla.Location(x=-33.0, y=-20.0, z=0.5)


# SCENARIO 4: PEDESTRIAN CHILD (5 e 10 km/h)
PEDESTRIAN_CHILD_MODEL = 'walker.pedestrian.0026'  # Modello bambino
PEDESTRIAN_CHILD_SPEED_5 = 1.39   # 5 km/h = 1.39 m/s
PEDESTRIAN_CHILD_SPEED_10 = 2.78  # 10 km/h = 2.78 m/s

# Bambino attraversa da DESTRA verso SINISTRA
PEDESTRIAN_CHILD_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-35.0, y=-35.0, z=0.5),
    carla.Rotation(yaw=-90)  # Verso sinistra
)
PEDESTRIAN_CHILD_DESTINATION = carla.Location(x=-33.0, y=-20.0, z=0.5)



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