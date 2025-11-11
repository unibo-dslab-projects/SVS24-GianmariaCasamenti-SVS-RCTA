import threading
import numpy as np
import cv2
import time
import config  # <-- AGGIUNTO IMPORT
from rcta_system.object_detector import ObjectDetector


class RctaCameraChannel:
    """
    Manage a single pair of cameras (RGB + depth) in a dedicated thread,
    Do data fusion and produce a frame.
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

        # dizionario tracker
        # Formato: { track_id: {'dist': float, 'time': float, 'class': str} }
        self.tracked_objects = {}
        self.last_cleanup_time = 0.0

        self.STALE_TRACK_THRESHOLD_SEC = 1.0  # Tempo per cui tenere un track se scompare
        self.MIN_VELOCITY_FOR_TTC_MPS = 0.5  # Velocità minima (m/s) per calcolare il TTC

        # Avvio del worker thread
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()
        print(f"PERCEPTION [Channel '{side}' started]")

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
        """Main loop to process RGB + Depth"""
        while self.running:
            if self.has_new_data and self.latest_rgb_img and self.latest_depth_img:
                # Prendi snapshot dei dati attuali
                rgb_carla = self.latest_rgb_img
                depth_carla = self.latest_depth_img
                self.has_new_data = False  # Reset flag
                # Conversione dati
                rgb_np = self._to_numpy_rgb(rgb_carla)
                depth_meters = self._to_depth_meters(depth_carla)
                timestamp = depth_carla.timestamp

                # YOLO Detection (Sincronizzata con Lock per sicurezza GPU)
                with self.detector_lock:
                    detections = self.detector.detect(rgb_np)

                # Fusione RGB-Depth e calcolo TTC settore
                fused_objects, min_dist = self._fuse_results(detections, depth_meters)

                # calcola ttc per ogni oggetto e aggiorna lo stato
                self._update_tracks_and_calc_ttc(fused_objects, timestamp)
                # pulisce i vecchi track
                self._cleanup_stale_tracks(timestamp)

                # Trova il TTC minimo tra tutti gli oggetti del settore
                min_sector_ttc = float('inf')
                for obj in fused_objects:
                    if obj.get('ttc_obj', float('inf')) < min_sector_ttc:
                        min_sector_ttc = obj['ttc_obj']

                # Aggiorna dati pronti per il main
                self.display_frame = rgb_np.copy()
                self.perception_data = {
                    'dist': min_dist,
                    'ttc': min_sector_ttc,  # Ora è il min TTC *degli oggetti*
                    'objects': fused_objects  # Lista di oggetti con 'ttc_obj' individuale
                }
            else:
                time.sleep(0.005)  # Evita busy-waiting eccessivo

    def _fuse_results(self, detections, depth_map):
        """
        For each detection, find the average distance in the corresponding depth map.
        Returns enriched objects and the global minimum distance of the scene.
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

            det['dist'] = obj_dist
            det['ttc_obj'] = float('inf')

            fused.append(det)
            if obj_dist < min_scene_dist:
                min_scene_dist = obj_dist

        return fused, min_scene_dist

    def _update_tracks_and_calc_ttc(self, current_objects, current_time):
        """
        Aggiorna lo stato degli oggetti tracciati e calcola il TTC per ognuno.
        Modifica 'current_objects' in-place aggiungendo 'ttc_obj'.
        """
        for obj in current_objects:
            track_id = obj['id']

            if track_id in self.tracked_objects:
                # Oggetto già tracciato
                prev_state = self.tracked_objects[track_id]

                delta_t = current_time - prev_state['time']
                delta_d = prev_state['dist'] - obj['dist']  # Positivo se si avvicina

                # Calcola TTC solo se abbiamo uno storico e si sta avvicinando
                if delta_t > 0.0:
                    rel_velocity = delta_d / delta_t  # m/s

                    if rel_velocity > self.MIN_VELOCITY_FOR_TTC_MPS:
                        # Calcola il TTC solo se la velocità è significativa
                        ttc = obj['dist'] / rel_velocity
                        obj['ttc_obj'] = ttc  # Assegna il TTC all'oggetto specifico

            # Aggiorna (o aggiungi) lo stato dell'oggetto
            self.tracked_objects[track_id] = {
                'dist': obj['dist'],
                'time': current_time,
                'class': obj['class']
            }

    def _cleanup_stale_tracks(self, current_time):
        """
        Rimuove gli oggetti da self.tracked_objects se non visti per un po'.
        """
        # Esegui la pulizia solo ogni tanto per efficienza
        if current_time - self.last_cleanup_time < self.STALE_TRACK_THRESHOLD_SEC:
            return

        self.last_cleanup_time = current_time

        stale_ids = [
            track_id for track_id, state in self.tracked_objects.items()
            if current_time - state['time'] > self.STALE_TRACK_THRESHOLD_SEC
        ]

        for track_id in stale_ids:
            del self.tracked_objects[track_id]

    def rgb_callback(self, img):
        self.latest_rgb_img = img
        # Consideriamo i dati pronti solo se abbiamo anche una depth recente
        if self.latest_depth_img is not None: self.has_new_data = True

    def depth_callback(self, img):
        self.latest_depth_img = img


class RctaPerception:
    """Manager of a single independent channel"""

    def __init__(self):

        # --- BLOCCO MODIFICATO ---
        if config.USE_SHARED_YOLO_INSTANCE:
            # Modalità 1: Un solo modello YOLO e un solo Lock condivisi
            print("PERCEPTION [Initializing with 1 Shared YOLO model]")
            detector = ObjectDetector()
            lock = threading.Lock()  # Lock per condividere l'unica istanza YOLO

            self.channels = {
                'rear': RctaCameraChannel('rear', detector, lock),
                'left': RctaCameraChannel('left', detector, lock),
                'right': RctaCameraChannel('right', detector, lock)
            }
        else:
            # Modalità 2: Tre modelli YOLO e tre Lock indipendenti
            print("PERCEPTION [Initializing with 3 Independent YOLO models]")

            # Crea un'istanza (e un lock) separata per ogni canale
            detector_rear = ObjectDetector()
            lock_rear = threading.Lock()

            detector_left = ObjectDetector()
            lock_left = threading.Lock()

            detector_right = ObjectDetector()
            lock_right = threading.Lock()

            self.channels = {
                'rear': RctaCameraChannel('rear', detector_rear, lock_rear),
                'left': RctaCameraChannel('left', detector_left, lock_left),
                'right': RctaCameraChannel('right', detector_right, lock_right)
            }
        # --- FINE BLOCCO MODIFICATO ---

    # Wrapper callbacks
    def rear_rgb_callback(self, i):
        self.channels['rear'].rgb_callback(i)

    def rear_depth_callback(self, i):
        self.channels['rear'].depth_callback(i)

    def left_rgb_callback(self, i):
        self.channels['left'].rgb_callback(i)

    def left_depth_callback(self, i):
        self.channels['left'].depth_callback(i)

    def right_rgb_callback(self, i):
        self.channels['right'].rgb_callback(i)

    def right_depth_callback(self, i):
        self.channels['right'].depth_callback(i)

    def get_all_perception_data(self):
        """Join all data in a single dictionary"""
        return {
            side: channel.perception_data
            for side, channel in self.channels.items()
        }