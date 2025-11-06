import carla
import random

class Spawner:
    """Handles the generation of actors"""
    def __init__(self, world, actor_list):
        self.world = world
        self.actor_list = actor_list
        self.blueprint_library = self.world.get_blueprint_library()

    def spawn_vehicle(self, model, spawn_point=None, autopilot=False):
        """Spawn veichles according to the model at a specific random point
        Returns:
            Carla.Actor: spawned veichles actor, or None on failure.
        """
        vehicle_bp = self.blueprint_library.filter(model)[0]

        if spawn_point is None:
            spawn_points = self.world.get_map().get_spawn_points()
            if not spawn_points:
                print("SPAWNER [Error: no spawn points]")
                return None
            spawn_point = random.choice(spawn_points)

        vehicle = self.world.try_spawn_actor(vehicle_bp, spawn_point)

        if vehicle:
            print(f"SPAWNER [Spawn succeeded, model: {model}]")
            vehicle.set_autopilot(autopilot)
            self.actor_list.append(vehicle)
        else:
            print(f"SPAWNER [ERROR: Spawn failed, model: {model}]")
        return vehicle

    def spawn_pedestrian(self, model, spawn_point, destination, speed):
        """
        Creates a pedestrian and set it to walk.
        """
        walker_bp = self.blueprint_library.filter(model)[0]
        if walker_bp.has_attribute('is_invincible'):
            walker_bp.set_attribute('is_invincible', 'false')

        pedestrian = self.world.try_spawn_actor(walker_bp, spawn_point)

        if not pedestrian:
            print(f"SPAWNER [ERROR: spawned failed: {model}]")
            return None, None

        print(f"SPAWNER [Spawned with successfully: {model}]")
        self.actor_list.append(pedestrian)

        walker_controller_bp = self.blueprint_library.find('controller.ai.walker')
        controller = self.world.spawn_actor(
            walker_controller_bp,
            carla.Transform(),
            attach_to=pedestrian
        )
        if not controller:
            print(f"SPAWNER [ERROR: controller spawn AI failed]")
            pedestrian.destroy()
            self.actor_list.remove(pedestrian)
            return None, None

        self.actor_list.append(controller)

        controller.start()
        controller.go_to_location(destination)
        controller.set_max_speed(speed)
        print(f"SPAWNER [AI pedestrian walks to {destination} with {speed} m/s]")

        return pedestrian, controller