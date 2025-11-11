import carla
import random
import config
from config import EGO_VEHICLE_MODEL


def setup_static_scenario(world, spawner):
    print("Creating static parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model=EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
        )
    except AttributeError as e:
        print(f"error: {e}")
        return None

    if not ego_vehicle:
        print(f"Failure to spawn ego_vehicle for the scenario")
        return None

    print(f"Vehicle spawned in position: {config.EGO_SPAWN_TRANSFORM.location}")

    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
        if blocker:
            spawned_blockers += 1

    print(f"Spawned {spawned_blockers} blocker vehicles")
    return ego_vehicle


def setup_parking_scenario(world, spawner):
    print("Creating static parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model=EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
        )
    except AttributeError as e:
        print(f"error: {e}")
        return None, None

    if not ego_vehicle:
        print(f"Failure to spawn ego_vehicle for the scenario")
        return None, None

    print(f"Vehicle spawned in position: {config.EGO_SPAWN_TRANSFORM.location}")

    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    target_vehicle = spawner.spawn_vehicle(
        model=config.TARGET_VEHICLE_MODEL,
        spawn_point=config.TARGET_SPAWN_TRANSFORM,
        autopilot=False
    )
    if not target_vehicle:
        print("ERROR: target_vehicle not spawned.")
        return ego_vehicle, None

    target_vehicle.set_target_velocity(config.TARGET_VELOCITY)
    print(f"Vehicle spawned in position: {config.TARGET_SPAWN_TRANSFORM.location}")

    return ego_vehicle, target_vehicle


def setup_parking_scenario_with_pedestrian(world, spawner):
    print("Creating static parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model=EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
        )
    except AttributeError as e:
        print(f"error: {e}")
        return None

    if not ego_vehicle:
        print(f"Failure to spawn ego_vehicle for the scenario")
        return None

    print(f"Vehicle spawned in position: {config.EGO_SPAWN_TRANSFORM.location}")

    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    print("Spawning pedestrian in scenario...")
    pedestrian, pedestrian_controller = spawner.spawn_pedestrian(
        model=config.PEDESTRIAN_MODEL,
        spawn_point=config.PEDESTRIAN_SPAWN_TRANSFORM,
        destination=config.PEDESTRIAN_DESTINATION,
        speed=config.PEDESTRIAN_WALK_SPEED
    )
    if not pedestrian:
        print("ERRORE: pedestrian spawn failed")

    return ego_vehicle


def setup_complex_scenario(world, spawner):
    print("Creating COMPLEX parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model=config.EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
        )
    except AttributeError as e:
        print(f"error: {e}")
        return None

    if not ego_vehicle:
        print(f"Failure to spawn ego_vehicle for the scenario")
        return None
    print(f"Ego vehicle spawned in position: {config.EGO_SPAWN_TRANSFORM.location}")

    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    spawned_pedestrians = 0
    print("Spawning pedestrians in complex scenario...")
    for ped_data in config.PEDESTRIAN_ACTORS:
        pedestrian, controller = spawner.spawn_pedestrian(
            model=ped_data['model'],
            spawn_point=ped_data['spawn'],
            destination=ped_data['dest'],
            speed=ped_data['speed']
        )
        if pedestrian:
            spawned_pedestrians += 1
        else:
            print(f"ERROR: Failed to spawn pedestrian {ped_data['model']}")
    print(f"Spawned {spawned_pedestrians} pedestrians")

    spawned_bicycles = 0
    print("Spawning bicycles in complex scenario...")
    for bike_data in config.BICYCLE_ACTORS:
        bicycle = spawner.spawn_vehicle(
            model=bike_data['model'],
            spawn_point=bike_data['spawn'],
            autopilot=False
        )
        if bicycle:
            bicycle.set_target_velocity(bike_data['velocity'])
            spawned_bicycles += 1
        else:
            print(f"ERROR: Failed to spawn bicycle {bike_data['model']}")
    print(f"Spawned {spawned_bicycles} bicycles")

    return ego_vehicle


def setup_vehicle_crossing_scenario(world, spawner):
    print("Creating VEHICLE CROSSING scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model=config.EGO_VEHICLE_MODEL,
            spawn_point=config.EGO_SPAWN_TRANSFORM,
            autopilot=False
        )
    except AttributeError as e:
        print(f"error: {e}")
        return None

    if not ego_vehicle:
        print(f"Failure to spawn ego_vehicle for the scenario")
        return None
    print(f"Ego vehicle spawned in position: {config.EGO_SPAWN_TRANSFORM.location}")

    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(model=model, spawn_point=transform, autopilot=False)
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    spawned_vehicles = 0
    print("Spawning crossing vehicles in scenario...")
    for vehicle_data in config.CROSSING_VEHICLE_ACTORS:
        vehicle = spawner.spawn_vehicle(
            model=vehicle_data['model'],
            spawn_point=vehicle_data['spawn'],
            autopilot=False
        )
        if vehicle:
            vehicle.set_target_velocity(vehicle_data['velocity'])
            spawned_vehicles += 1
        else:
            print(f"ERROR: Failed to spawn vehicle {vehicle_data['model']}")
    print(f"Spawned {spawned_vehicles} crossing vehicles")

    return ego_vehicle