import carla
import time
import cv2
import pygame
import config

from carla_bridge.carla_manager import CarlaManager
from carla_bridge.spawner import Spawner
from carla_bridge.sensor_manager import SensorManager

from scenarios.parking_lot_scenario import setup_parking_scenario, setup_parking_scenario_with_pedestrian

from rcta_system.perception import RctaPerception
from rcta_system.decision_making import DecisionMaker

from hmi.mqtt_publisher import MqttPublisher

from controller.keyboard_controller import KeyboardController

def draw_detections(image, detections):
    """
    draws bounding box and image tag.
    modify image "in-place"
    """
    for det in detections:
        bbox = det['bbox']
        label = f"{det['class']} {det['confidence']:.2f}"

        cv2.rectangle(image, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(image, label, (bbox[0], bbox[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)


def draw_depth_info(image, distance, ttc, is_alert):
    """
    Disegna le informazioni di Distanza e TTC sull'immagine di profondità.
    """
    # Colore del testo: Rosso se in allarme, Verde altrimenti
    color = (0, 0, 255) if is_alert else (0, 255, 0)

    dist_text = f"Dist: {distance:.2f} m"
    ttc_text = f"TTC: {ttc:.2f} s"

    # Posiziona il testo
    cv2.putText(image, dist_text, (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
    cv2.putText(image, ttc_text, (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

def main():
    pygame.init()
    # Crea una piccola finestra solo per catturare l'input
    pygame.display.set_mode((200, 100))
    pygame.display.set_caption('Controller Input')

    try:
        with CarlaManager() as manager:
            print(f"MAIN [loading: {config.MAP_NAME}]")
            manager.client.load_world(config.MAP_NAME)
            manager.world = manager.client.get_world()
            manager.world.tick()

            print("MAIN [Initializing scenario]")
            spawner = Spawner(manager.world, manager.actor_list)
            # ego_vehicle, target_vehicle = setup_parking_scenario(manager.world, spawner)
            ego_vehicle = setup_parking_scenario_with_pedestrian(manager.world, spawner)

            print("MAIN [Initializing perception and Sensor manager]")
            perception_system = RctaPerception()
            sensor_manager = SensorManager(manager.world, manager.actor_list)

            print("MAIN [Initializing Decision Maker and HMI Publisher]")
            decision_maker = DecisionMaker()
            mqtt_publisher = MqttPublisher(
                broker_address=config.MQTT_BROKER,
                port=config.MQTT_PORT
            )
            mqtt_publisher.connect()

            print("MAIN [Initializing controller]")
            controller = KeyboardController()

            print("MAIN [Initializing cameras and callback]")
            rear_cam, left_cam, right_cam = sensor_manager.setup_rcta_cameras(ego_vehicle)

            rear_cam.listen(perception_system.rear_cam_callback)
            left_cam.listen(perception_system.left_cam_callback)
            right_cam.listen(perception_system.right_cam_callback)

            print("MAIN [Initializing spectator]")
            spectator = manager.world.get_spectator()

            time.sleep(1.0)
            running = True

            while running:
                manager.world.tick()

                #spectator view
                ego_transform = ego_vehicle.get_transform()
                spectator_location = (ego_transform.location +
                                      ego_transform.get_forward_vector() * (-10) +
                                      carla.Location(z=5))
                spectator_rotation = carla.Rotation(pitch=-30, yaw=ego_transform.rotation.yaw)
                spectator.set_transform(carla.Transform(spectator_location, spectator_rotation))

                #Gestione input
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                keys = pygame.key.get_pressed()
                if keys[pygame.K_q]:
                    running = False

                control = controller.parse_input(keys)
                ego_vehicle.apply_control(control)
                is_reversing = control.reverse

                #Percezione
                perception_data = perception_system.get_perception_data()
                #Decisione
                dangerous_objects_list = decision_maker.evaluate(
                    perception_data,
                    is_reversing
                )
                mqtt_publisher.publish_status(dangerous_objects_list)

                #Finestre di visualizzazione
                frames = perception_system.current_frames
                detections = perception_system.detected_objects
                if frames['rear'] is not None:
                    display_rear = frames['rear'].copy()
                    draw_detections(display_rear, detections['rear'])
                    cv2.imshow('Rear Camera', display_rear)

                if frames['left'] is not None:
                    display_left = frames['left'].copy()
                    dist_left = perception_data['left']['dist']
                    ttc_left = perception_data['left']['ttc']
                    is_alert_left = "depth_left" in dangerous_objects_list

                    draw_depth_info(display_left, dist_left, ttc_left, is_alert_left)
                    cv2.imshow('Left RCTA Camera (Depth)', display_left)

                if frames['right'] is not None:
                    display_right = frames['right'].copy()
                    dist_right = perception_data['right']['dist']
                    ttc_right = perception_data['right']['ttc']
                    is_alert_right = "depth_right" in dangerous_objects_list

                    draw_depth_info(display_right, dist_right, ttc_right, is_alert_right)
                    cv2.imshow('Right RCTA Camera (Depth)', display_right)


                cv2.waitKey(1)
                pygame.display.flip()


    except KeyboardInterrupt:
        print("\nMAIN [Script interrupted from keyboard]")
    except Exception as e:
        print(f"\nMAIN [Exception: {e}]")
    finally:
        pygame.quit()
        cv2.destroyAllWindows()
        print("MAIN [All windows closed]")


if __name__ == '__main__':
    main()
