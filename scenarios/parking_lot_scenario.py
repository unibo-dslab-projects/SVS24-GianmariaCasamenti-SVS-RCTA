import carla
import random
import config
import threading

def setup_rcta_base_scenario(world, spawner, blocking_cars=True, bad_weather=False):
    # Spawn ego vehicle
    ego_vehicle = spawner.spawn_vehicle(
            model=config.EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
    )

    if not ego_vehicle:
        print(f"[ERROR] Failed to spawn ego vehicle")
        return None

    spawned_blockers = 0
    if blocking_cars:
        for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
            model = random.choice(config.BLOCKING_VEHICLE_MODELS)
            blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
            if blocker:
                spawned_blockers += 1

    if bad_weather:
        weather = carla.WeatherParameters(
            cloudiness=80.0,
            precipitation=30.0,
            precipitation_deposits=50.0,
            wind_intensity=50.0,
            fog_density=30.0,
            wetness=50.0
        )
        world.set_weather(weather)
    else:
        # Meteo chiaro
        weather = carla.WeatherParameters.ClearNoon
        world.set_weather(weather)
    return ego_vehicle

def scenario_vehicle(spawner):
    print(f"[SCENARIO] Spawning scenario 1")

    target_vehicle = spawner.spawn_vehicle(
        model=config.TARGET_VEHICLE_MODEL,
        spawn_point=config.TARGET_SPAWN_TRANSFORM,
        autopilot=False
    )
    if not target_vehicle:
        print("ERROR: car not spawned.")

    def start_movement():
        target_vehicle.set_target_velocity(config.TARGET_VELOCITY)
        print("[SCENARIO] Car started moving")

    timer = threading.Timer(4.0, start_movement)
    timer.start()

def scenario_bicycle(spawner):
    print(f"[SCENARIO] Spawning scenario 2")

    bicycle = spawner.spawn_vehicle(
        model=config.BICYCLE_MODEL,
        spawn_point=config.BICYCLE_SPAWN_TRANSFORM,
        autopilot=False
    )
    if not bicycle:
        print("ERROR: target_vehicle not spawned.")

    def start_movement():
        bicycle.set_target_velocity(config.BICYCLE_VELOCITY)
        print("[SCENARIO] Bike started moving")

    timer = threading.Timer(4.0, start_movement)
    timer.start()

def scenario_pedestrian_adult(spawner):
    print(f"[SCENARIO] Spawning scenario 3")

    pedestrian = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_MODEL,
        spawn_point=config.PEDESTRIAN_SPAWN_TRANSFORM,
        destination=config.PEDESTRIAN_DESTINATION,
        speed=config.PEDESTRIAN_WALK_SPEED
    )

    if not pedestrian:
        print("ERROR: pedestrian not spawned.")

def scenario_pedestrian_child( spawner):
    print(f"[SCENARIO] Spawning scenario 4")

    pedestrian = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_CHILD_MODEL,
        spawn_point=config.PEDESTRIAN_SPAWN_TRANSFORM,
        destination=config.PEDESTRIAN_DESTINATION,
        speed=config.PEDESTRIAN_CHILD_WALK_SPEED
    )

    if not pedestrian:
        print("ERROR: pedestrian not spawned.")





