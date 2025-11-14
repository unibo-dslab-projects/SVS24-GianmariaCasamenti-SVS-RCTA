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
                                            scenario_pedestrian_child)
from rcta_system.perception import RctaPerception
from rcta_system.decision_making import DecisionMaker
from hmi.mqtt_publisher import MqttPublisher
from controller.keyboard_controller import KeyboardController


def draw_fused_detections(image, perception_data):
    RED = (0, 0, 255)
    YELLOW = (0,255,255)
    GREEN = (0, 255, 0)

    sector_ttc = perception_data['ttc']
    sector_dist = perception_data['dist']

    for det in perception_data['objects']:
        bbox = [int(c) for c in det['bbox']]
        dist = det.get('dist', float('inf'))
        obj_ttc = det.get('ttc_obj', float('inf'))
        id = det.get('id')

        if obj_ttc < config.TTC_THRESHOLD:
            color = RED
        elif dist < config.DIST_THRESHOLD:
            color = YELLOW
        else:
            color = GREEN

        dist_str = f"{dist:.1f}m"
        ttc_str = f"{obj_ttc:.1f}s" if obj_ttc != float('inf') else "---"
        label = f"ID:{id} {det['class']} {dist_str} {ttc_str}"

        cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
        cv2.putText(image, label, (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    #info_color = RED if (sector_ttc < config.TTC_THRESHOLD or sector_dist < 3.0) else GREEN
    #info_text = f"MIN DIST: {sector_dist:.1f}m | MIN TTC: {sector_ttc:.1f}s"
    #cv2.putText(image, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 2)


def main():
    pygame.init()
    pygame.display.set_mode((200, 100))
    pygame.display.set_caption('Input')

    clock = pygame.time.Clock()


    try:
        with CarlaManager() as manager:
            print("MAIN [Initializing scenario]")
            spawner = Spawner(manager.world, manager.actor_list)
            #ego_vehicle = scenario_vehicle(manager.world,spawner, True, False)
            #ego_vehicle = scenario_bicycle(manager.world,spawner, True, False)
            ego_vehicle = scenario_pedestrian_adult(manager.world,spawner, True, False)
            #ego_vehicle = scenario_pedestrian_child(manager.world,spawner, True, False)



            print("MAIN [Initializing perception and Sensor manager]")
            perception_system = RctaPerception()
            sensor_manager = SensorManager(manager.world, manager.actor_list)

            print("MAIN [Initializing Decision Maker and HMI Publisher]")
            decision_maker = DecisionMaker()
            mqtt_publisher = MqttPublisher()
            mqtt_publisher.connect()

            print("MAIN [Initializing controller]")
            controller = KeyboardController()

            print("MAIN [Initializing cameras and callback]")
            (r_rgb, r_depth, l_rgb, l_depth, ri_rgb, ri_depth) = sensor_manager.setup_rcta_cameras(ego_vehicle)

            r_rgb.listen(perception_system.rear_rgb_callback)
            r_depth.listen(perception_system.rear_depth_callback)
            l_rgb.listen(perception_system.left_rgb_callback)
            l_depth.listen(perception_system.left_depth_callback)
            ri_rgb.listen(perception_system.right_rgb_callback)
            ri_depth.listen(perception_system.right_depth_callback)

            print("MAIN [Initializing spectator]")
            spectator = manager.world.get_spectator()

            time.sleep(1.0)
            running = True
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

                is_reversing = control.reverse

                all_perception_data = perception_system.get_all_perception_data(True)
                dangerous_objects = decision_maker.evaluate(all_perception_data, is_reversing)
                mqtt_publisher.publish_status(dangerous_objects)

                if config.DEBUG:
                    if perception_system.display_frame_rear is not None:
                        frame = perception_system.display_frame_rear
                        data = perception_system.perception_data['rear']
                        draw_fused_detections(frame, data)
                        cv2.imshow("REAR RGBD camera", frame)

                    if perception_system.display_frame_left is not None:
                        frame = perception_system.display_frame_left
                        data = perception_system.perception_data['left']
                        draw_fused_detections(frame, data)
                        cv2.imshow("LEFT RGBD camera", frame)

                    if perception_system.display_frame_right is not None:
                        frame = perception_system.display_frame_right
                        data = perception_system.perception_data['right']
                        draw_fused_detections(frame, data)
                        cv2.imshow("RIGHT RGBD camera", frame)

                cv2.waitKey(1)
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