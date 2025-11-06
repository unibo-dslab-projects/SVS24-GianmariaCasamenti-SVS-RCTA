import threading
import numpy as np
import cv2
import time
from rcta_system.object_detector import ObjectDetector


class RctaCameraChannel:
    """
    Gestisce una singola coppia di camere (RGB + Depth) in un thread dedicato.
    Effettua la fusione dei dati e produce frame pronti per la visualizzazione.
    """

    def __init__(self, side, detector, detector_lock):
        self.side = side
        self.detector = detector
        self.detector_lock = detector_lock  # Lock condiviso per l'inferenza
        self.running = True

        # Buffer per i dati grezzi in arrivo dai callback
        self.latest_rgb_img = None
        self.latest_depth_img = None
        self.has_new_data = False

        # Dati pronti per il main thread
        self.display_frame = None
        self.perception_data = {'dist': float('inf'), 'ttc': float('inf'), 'objects': []}

        # Variabili per calcolo TTC di settore
        self.prev_min_dist = float('inf')
        self.prev_time = 0.0

        # Avvio del worker thread
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()
        print(f"RctaPerception: Channel '{side}' started.")

    def _to_numpy_rgb(self, carla_img):
        array = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_img.height, carla_img.width, 4))
        return array[:, :, :3]  # BGR per OpenCV

    def _to_depth_meters(self, carla_img):
        array = np.frombuffer(carla_img.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_img.height, carla_img.width, 4)).astype(np.float64)
        # Formula standard CARLA per ottenere metri
        normalized = (array[:, :, 2] + array[:, :, 1] * 256 + array[:, :, 0] * 256 * 256) / (256 ** 3 - 1)
        return normalized * 1000.0

    def _worker_loop(self):
        """Loop principale del thread che processa RGB+Depth."""
        while self.running:
            if self.has_new_data and self.latest_rgb_img and self.latest_depth_img:
                # 1. Prendi snapshot dei dati attuali
                rgb_carla = self.latest_rgb_img
                depth_carla = self.latest_depth_img
                self.has_new_data = False  # Reset flag

                # 2. Conversione dati
                rgb_np = self._to_numpy_rgb(rgb_carla)
                depth_meters = self._to_depth_meters(depth_carla)
                timestamp = depth_carla.timestamp

                # 3. YOLO Detection (Sincronizzata con Lock per sicurezza GPU)
                with self.detector_lock:
                    detections = self.detector.detect(rgb_np)

                # 4. Fusione RGB-Depth e calcolo TTC settore
                fused_objects, min_dist = self._fuse_results(detections, depth_meters)
                sector_ttc = self._calculate_sector_ttc(min_dist, timestamp)

                # 5. Aggiorna dati pronti per il main
                self.display_frame = rgb_np.copy()
                self.perception_data = {
                    'dist': min_dist,
                    'ttc': sector_ttc,
                    'objects': fused_objects
                }
            else:
                time.sleep(0.005)  # Evita busy-waiting eccessivo

    def _fuse_results(self, detections, depth_map):
        """
        Per ogni detection, trova la distanza media nella depth map corrispondente.
        Restituisce oggetti arricchiti e la distanza minima globale della scena.
        """
        h, w = depth_map.shape
        min_scene_dist = float('inf')
        fused = []

        for det in detections:
            # Coordinate BBox
            x1, y1, x2, y2 = map(int, det['bbox'])
            x1, x2 = max(0, x1), min(w, x2)
            y1, y2 = max(0, y1), min(h, y2)

            obj_dist = float('inf')
            if x1 < x2 and y1 < y2:
                # Estrai ROI dalla mappa di profondità
                roi = depth_map[y1:y2, x1:x2]
                # Usa il 10° percentile per trovare la distanza dell'oggetto ignorando outlier
                if roi.size > 0:
                    obj_dist = np.percentile(roi, 10)

            # Arricchisci la detection con la distanza
            det['dist'] = obj_dist
            # TTC per singolo oggetto richiederebbe tracking, per ora usiamo placeholder
            det['ttc_obj'] = 0.0

            fused.append(det)
            if obj_dist < min_scene_dist:
                min_scene_dist = obj_dist

        return fused, min_scene_dist

    def _calculate_sector_ttc(self, current_dist, current_time):
        ttc = float('inf')
        if self.prev_time > 0.0 and current_dist < 100.0:  # Calcola solo se distanza ragionevole
            delta_t = current_time - self.prev_time
            delta_d = self.prev_min_dist - current_dist
            # Se l'oggetto si avvicina velocemente (> 0.5 m/s)
            if delta_t > 0.0 and delta_d / delta_t > 0.5:
                v_rel = delta_d / delta_t
                ttc = current_dist / v_rel

        self.prev_min_dist = current_dist
        self.prev_time = current_time
        return ttc

    # --- Callbacks ---
    def rgb_callback(self, img):
        self.latest_rgb_img = img
        # Consideriamo i dati pronti solo se abbiamo anche una depth recente
        if self.latest_depth_img is not None: self.has_new_data = True

    def depth_callback(self, img):
        self.latest_depth_img = img


class RctaPerception:
    """
    Manager che inizializza i 3 canali indipendenti.
    """

    def __init__(self):
        self.detector = ObjectDetector()
        self.lock = threading.Lock()  # Lock per condividere l'unica istanza YOLO

        self.channels = {
            'rear': RctaCameraChannel('rear', self.detector, self.lock),
            'left': RctaCameraChannel('left', self.detector, self.lock),
            'right': RctaCameraChannel('right', self.detector, self.lock)
        }

    # Wrapper callbacks
    def rear_rgb_callback(self, i): self.channels['rear'].rgb_callback(i)

    def rear_depth_callback(self, i): self.channels['rear'].depth_callback(i)

    def left_rgb_callback(self, i): self.channels['left'].rgb_callback(i)

    def left_depth_callback(self, i): self.channels['left'].depth_callback(i)

    def right_rgb_callback(self, i): self.channels['right'].rgb_callback(i)

    def right_depth_callback(self, i): self.channels['right'].depth_callback(i)

    def get_all_perception_data(self):
        """Raccoglie i dati correnti da tutti i canali in un unico dizionario."""
        return {
            side: channel.perception_data
            for side, channel in self.channels.items()
        }