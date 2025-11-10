import carla
import config

class CarlaManager:
    """Manages the connection to the CARLA server and actor cleanup"""
    def __init__(self, map_name = config.MAP_NAME):
        self.client = None
        self.world = None
        self.actor_list = []
        self.map_name = map_name

    def __enter__(self):
        """Connection to CARLA server and gets the world"""
        print("CARLA_MANAGER [Connecting to CARLA]")
        self.client = carla.Client(config.HOST, config.PORT)
        self.client.set_timeout(config.TIMEOUT)

        print(f"CARLA_MANAGER [Loading map: {self.map_name}]")
        self.world = self.client.load_world(self.map_name)

        print("CARLA_MANAGER [Applying synchronous mode settings]")
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 0.05  # 20 FPS (1 / 0.05)
        self.world.apply_settings(settings)

        self.world.tick()
        print("CARLA_MANAGER [Settings applied and initial tick done]")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Destroys all tracked actors to clean up the simulation"""
        print("CARLA_MANAGER [Cleaning up actors]")
        if self.world:
            try:
                settings = self.world.get_settings()
                settings.synchronous_mode = False
                settings.fixed_delta_seconds = None
                self.world.apply_settings(settings)
                print("CARLA_MANAGER [Resetted to asynchronous mode]")
            except Exception as e:
                print(f"CARLA_MANAGER [Could not reset settings: {e}]")

        for actor in self.actor_list:
            if actor.is_alive:
                print(f"CARLA_MANAGER [Destroying actor {actor.type_id}]")
                actor.destroy()