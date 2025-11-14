import carla
import random
import config
from config import EGO_VEHICLE_MODEL


def setup_rcta_base_scenario(world, spawner, blocking_cars=True, bad_weather=False):
    print(f"[RCTA BASE] Creating scenario - Blocking Cars: {blocking_cars}, Bad Weather: {bad_weather}")

    # Spawn ego vehicle
    try:
        ego_vehicle = spawner.spawn_vehicle(
            model=EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
        )
    except AttributeError as e:
        print(f"[ERROR] {e}")
        return None

    if not ego_vehicle:
        print(f"[ERROR] Failed to spawn ego vehicle")
        return None

    print(f"[RCTA BASE] Ego vehicle spawned at: {config.EGO_SPAWN_TRANSFORM.location}")

    # Spawn blocking vehicles se richiesto
    spawned_blockers = 0
    if blocking_cars:
        for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
            model = random.choice(config.BLOCKING_VEHICLE_MODELS)
            blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
            if blocker:
                spawned_blockers += 1
        print(f"[RCTA BASE] Spawned {spawned_blockers} blocking vehicles")
    else:
        print(f"[RCTA BASE] No blocking vehicles (open scenario)")

    # Configura meteo avverso se richiesto
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
        print(f"[RCTA BASE] Bad weather conditions applied")
    else:
        # Meteo chiaro
        weather = carla.WeatherParameters.ClearNoon
        world.set_weather(weather)
        print(f"[RCTA BASE] Clear weather conditions")

    return ego_vehicle


# SCENARIO 1: VEHICLE CROSSING (20 km/h)
def setup_scenario_vehicle_20kmh(world, spawner, blocking_cars=True, bad_weather=False):
    print(f"[SCENARIO 1] VEHICLE CROSSING - 20 km/h")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    spawn_transform = config.TARGET_SPAWN_TRANSFORM_VEHICLE
    velocity = config.TARGET_VELOCITY_20

    target_vehicle = spawner.spawn_vehicle(
        model=config.TARGET_VEHICLE_MODEL,
        spawn_point=spawn_transform,
        autopilot=False
    )

    if not target_vehicle:
        print("[ERROR] Failed to spawn target vehicle")
        return ego_vehicle

    target_vehicle.set_target_velocity(velocity)
    return ego_vehicle


# SCENARIO 2: BICYCLE CROSSING (10 km/h e 15 km/h)
def setup_scenario_bicycle(world, spawner, speed_kmh=10, blocking_cars=True, bad_weather=False, ):
    print(f"[SCENARIO 2] BICYCLE CROSSING - {speed_kmh} km/h")
    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    spawn_transform = config.BICYCLE_SPAWN_TRANSFORM
    velocity = config.BICYCLE_VELOCITY_10 if speed_kmh == 10 else config.BICYCLE_VELOCITY_15


    bicycle = spawner.spawn_vehicle(
        model=config.BICYCLE_MODEL,
        spawn_point=spawn_transform,
        autopilot=False
    )

    if not bicycle:
        print("[ERROR] Failed to spawn bicycle")
        return ego_vehicle

    bicycle.set_target_velocity(velocity)
    return ego_vehicle


# SCENARIO 3: PEDESTRIAN ADULT (5 km/h)
def setup_scenario_pedestrian_adult(world, spawner, blocking_cars=True, bad_weather=False):
    print(f"[SCENARIO 3] PEDESTRIAN ADULT - 5 km/h")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    spawn_transform = config.PEDESTRIAN_ADULT_SPAWN_TRANSFORM
    destination = config.PEDESTRIAN_ADULT_DESTINATION

    pedestrian, controller = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_ADULT_MODEL,
        spawn_point=spawn_transform,
        destination=destination,
        speed=config.PEDESTRIAN_ADULT_SPEED
    )

    if not pedestrian:
        print("[ERROR] Failed to spawn adult pedestrian")
        return ego_vehicle

    return ego_vehicle


# SCENARIO 4: PEDESTRIAN CHILD (5 km/h e 10 km/h)
def setup_scenario_pedestrian_child(world, spawner, speed_kmh=5, blocking_cars=True, bad_weather=False):
    print(f"[SCENARIO 4] PEDESTRIAN CHILD - {speed_kmh} km/h")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    # Velocità del bambino (5 km/h = 1.39 m/s, 10 km/h = 2.78 m/s)
    speed_ms = speed_kmh / 3.6


    spawn_transform = config.PEDESTRIAN_CHILD_SPAWN_TRANSFORM
    destination = config.PEDESTRIAN_CHILD_DESTINATION

    pedestrian, controller = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_CHILD_MODEL,
        spawn_point=spawn_transform,
        destination=destination,
        speed=speed_ms
    )

    if not pedestrian:
        print("[ERROR] Failed to spawn child pedestrian")
        return ego_vehicle

    return ego_vehicle


# SCENARIO 5: COMPLEX MULTI-TARGET CROSSING
def setup_scenario_complex_multi_target(world, spawner, blocking_cars=True, bad_weather=False):
    return []


