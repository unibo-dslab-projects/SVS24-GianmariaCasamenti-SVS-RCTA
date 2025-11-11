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
TARGET_VEHICLE_MODEL = 'vehicle.mercedes.sprinter'
TARGET_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-35.0, y=-40.0, z=0.5),
    carla.Rotation(yaw=90)
)
#2 m/s (circa 7 km/h)
TARGET_VELOCITY = carla.Vector3D(x=0, y=2.0, z=0)
PEDESTRIAN_MODEL = 'walker.pedestrian.0002'
PEDESTRIAN_SPAWN_TRANSFORM = carla.Transform(
    carla.Location(x=-33, y=-40.0, z=0.5),
    carla.Rotation(yaw =90)
)

PEDESTRIAN_DESTINATION = carla.Location(x=-31.4, y=-25.2, z=0.5)
PEDESTRIAN_WALK_SPEED = 2.0

PEDESTRIAN_ACTORS = [
    {
        'model': 'walker.pedestrian.0002', # Pedone 1 (simile all'originale)
        'spawn': carla.Transform(carla.Location(x=-31.4, y=-40.0, z=0.5), carla.Rotation(yaw=90)),
        'dest': carla.Location(x=-31.4, y=-30.2, z=0.5),
        'speed': 1.4
    },
    {
        'model': 'walker.pedestrian.0003', # Pedone 2 (attraversa più lontano)
        'spawn': carla.Transform(carla.Location(x=-33.0, y=-42.0, z=0.5), carla.Rotation(yaw=90)),
        'dest': carla.Location(x=-33.0, y=-28.0, z=0.5),
        'speed': 1.5
    },
    {
        'model': 'walker.pedestrian.0004', # Pedone 3 (cammina in direzione opposta)
        'spawn': carla.Transform(carla.Location(x=-34.0, y=-28.0, z=0.5), carla.Rotation(yaw=-90)),
        'dest': carla.Location(x=-34.0, y=-42.0, z=0.5),
        'speed': 1.3
    }
]

BICYCLE_ACTORS = [
    {
        'model': 'vehicle.diamondback.century', # Bici 1 (attraversa verso nord)
        'spawn': carla.Transform(carla.Location(x=-36.0, y=-45.0, z=0.5), carla.Rotation(yaw=90)),
        'velocity': carla.Vector3D(x=0, y=3.0, z=0) # 3 m/s (più veloce di un pedone)
    },
    {
        'model': 'vehicle.gazelle.omafiets', # Bici 2 (attraversa verso sud)
        'spawn': carla.Transform(carla.Location(x=-37.0, y=-28.0, z=0.5), carla.Rotation(yaw=-90)),
        'velocity': carla.Vector3D(x=0, y=-2.5, z=0) # 2.5 m/s
    }
]

CROSSING_VEHICLE_ACTORS = [
    {
        'model': 'vehicle.tesla.model3', # Auto 1 (da destra, veloce)
        'spawn': carla.Transform(carla.Location(x=-35.0, y=-45.0, z=0.5), carla.Rotation(yaw=90)),
        'velocity': carla.Vector3D(x=0, y=5.0, z=0) # Veloce: 5 m/s (~18 km/h)
    },
    {
        'model': 'vehicle.volkswagen.t2', # Auto 2 (da destra, lenta, furgone)
        'spawn': carla.Transform(carla.Location(x=-36.0, y=-47.0, z=0.5), carla.Rotation(yaw=90)),
        'velocity': carla.Vector3D(x=0, y=3.5, z=0) # Lenta: 3.5 m/s (~12.6 km/h)
    },
    {
        'model': 'vehicle.harley-davidson.low_rider', # Auto 3 (da sinistra, molto veloce, moto)
        'spawn': carla.Transform(carla.Location(x=-37.0, y=-25.0, z=0.5), carla.Rotation(yaw=-90)),
        'velocity': carla.Vector3D(x=0, y=-6.0, z=0) # Molto veloce: 6 m/s (~21.6 km/h)
    },
    {
        'model': 'vehicle.audi.a2', # Auto 4 (da sinistra, media)
        'spawn': carla.Transform(carla.Location(x=-35.5, y=-24.0, z=0.5), carla.Rotation(yaw=-90)),
        'velocity': carla.Vector3D(x=0, y=-4.0, z=0) # Media: 4 m/s (~14.4 km/h)
    }
]

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