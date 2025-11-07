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
    carla.Location(x=-31.4, y=-40.0, z=0.5),
    carla.Rotation(yaw =90)
)
PEDESTRIAN_DESTINATION = carla.Location(x=-31.4, y=-30.2, z=0.5)
PEDESTRIAN_WALK_SPEED = 1.4

#_____________________________________CAMERAS SETTING________________________
CAMERA_IMAGE_WIDTH = 416 #640
CAMERA_IMAGE_HEIGHT = 416 #384
CAMERA_FOV = "110"
REAR_CAMERA_TRANSFORM = carla.Transform(
    carla.Location(x=-2.0, y=0.0, z=0.9),
    carla.Rotation(yaw =180)
)
LEFT_CAMERA_TRANSFORM = carla.Transform(
    carla.Location(x=-2.0, y=-0.5, z=0.9),
    carla.Rotation(yaw =-135)
)
RIGHT_CAMERA_TRANSFORM = carla.Transform(
    carla.Location(x=-2.0, y=0.5, z=0.9),
    carla.Rotation(yaw=135)
)
YOLO_MODEL_PATH = 'models/yolov8n.pt'


#_____________________________________CONTROLLER SETTING________________________
THROTTLE = 0.6
STEER_INCREMENT = 0.05

#_____________________________________RCTA SETTING________________________
TTC_THRESHOLD = 2.5 #secondi
DIST_THRESHOLD = 4.0 #metri
DEBUG = False



