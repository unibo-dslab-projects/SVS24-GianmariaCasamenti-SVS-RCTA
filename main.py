import carla
import time
import cv2
import pygame

from carla_bridge.carla_manager import CarlaManager
from carla_bridge.spawner import Spawner
from carla_bridge.sensor_manager import SensorManager
from scenarios.parking_lot_scenario import (setup_rcta_base_scenario,
                                            scenario_bicycle)
from controller.keyboard_controller import KeyboardController

from rcta_system.rcta_callbacks import sync_and_callback


def main():
    pygame.init()
    pygame.display.set_mode((200, 100))
    pygame.display.set_caption('CARLA Controller')
    clock = pygame.time.Clock()

    try:
        with CarlaManager() as manager:
            print("MAIN [Initializing scenario]")

            # Spawn ego vehicle and scenario
            spawner = Spawner(manager.world, manager.actor_list)
            ego_vehicle = setup_rcta_base_scenario(manager.world, spawner, True, False)

            if not ego_vehicle:
                print("MAIN [ERROR: Could not spawn ego vehicle]")
                return None

            print("MAIN [Initializing controller]")
            controller = KeyboardController()

            print("MAIN [Initializing spectator camera]")
            spectator = manager.world.get_spectator()

            print("MAIN [Initializing Sensor manager and cameras]")
            sensor_manager = SensorManager(manager.world, manager.actor_list)
            (r_rgb, r_depth, l_rgb, l_depth, ri_rgb, ri_depth) = sensor_manager.setup_rcta_cameras(ego_vehicle)

            print("MAIN [Registering RCTA callbacks]")
            # REAR zone callbacks
            r_rgb.listen(lambda image: sync_and_callback("rear", "rgb", image))
            r_depth.listen(lambda image: sync_and_callback("rear", "depth", image))
            print("MAIN [REAR callbacks registered]")

            # LEFT zone callbacks
            l_rgb.listen(lambda image: sync_and_callback("left", "rgb", image))
            l_depth.listen(lambda image: sync_and_callback("left", "depth", image))
            print("MAIN [LEFT callbacks registered]")

            # RIGHT zone callbacks
            ri_rgb.listen(lambda image: sync_and_callback("right", "rgb", image))
            ri_depth.listen(lambda image: sync_and_callback("right", "depth", image))
            print("MAIN [RIGHT callbacks registered]")

            # Spawn scenario actors
            # scenario_vehicle(spawner)
            scenario_bicycle(spawner)
            # scenario_pedestrian_adult(spawner)
            # scenario_pedestrian_child(spawner)

            time.sleep(2.0)

            print("MAIN [Starting loop]")
            running = True

            while running:
                # Handle pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Get keyboard input and apply control
                keys = pygame.key.get_pressed()
                control = controller.parse_input(keys)
                ego_vehicle.apply_control(control)

                # Update spectator camera position
                ego_transform = ego_vehicle.get_transform()
                spectator_location = (ego_transform.location +
                                      ego_transform.get_forward_vector() * (-10) +
                                      carla.Location(z=5))
                spectator_rotation = carla.Rotation(pitch=-30,
                                                    yaw=ego_transform.rotation.yaw)
                spectator.set_transform(carla.Transform(spectator_location,
                                                        spectator_rotation))

                pygame.display.flip()

                # 30 FPS
                clock.tick(30)

    except KeyboardInterrupt:
        print("\nMAIN [Script interrupted from keyboard]")
    except Exception as e:
        print(f"\nMAIN [Exception: {e}]")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        cv2.destroyAllWindows()
        print("MAIN [Cleanup completed]")


if __name__ == '__main__':
    main()