import carla
import random
import config


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

    # Spawn blocking vehicles se richiesto
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


def scenario_vehicle(world, spawner, blocking_cars, bad_weather):
    print(f"[SCENARIO] Spawning scenario 1")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    target_vehicle = spawner.spawn_vehicle(
        model=config.TARGET_VEHICLE_MODEL,
        spawn_point=config.TARGET_SPAWN_TRANSFORM,
        autopilot=False
    )
    if not target_vehicle:
        print("ERROR: bicycle not spawned.")
        return ego_vehicle

    target_vehicle.set_target_velocity(config.TARGET_VELOCITY)
    return ego_vehicle

def scenario_bicycle(world, spawner, blocking_cars, bad_weather):
    print(f"[SCENARIO] Spawning scenario 2")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    bicycle = spawner.spawn_vehicle(
        model=config.BICYCLE_MODEL,
        spawn_point=config.BICYCLE_SPAWN_TRANSFORM,
        autopilot=False
    )
    if not bicycle:
        print("ERROR: target_vehicle not spawned.")
        return ego_vehicle

    bicycle.set_target_velocity(config.BICYCLE_VELOCITY)
    return ego_vehicle

def scenario_pedestrian_adult(world, spawner, blocking_cars, bad_weather):
    print(f"[SCENARIO] Spawning scenario 3")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    pedestrian = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_MODEL,
        spawn_point=config.PEDESTRIAN_SPAWN_TRANSFORM,
        destination=config.PEDESTRIAN_DESTINATION,
        speed=config.PEDESTRIAN_WALK_SPEED
    )

    if not pedestrian:
        print("ERROR: pedestrian not spawned.")
        return ego_vehicle

    return ego_vehicle


def scenario_pedestrian_child(world, spawner, blocking_cars, bad_weather):
    print(f"[SCENARIO] Spawning scenario 4")

    ego_vehicle = setup_rcta_base_scenario(world, spawner, blocking_cars, bad_weather)
    if not ego_vehicle:
        return None

    pedestrian = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_CHILD_MODEL,
        spawn_point=config.PEDESTRIAN_SPAWN_TRANSFORM,
        destination=config.PEDESTRIAN_DESTINATION,
        speed=config.PEDESTRIAN_CHILD_WALK_SPEED
    )

    if not pedestrian:
        print("ERROR: pedestrian not spawned.")
        return ego_vehicle

    return ego_vehicle


