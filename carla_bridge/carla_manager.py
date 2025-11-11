import carla
import config


class CarlaManager:
    def __init__(self, map_name=config.MAP_NAME, use_async_mode=config.ASYNC_MODE):
        self.client = None
        self.world = None
        self.actor_list = []
        self.map_name = map_name
        self.use_async_mode = use_async_mode

    def __enter__(self):
        print("CARLA_MANAGER [Connecting to CARLA]")
        self.client = carla.Client(config.HOST, config.PORT)
        self.client.set_timeout(config.TIMEOUT)

        print(f"CARLA_MANAGER [Loading map: {self.map_name}]")
        self.world = self.client.load_world(self.map_name)

        if self.use_async_mode:
            print("CARLA_MANAGER [Using ASYNCHRONOUS mode]")
            settings = self.world.get_settings()
            settings.synchronous_mode = False
            settings.fixed_delta_seconds = None
            self.world.apply_settings(settings)
            print("CARLA_MANAGER [Asynchronous mode enabled]")
        else:
            print("CARLA_MANAGER [Applying synchronous mode settings]")
            settings = self.world.get_settings()
            settings.synchronous_mode = True
            settings.fixed_delta_seconds = config.DELTA_SECONDS
            self.world.apply_settings(settings)

            self.world.tick()
            print("CARLA_MANAGER [Synchronous mode enabled and initial tick done]")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
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