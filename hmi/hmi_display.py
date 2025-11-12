import pygame
import math
import paho.mqtt.client as mqtt
import json
import sys
import os

# --- CONFIGURAZIONE PATH ---
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
try:
    import config
except ImportError:
    print("HMI_DISPLAY [ERROR: Config not found]")
    sys.exit(1)

# --- COSTANTI GRAFICHE ---
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600
BG_COLOR = (30, 30, 30)  # grigio
CAR_COLOR = (100, 100, 255)  # blue

COLOR_SAFE = (50, 200, 50, 100)  # verde trasparente
COLOR_WARNING = (255, 200, 0, 180)  # Giallo semi-opaco
COLOR_DANGER = (255, 0, 0, 200)

# --- NUOVE COSTANTI TESTO ---
TEXT_COLOR = (255, 255, 255)
TEXT_DANGER_COLOR = (255, 180, 180)  # Rosso chiaro per TTC
TEXT_BG_COLOR = (0, 0, 0, 160)  # Sfondo semi-trasparente per leggibilità

CAR_ICON_PATH = os.path.join(project_root, "hmi", "car-top.png")

# --- MODIFICA STATO GLOBALE ---
# Ora memorizziamo lo stato completo per ogni settore
radar_data = {
    'left': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf')},
    'rear': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf')},
    'right': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf')}
}
flash_timer = 0


def _on_connect(client, userdata, flags, reason_code, propertie):
    """
    Callback when a connection is established.
    """
    if reason_code == 0:
        print(f"HMI_DISPLAY [Connected to the broker {config.MQTT_BROKER}]")
        client.subscribe(config.MQTT_TOPIC_ALERTS)
        print(f"HMI_DISPLAY [Subscribed at the topic'{config.MQTT_TOPIC_ALERTS}]'")
    else:
        print(f"HMI_DISPLAY [Connection failed {reason_code}]")


def _on_message(client, userdata, msg):
    """
    Callback when a message is received.
    --- VERSIONE CORRETTA E AGGIORNATA ---
    """
    global radar_data  # Usiamo la variabile globale corretta
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        # Reset
        new_data = {
            'left': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf')},
            'rear': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf')},
            'right': {'state': 'SAFE', 'label': '', 'dist': float('inf'), 'ttc': float('inf')}
        }

        if data.get("alert") is True:
            for obj in data.get("objects", []):
                side = obj.get("zone")
                if not side: continue

                level = obj.get("alert_level")
                label = obj.get("class", "???").upper()
                dist = obj.get("distance", float('inf'))
                ttc = obj.get("ttc", float('inf'))

                current_state = new_data[side]['state']

                # Priorità: Danger > Warning > (più vicino)
                if level == "danger":
                    # Sovrascrivi sempre con DANGER
                    new_data[side] = {'state': 'DANGER', 'label': "FAST!" if label == "FAST" else label, 'dist': dist,
                                      'ttc': ttc}

                elif level == "warning" and current_state != 'DANGER':
                    # Applica WARNING solo se non è DANGER e se è l'oggetto più vicino
                    if dist < new_data[side]['dist']:
                        new_data[side] = {'state': 'WARNING', 'label': label, 'dist': dist, 'ttc': ttc}

        # --- FIX BUG: Aggiorna lo stato globale ---
        radar_data = new_data

    except json.JSONDecodeError:
        print(f"HMI_GRAPHICS [Invalid JSON: {msg.payload}]")
    except Exception as e:
        print(f"HMI_GRAPHICS [Error processing message: {e}]")


def draw_sector(surface, center, start_angle, end_angle, radius, color):
    """
    Disegna un settore circolare (approssimato con un poligono) per il radar.
    """
    points = [center]
    steps = 20  # Precisione dell'arco
    for i in range(steps + 1):
        angle = math.radians(start_angle + (end_angle - start_angle) * i / steps)
        x = center[0] + radius * math.cos(angle)
        y = center[1] - radius * math.sin(angle)  # Y invertita in Pygame
        points.append((x, y))

    sector_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.draw.polygon(sector_surf, color, points)
    surface.blit(sector_surf, (0, 0))


# --- NUOVA FUNZIONE PER DISEGNARE ETICHETTE ---
def draw_labels(surface, center, sectors_config, font_class, font_data):
    """
    Disegna le etichette (classe, dist, ttc) sui settori.
    """
    for side, data in sectors_config.items():
        if data['state'] == 'SAFE':
            continue  # Non disegnare nulla se sicuro

        # Calcola posizione centrale del testo
        mid_angle_rad = math.radians((data['start'] + data['end']) / 2)
        text_radius = 180  # Distanza dal centro

        x = center[0] + text_radius * math.cos(mid_angle_rad)
        y = center[1] - text_radius * math.sin(mid_angle_rad)

        # Prepara le stringhe
        label_str = data['label']
        dist_str = f"{data['dist']:.1f}m" if data['dist'] != float('inf') else ""
        ttc_str = f"{data['ttc']:.1f}s" if data['ttc'] != float('inf') else ""

        # Stringa dati combinata
        data_str = f"{dist_str} | {ttc_str}" if dist_str and ttc_str else (dist_str or ttc_str)

        # Renderizza i testi
        surf_class = font_class.render(label_str, True, TEXT_COLOR)

        # Colora i dati di rosso chiaro se è DANGER
        data_color = TEXT_DANGER_COLOR if data['state'] == 'DANGER' else TEXT_COLOR
        surf_data = font_data.render(data_str, True, data_color)

        # Calcola il layout verticale (classe in alto, dati sotto)
        rect_class = surf_class.get_rect(center=(x, y - 12))
        rect_data = surf_data.get_rect(center=(x, y + 12))

        # Creiamo un rettangolo di sfondo unico
        bg_rect = rect_class.union(rect_data).inflate(10, 8)

        # Disegna sfondo
        s = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        s.fill(TEXT_BG_COLOR)
        surface.blit(s, bg_rect.topleft)

        # Disegna testi
        surface.blit(surf_class, rect_class)
        surface.blit(surf_data, rect_data)


def main():
    global flash_timer
    global radar_data  # Assicurati che usi radar_data

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
    pygame.font.init()  # Inizializza il modulo font
    font_class = pygame.font.SysFont('Arial', 24, bold=True)
    font_data = pygame.font.SysFont('Arial', 18)

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

    cx, cy = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        flash_timer += 1
        flash_on = (flash_timer % 30) < 15

        # --- MODIFICA: Leggi da radar_data ---
        sectors_config = {
            'rear': {'start': 250, 'end': 290, **radar_data['rear']},
            'right': {'start': 290, 'end': 350, **radar_data['right']},
            'left': {'start': 190, 'end': 250, **radar_data['left']}
        }

        # --- Disegno Settori ---
        for side, data in sectors_config.items():
            state = data['state']
            color = COLOR_SAFE

            if state == 'WARNING':
                color = COLOR_WARNING
            elif state == 'DANGER':
                color = COLOR_DANGER if flash_on else (255, 0, 0, 50)

            draw_sector(screen, (cx, cy + 40), data['start'], data['end'], 250, color)

        # --- Disegno Veicolo Ego ---
        if car_img:
            img_rect = car_img.get_rect(center=(cx, cy))
            screen.blit(car_img, img_rect)
        else:
            # Fallback
            pygame.draw.rect(screen, CAR_COLOR, (cx - 30, cy - 60, 60, 120), border_radius=10)
            pygame.draw.polygon(screen, (80, 80, 255), [(cx - 30, cy - 60), (cx + 30, cy - 60), (cx, cy - 90)])

        # --- NUOVA CHIAMATA: Disegna Etichette ---
        # Disegnato dopo l'auto, così il testo è sopra tutto
        draw_labels(screen, (cx, cy + 40), sectors_config, font_class, font_data)

        pygame.display.flip()
        clock.tick(60)

    client.loop_stop()
    client.disconnect()
    pygame.quit()
    print("HMI_GRAPHICS [Shutdown complete]")


if __name__ == "__main__":
    main()