import carla
import time
import cv2
import pygame
import config

from carla_bridge.carla_manager import CarlaManager
from carla_bridge.spawner import Spawner
from carla_bridge.sensor_manager import SensorManager
from scenarios.parking_lot_scenario import (scenario_vehicle,
                                            scenario_bicycle,
                                            scenario_pedestrian_adult,
                                            scenario_pedestrian_child,
                                            setup_rcta_base_scenario)

from rcta_system.rcta_pipeline import RCTAPipeline
from hmi.mqtt_publisher import MqttPublisher
from controller.keyboard_controller import KeyboardController


def draw_fused_detections(image, pipeline):
    RED = (0, 0, 255)
    YELLOW = (0,255,255)
    GREEN = (0, 255, 0)

    # Get tracked objects from pipeline
    for track_id, state in pipeline.tracked_objects.items():
        # For visualization, we need to access the last processed objects
        # Since we don't store full bbox info in tracked_objects,
        # we'll draw a simplified version
        pass

    # Alternative: Draw current frame objects
    # This would require storing last processed objects in pipeline
    # For now, we keep it simple and just show the frame
    return image


def main():
    pygame.init()
    pygame.display.set_mode((200, 100))
    pygame.display.set_caption('Input')

    clock = pygame.time.Clock()


    try:
        with CarlaManager() as manager:
            print("MAIN [Initializing scenario]")
            spawner = Spawner(manager.world, manager.actor_list)
            ego_vehicle = setup_rcta_base_scenario(manager.world, spawner, True, False)
            if not ego_vehicle:
                return None

            print("MAIN [Initializing Decision Maker and HMI Publisher]")
            mqtt_publisher = MqttPublisher()
            mqtt_publisher.connect()

            print("MAIN [Initializing 3 independent pipelines ]")
            pipeline_rear = RCTAPipeline("rear", mqtt_publisher)
            pipeline_left = RCTAPipeline("left", mqtt_publisher)
            pipeline_right = RCTAPipeline("right", mqtt_publisher)

            print("MAIN [Initializing Sensor manager and cameras]")
            sensor_manager = SensorManager(manager.world, manager.actor_list)
            (r_rgb, r_depth, l_rgb, l_depth, ri_rgb, ri_depth) = sensor_manager.setup_rcta_cameras(ego_vehicle)

            print("MAIN [Registering camera callbacks to pipelines]")
            pipeline_rear.set_camera_callbacks(r_rgb, r_depth)
            pipeline_left.set_camera_callbacks(l_rgb, l_depth)
            pipeline_right.set_camera_callbacks(ri_rgb, ri_depth)

            print("MAIN [Starting pipeline threads]")
            pipeline_rear.start()
            pipeline_left.start()
            pipeline_right.start()

            print("MAIN [Initializing controller]")
            controller = KeyboardController()

            print("MAIN [Initializing spectator]")
            spectator = manager.world.get_spectator()

            #scenario_vehicle(spawner)
            scenario_bicycle(spawner)
            #scenario_pedestrian_adult(spawner)
            #scenario_pedestrian_child(spawner)

            time.sleep(1.0)
            running = True
            frame_count = 0
            start_time = time.time()
            while running:
                manager.world.tick()

                ego_transform = ego_vehicle.get_transform()
                spectator_location = (ego_transform.location +
                                      ego_transform.get_forward_vector() * (-10) +
                                      carla.Location(z=5))
                spectator_rotation = carla.Rotation(pitch=-30, yaw=ego_transform.rotation.yaw)
                spectator.set_transform(carla.Transform(spectator_location, spectator_rotation))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                keys = pygame.key.get_pressed()
                control = controller.parse_input(keys)
                ego_vehicle.apply_control(control)

                is_reversing =True
            
                # FPS counter
                frame_count += 1
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"MAIN [FPS: {fps:.1f}]")

                pygame.display.flip()
                clock.tick(config.TARGET_FPS)

    except KeyboardInterrupt:
        print("\nMAIN [Script interrupted from keyboard]")
    except Exception as e:
        print(f"\nMAIN [Exception: {e}]")
        import traceback
        traceback.print_exc()
    finally:
        if 'mqtt_publisher' in locals():
            mqtt_publisher.disconnect()
        pygame.quit()
        cv2.destroyAllWindows()
        print("MAIN [All windows closed]")


if __name__ == '__main__':
    main()