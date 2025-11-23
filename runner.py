import carla
import time
import pygame
import config

from carla_bridge.carla_manager import CarlaManager
from carla_bridge.spawner import Spawner
from scenarios.parking_lot_scenario import (
    scenario_vehicle,
    scenario_bicycle,
    scenario_pedestrian_adult,
    scenario_pedestrian_child,
    setup_rcta_base_scenario
)
from controller.keyboard_controller import KeyboardController


def main():
    # Inizializzazione pygame per input da tastiera
    pygame.init()
    pygame.display.set_mode((200, 100))
    pygame.display.set_caption('CARLA Control')
    clock = pygame.time.Clock()

    try:
        with CarlaManager() as manager:
            # MODALITÀ ASINCRONA (come nel notebook originale)
            # Non impostiamo synchronous_mode, quindi rimane False (default)
            # La simulazione CARLA gira in modo indipendente
            
            print("MAIN [Initializing scenario]")
            spawner = Spawner(manager.world, manager.actor_list)
            ego_vehicle = setup_rcta_base_scenario(manager.world, spawner, True, False)
            if not ego_vehicle:
                print("MAIN [Failed to spawn ego vehicle]")
                return

            print("MAIN [Initializing controller]")
            controller = KeyboardController()

            print("MAIN [Initializing spectator]")
            spectator = manager.world.get_spectator()

            # Scegli uno scenario (decommentane uno)
            # scenario_vehicle(spawner)
            scenario_bicycle(spawner)
            # scenario_pedestrian_adult(spawner)
            # scenario_pedestrian_child(spawner)

            print("MAIN [Starting simulation loop]")
            time.sleep(1.0)

            running = True
            frame_count = 0
            start_time = time.time()

            while running:
                # NESSUN world.tick() in modalità asincrona!
                # Il simulatore avanza automaticamente
                
                # Aggiorna posizione spectator (visuale aerea dietro il veicolo)
                ego_transform = ego_vehicle.get_transform()
                spectator_location = (
                        ego_transform.location +
                        ego_transform.get_forward_vector() * (-10) +
                        carla.Location(z=5)
                )
                spectator_rotation = carla.Rotation(
                    pitch=-30,
                    yaw=ego_transform.rotation.yaw
                )
                spectator.set_transform(
                    carla.Transform(spectator_location, spectator_rotation)
                )

                # Gestione eventi pygame
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                # Leggi input da tastiera e applica controllo
                keys = pygame.key.get_pressed()
                control = controller.parse_input(keys)
                ego_vehicle.apply_control(control)

                # FPS counter ogni 100 frame
                frame_count += 1
                if frame_count % 100 == 0:
                    elapsed = time.time() - start_time
                    fps = frame_count / elapsed
                    print(f"MAIN [FPS: {fps:.1f}]")

                # Mantieni il framerate del loop Python (non del simulatore!)
                pygame.display.flip()
                clock.tick(40)  # 40 FPS per il loop Python

    except KeyboardInterrupt:
        print("\nMAIN [Script interrupted from keyboard]")
    except Exception as e:
        print(f"\nMAIN [Exception: {e}]")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("MAIN [Cleanup completed]")


if __name__ == '__main__':
    main()