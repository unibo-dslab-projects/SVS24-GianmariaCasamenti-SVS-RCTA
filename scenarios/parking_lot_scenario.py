import carla
import random
import config
from config import EGO_VEHICLE_MODEL


def setup_static_scenario(world, spawner):
    """
    Creates a static parking lot scenario for RCTA test.
    Spawns ego_vehicle in a parking lot and adds several vehicles (static) around it.

    :param world: carla's world object
    :param spawner: Object to spawn actors
    :return: The spawned actor ego_vehicle, or None if it fails
    """
    print("Creating static parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model= EGO_VEHICLE_MODEL,
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

    #spawning vehicles around
    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model  = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(
            model=model,
            spawn_point=transform,
            autopilot=False
        )
        if blocker:
            spawned_blockers += 1

    print(f"Spawned {spawned_blockers} blocker vehicles")
    return ego_vehicle


def setup_parking_scenario(world, spawner):
    """
    Creates a static parking lot scenario for RCTA test.
    Spawns ego_vehicle in a parking lot and adds several vehicles (static) around it.
    Spawns also a target vehicle that moves.

    :param world: carla's world object
    :param spawner: Object to spawn actors
    :return: Tuple(ego_vehicle, target_vehicle), or (None,None) if it fails
    """
    print("Creating static parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model= EGO_VEHICLE_MODEL,
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

    #spawning vehicles around
    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model  = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(
            model=model,
            spawn_point=transform,
            autopilot=False
        )
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    #spawning target vehicle
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
    """
    Creates a static parking lot scenario for RCTA test.
    Spawns ego_vehicle in a parking lot and adds several vehicles (static) around it.
    Spawns also a target vehicle that moves.

    :param world: carla's world object
    :param spawner: Object to spawn actors
    :return: ego_vehicle or None
    """
    print("Creating static parking lot scenario")

    try:
        ego_vehicle = spawner.spawn_vehicle(
            model= EGO_VEHICLE_MODEL,
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

    #spawning vehicles around
    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model  = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(
            model=model,
            spawn_point=transform,
            autopilot=False
        )
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
    """
    Crea uno scenario di parcheggio complesso per il test RCTA.
    Spawna ego_vehicle, veicoli statici, 3 pedoni e 2 biciclette.

    :param world: carla's world object
    :param spawner: Object to spawn actors
    :return: ego_vehicle or None
    """
    print("Creating COMPLEX parking lot scenario")

    # 1. Spawn Ego Vehicle
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

    # Spawn Blocker Vehicles
    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(
            model=model,
            spawn_point=transform,
            autopilot=False
        )
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    # Spawn Pedestrians
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

    # 4. Spawn Bicycles (dal config)
    spawned_bicycles = 0
    print("Spawning bicycles in complex scenario...")
    for bike_data in config.BICYCLE_ACTORS:
        bicycle = spawner.spawn_vehicle(
            model=bike_data['model'],
            spawn_point=bike_data['spawn'],
            autopilot=False
        )
        if bicycle:
            # Imposta la velocità costante, come per il target_vehicle
            bicycle.set_target_velocity(bike_data['velocity'])
            spawned_bicycles += 1
        else:
            print(f"ERROR: Failed to spawn bicycle {bike_data['model']}")
    print(f"Spawned {spawned_bicycles} bicycles")

    return ego_vehicle

def setup_vehicle_crossing_scenario(world, spawner):
    """
    Crea uno scenario di parcheggio con traffico incrociato di soli veicoli.
    Spawna ego_vehicle, veicoli statici e 4 veicoli in movimento.

    :param world: carla's world object
    :param spawner: Object to spawn actors
    :return: ego_vehicle or None
    """
    print("Creating VEHICLE CROSSING scenario")

    # 1. Spawn Ego Vehicle
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

    # 2. Spawn Blocker Vehicles (statici)
    spawned_blockers = 0
    for transform in config.BLOCKING_VEHICLE_TRANSFORMS:
        model = random.choice(config.BLOCKING_VEHICLE_MODELS)
        blocker = spawner.spawn_vehicle(
            model=model,
            spawn_point=transform,
            autopilot=False
        )
        if blocker:
            spawned_blockers += 1
    print(f"Spawned {spawned_blockers} blocker vehicles")

    # 3. Spawn Crossing Vehicles (dal config)
    spawned_vehicles = 0
    print("Spawning crossing vehicles in scenario...")
    for vehicle_data in config.CROSSING_VEHICLE_ACTORS:
        vehicle = spawner.spawn_vehicle(
            model=vehicle_data['model'],
            spawn_point=vehicle_data['spawn'],
            autopilot=False
        )
        if vehicle:
            # Imposta la velocità costante
            vehicle.set_target_velocity(vehicle_data['velocity'])
            spawned_vehicles += 1
        else:
            print(f"ERROR: Failed to spawn vehicle {vehicle_data['model']}")
    print(f"Spawned {spawned_vehicles} crossing vehicles")

    return ego_vehicle
