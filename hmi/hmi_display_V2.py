import pygame
import math
import paho.mqtt.client as mqtt
import json
import sys
import os
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
try:
    import config
except ImportError:
    print("HMI_DISPLAY [ERROR: Config not found]")
    sys.exit(1)


SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
BG_COLOR = (30,30,30) #grigio
CAR_COLOR = (100, 100, 255) #blue

COLOR_SAFE = (50, 200, 50, 100) #verde trasparente
COLOR_WARNING = (255, 200, 0, 180)   # Giallo semi-opaco
COLOR_DANGER = (255, 0, 0, 200)

CAR_ICON_PATH = os.path.join(project_root, "docs", "car-top.png")

radar_state = {
    'left':'SAFE',
    'right':'SAFE',
    'rear':'SAFE',
}
flash_timer = 0

def _on_connect(client, userdata, flags, reason_code, propertie):
    """
    Callback when a connection is established.
    """
    if reason_code == 0:
        print(f"HMI_DISPLAY [Connected to the broker {config.MQTT_BROKER}]")
        #topic
        client.subscribe(config.MQTT_TOPIC_ALERTS)
        print(f"HMI_DISPLAY [Subscribed at the topic'{config.MQTT_TOPIC_ALERTS}]'")
    else:
        print(f"HMI_DISPLAY [Connection failed {reason_code}]")


def _on_message(client, userdata, msg):
    """
    Callback when a message is received.
    """
    global radar_state
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        # Reset
        new_state = {'left': 'SAFE', 'rear': 'SAFE', 'right': 'SAFE'}
        if data.get("alert") is True:
            objects = data.get("objects", [])
            for obj_str in objects:
                # Formato atteso: "lato:tipo_alert" (es. "rear:approaching_fast" o "left:car_near")
                parts = obj_str.split(':')
                if len(parts) >= 2:
                    side = parts[0]
                    alert_type = parts[1]

                    # Determina livello di pericolo
                    if "approaching_fast" in alert_type:
                        new_state[side] = 'DANGER'
                    elif "_near" in alert_type and new_state[side] != 'DANGER':
                        # Upgrade a WARNING solo se non è già DANGER
                        new_state[side] = 'WARNING'
        radar_state = new_state

    except json.JSONDecodeError:
        print(f"HMI_GRAPHICS [Invalid JSON: {msg.payload}]")
    except Exception as e:
        print(f"HMI_GRAPHICS [Error processing message: {e}]")

def draw_sector(surface, center, start_angle, end_angle, radius, color):
    """
    Disegna un settore circolare (approssimato con un poligono) per il radar.
    """
    points = [center]
    steps = 20 # Precisione dell'arco
    for i in range(steps + 1):
        angle = math.radians(start_angle + (end_angle - start_angle) * i / steps)
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle) # Y invertita in Pygame
        points.append((x, y))

    # Crea una surface temporanea per la trasparenza (alpha)
    sector_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(sector_surf, color, points)
    surface.blit(sector_surf, (0, 0))


def main():
    global flash_timer

    # 1. Setup MQTT (non-blocking)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = _on_connect
    client.on_message = _on_message
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        client.loop_start()  # Avvia thread in background per MQTT
    except Exception as e:
        print(f"HMI_GRAPHICS [MQTT Error: {e}]")
        return

    # 2. Setup Pygame
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RCTA Radar HMI")
    clock = pygame.time.Clock()

    # Caricamento asset (con fallback)
    car_img = None
    if os.path.exists(CAR_ICON_PATH):
        try:
            car_img = pygame.image.load(CAR_ICON_PATH).convert_alpha()
            # Scaliamo l'auto a una dimensione ragionevole se necessario
            car_img = pygame.transform.scale(car_img, (200, 250))
        except:
            print("HMI_GRAPHICS [Warning: Could not load car image]")

    # Centro del veicolo nello schermo
    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    running = True
    while running:
        # --- Gestione Eventi Pygame ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- Logica di Rendering ---
        screen.fill(BG_COLOR)

        flash_timer += 1
        flash_on = (flash_timer % 30) < 15  # Lampeggia ogni mezzo secondo circa a 60FPS

        # Definizione angoli settori (in gradi standard, 0 = destra, 90 = su)
        # Rear: tra 240° e 300° (che in coordinate schermo è verso il basso)
        # Poiché Y è invertita: 270° è GIÙ in math.sin/cos standard se non invertiamo Y.
        # Usiamo coordinate polari "standard" e invertiamo Y nel disegno.
        # 270° = Basso (Rear), 270-45 = 225° (Left approx), 270+45 = 315° (Right approx)

        sectors_config = {
            'rear': {'start': 250, 'end': 290, 'state': radar_state['rear']},
            'right': {'start': 290, 'end': 350, 'state': radar_state['right']},
            'left': {'start': 190, 'end': 250, 'state': radar_state['left']}
        }

        for side, data in sectors_config.items():
            state = data['state']
            color = COLOR_SAFE

            if state == 'WARNING':
                color = COLOR_WARNING
            elif state == 'DANGER':
                # Se DANGER, lampeggia (alterna rosso e trasparente)
                color = COLOR_DANGER if flash_on else (255, 0, 0, 50)

            # Disegna il settore
            draw_sector(screen, (cx, cy + 40), data['start'], data['end'], 250, color)

        # --- Disegno Veicolo Ego ---
        if car_img:
            # Centra l'immagine
            img_rect = car_img.get_rect(center=(cx, cy))
            screen.blit(car_img, img_rect)
        else:
            # Fallback: rettangolo blu
            pygame.draw.rect(screen, CAR_COLOR, (cx - 30, cy - 60, 60, 120), border_radius=10)
            # Fronte auto
            pygame.draw.polygon(screen, (80, 80, 255), [(cx - 30, cy - 60), (cx + 30, cy - 60), (cx, cy - 90)])

        # Info testuali di debug (opzionale)
        # font = pygame.font.SysFont('Arial', 18)
        # text = font.render(f"L:{radar_state['left']} R:{radar_state['rear']} R:{radar_state['right']}", True, (255, 255, 255))
        # screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    # Chiusura
    client.loop_stop()
    client.disconnect()
    pygame.quit()
    print("HMI_GRAPHICS [Shutdown complete]")


if __name__ == "__main__":
    main()