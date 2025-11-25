import pygame
import math
import paho.mqtt.client as mqtt
import json
import sys
import os
import time

script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
try:
    import config
except ImportError:
    print("HMI_DISPLAY [ERROR: Config not found]")
    sys.exit(1)


SCREEN_WIDTH = 420
SCREEN_HEIGHT = 420
BG_COLOR = (30, 30, 30)  # grigio
CAR_COLOR = (100, 100, 255)  # blue

COLOR_SAFE = (50, 200, 50, 100)  # verde trasparente
COLOR_WARNING = (255, 200, 0, 180)  # Giallo semi-opaco
COLOR_DANGER = (255, 0, 0, 200)

TEXT_COLOR = (255, 255, 255)
TEXT_DANGER_COLOR = (255, 180, 180)
TEXT_BG_COLOR = (0, 0, 0, 160)  # Sfondo semi-trasparente per leggibilità

CAR_ICON_PATH = os.path.join(project_root, "hmi", "car-top.png")

radar_data = {
    'left': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf'), 'last_seen': 0.0},
    'rear': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf'), 'last_seen': 0.0},
    'right': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf'), 'last_seen': 0.0}
}

ZONE_TIMEOUT_SEC = 1.0

def _on_connect(client, userdata, flags, reason_code, propertie):
    if reason_code == 0:
        print(f"HMI_DISPLAY [Connected to the broker {config.MQTT_BROKER}]")
        client.subscribe(config.MQTT_TOPIC_ALERTS)
        print(f"HMI_DISPLAY [Subscribed at the topic'{config.MQTT_TOPIC_ALERTS}]'")
    else:
        print(f"HMI_DISPLAY [Connection failed {reason_code}]")

def _on_message(client, userdata, msg):
    global radar_data
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        current_time = time.time()

        if data.get("alert") is True:
            for obj in data.get("objects", []):
                zone = obj.get("zone")
                if zone not in radar_data:
                    continue

                level = obj.get("alert_level")
                label = obj.get("class", "???").upper()
                dist = obj.get("distance", float('inf'))
                ttc = obj.get("ttc", float('inf'))

                current_state = radar_data[zone]['state']

                # Priorità: Danger > Warning > (più vicino)
                if level == "danger":
                    radar_data[zone] = {
                        'state': 'DANGER',
                        'label': label,
                        'dist': dist,
                        'ttc': ttc,
                        'last_seen': current_time
                    }

                elif level == "warning" and current_state != 'DANGER':
                    # Applica WARNING solo se non è DANGER e se è l'oggetto più vicino
                    if dist < radar_data[zone]['dist']:
                        radar_data[zone] = {
                            'state': 'WARNING',
                            'label': label,
                            'dist': dist,
                            'ttc': ttc,
                            'last_seen': current_time
                        }

    except json.JSONDecodeError:
        print(f"HMI_GRAPHICS [Invalid JSON: {msg.payload}]")
    except Exception as e:
        print(f"HMI_GRAPHICS [Error processing message: {e}]")

def draw_sector(surface, center, start_angle, end_angle, radius, color):
    points = [center]
    steps = 30
    for i in range(steps + 1):
        angle = math.radians(start_angle + (end_angle - start_angle) * i / steps)
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle)
        points.append((x, y))

    sector_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(sector_surf, color, points)
    surface.blit(sector_surf, (0, 0))

def draw_labels(surface, center, sectors_config, font_class, font_data):
    for side, data in sectors_config.items():
        if data['state'] == 'SAFE':
            continue

        # Posizione del testo
        mid_angle_rad = math.radians((data['start'] + data['end']) / 2)
        text_radius = 130

        x = center[0] + text_radius * math.cos(mid_angle_rad)
        y = center[1] - text_radius * math.sin(mid_angle_rad)

        # Prepara stringhe
        label_str = data['label']
        dist_str = f"{data['dist']:.1f}m" if data['dist'] != float('inf') else ""
        ttc_str = f"{data['ttc']:.1f}s" if data['ttc'] != float('inf') else ""

        data_str = f"{dist_str} | {ttc_str}" if dist_str and ttc_str else (dist_str or ttc_str)

        # Renderizza testi
        surf_class = font_class.render(label_str, True, TEXT_COLOR)
        data_color = TEXT_DANGER_COLOR if data['state'] == 'DANGER' else TEXT_COLOR
        surf_data = font_data.render(data_str, True, data_color)

        # Layout
        rect_class = surf_class.get_rect(center=(x, y - 12))
        rect_data = surf_data.get_rect(center=(x, y + 12))

        # Sfondo
        bg_rect = rect_class.union(rect_data).inflate(12, 10)
        s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        s.fill(TEXT_BG_COLOR)
        surface.blit(s, bg_rect.topleft)

        # Disegna testi
        surface.blit(surf_class, rect_class)
        surface.blit(surf_data, rect_data)

def check_zone_timeouts():
    current_time = time.time()
    for zone in radar_data:
        if radar_data[zone]['state'] != 'SAFE':
            if current_time - radar_data[zone]['last_seen'] > ZONE_TIMEOUT_SEC:
                radar_data[zone] = {
                    'state': 'SAFE',
                    'label': '',
                    'dist': float('inf'),
                    'ttc': float('inf'),
                    'last_seen': 0.0
                }

def main():
    global radar_data, last_update

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = _on_connect
    client.on_message = _on_message
    try:
        client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
        client.loop_start()
    except Exception as e:
        print(f"HMI_GRAPHICS [MQTT Error: {e}]")
        return

    # --- Setup Pygame e FONT ---
    pygame.init()
    pygame.font.init()
    font_class = pygame.font.SysFont('Arial', 20, bold=True)
    font_data = pygame.font.SysFont('Arial', 15)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("RCTA HMI")
    clock = pygame.time.Clock()

    car_img = None
    if os.path.exists(CAR_ICON_PATH):
        try:
            car_img = pygame.image.load(CAR_ICON_PATH).convert_alpha()
            car_img = pygame.transform.scale(car_img, (200, 250))
        except:
            print("HMI_GRAPHICS [Warning: Could not load car image]")

    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2 + 20

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        check_zone_timeouts()

        screen.fill(BG_COLOR)

        sectors_config = {
            'left': {'start': 180, 'end': 240, **radar_data['left']},
            'rear': {'start': 240, 'end': 300, **radar_data['rear']},
            'right': {'start': 300, 'end': 360, **radar_data['right']}
        }

        # --- Disegno Settori ---
        for side, data in sectors_config.items():
            state = data['state']
            color = COLOR_SAFE
            if state == 'WARNING':
                color = COLOR_WARNING
            elif state == 'DANGER':
                color = COLOR_DANGER
            draw_sector(screen, (cx, cy), data['start'], data['end'], 180, color)

        img_rect = car_img.get_rect(center=(cx, cy-60))
        screen.blit(car_img, img_rect)
        draw_labels(screen, (cx, cy), sectors_config, font_class, font_data)

        pygame.display.flip()
        clock.tick(40)

    client.loop_stop()
    client.disconnect()
    pygame.quit()
    print("HMI_GRAPHICS [Shutdown complete]")


if __name__ == "__main__":
    main()