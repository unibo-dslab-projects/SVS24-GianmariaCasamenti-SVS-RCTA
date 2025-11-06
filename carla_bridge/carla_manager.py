import carla
import config

class CarlaManager:
    """Manages the connection to the CARLA server and actor cleanup"""
    def __init__(self):
        self.client = None
        self.world = None
        self.actor_list = []

    def __enter__(self):
        """Connection to CARLA server and gets the world"""
        print("CARLA_MANAGER [Connecting to CARLA]")
        self.client = carla.Client(config.HOST, config.PORT)
        self.client.set_timeout(config.TIMEOUT)
        self.world = self.client.get_world()
        print("CARLA_MANAGER [Connection successfully]")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Destroys all tracked actors to clean up the simulation"""
        print("CARLA_MANAGER [Cleaning up actors]")
        for actor in self.actor_list:
            if actor.is_alive:
                print(f"CARLA_MANAGER [Destroying actor {actor.type_id}]")
                actor.destroy()