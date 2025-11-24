import carla
import config


class CarlaManager:
    """
    Manages CARLA connection in pure async mode (like notebook).
    No synchronization settings applied - CARLA runs freely.
    """

    def __init__(self, map_name=config.MAP_NAME):
        self.client = None
        self.world = None
        self.actor_list = []
        self.map_name = map_name

    def __enter__(self):
        print("CARLA_MANAGER [Connecting to CARLA]")
        self.client = carla.Client(config.HOST, config.PORT)
        self.client.set_timeout(config.TIMEOUT)

        print(f"CARLA_MANAGER [Loading map: {self.map_name}]")
        self.world = self.client.load_world(self.map_name)

        # Pure async mode - no synchronization (like notebook)
        print("CARLA_MANAGER [Running in asynchronous mode (like notebook)]")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("CARLA_MANAGER [Cleaning up actors]")

        for actor in self.actor_list:
            if actor.is_alive:
                print(f"CARLA_MANAGER [Destroying actor {actor.type_id}]")
                actor.destroy()