import numpy as np
from rcta_system.object_detector import ObjectDetector
import cv2
import threading
import time


class RctaPerception:
    """
    Manages vision-only perception for the rcta system.
    Handles 3 RGBD pairs (6 sensors total) with ASYNC detection.
    """

    def __init__(self):
        print("Starting RctaPerception (Async Mode)...")
        self.detector = ObjectDetector()

        # Lock per sincronizzare l'accesso ai dati condivisi tra thread
        self.lock = threading.Lock()
        self.running = True

        # Buffer per i frame più recenti da passare a YOLO
        self.latest_rgb_for_yolo = {
            'rear': None, 'left': None, 'right': None
        }
        # Flag per sapere se c'è un frame nuovo da processare
        self.has_new_frame = {
            'rear': False, 'left': False, 'right': False
        }

        # Dati processati (distanze, ttc)
        self.perception_data = {
            'rear': {'dist': float('inf'), 'ttc': float('inf')},
            'left': {'dist': float('inf'), 'ttc': float('inf')},
            'right': {'dist': float('inf'), 'ttc': float('inf')}
        }

        # Oggetti rilevati da YOLO (aggiornati dal thread asincrono)
        self.detected_objects = {
            'rear': [],
            'left': [],
            'right': []
        }

        # Frame per visualizzazione immediata nel Main (fluidi)
        self.current_rgb_frames = {
            'rear': None, 'left': None, 'right': None
        }
        self.current_depth_frames = {
            'rear': None, 'left': None, 'right': None
        }

        self.previous_data = {
            'rear': {'dist': float('inf'), 'time': 0.0},
            'left': {'dist': float('inf'), 'time': 0.0},
            'right': {'dist': float('inf'), 'time': 0.0}
        }

        # AVVIO DEL THREAD DI DETECTION
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        print("RctaPerception: Detection thread started.")

    def _detection_loop(self):
        """
        Loop infinito che gira in un thread separato.
        Controlla ciclicamente se ci sono nuovi frame e lancia YOLO.
        """
        while self.running:
            something_processed = False
            # Cicla attraverso le tre camere
            for side in ['rear', 'left', 'right']:
                img_to_process = None

                # Sezione critica: controlliamo se c'è un nuovo frame in modo sicuro
                with self.lock:
                    if self.has_new_frame[side]:
                        # Prendiamo un riferimento al frame e resettiamo il flag
                        img_to_process = self.latest_rgb_for_yolo[side]
                        self.has_new_frame[side] = False

                # Se abbiamo trovato un frame nuovo, eseguiamo YOLO (fuori dal lock!)
                if img_to_process is not None:
                    detections = self.detector.detect(img_to_process)
                    # Aggiorniamo i risultati in modo sicuro
                    with self.lock:
                        self.detected_objects[side] = detections
                    something_processed = True

            # Se non abbiamo processato nulla in questo ciclo, dormiamo un po' per non fondere la CPU
            if not something_processed:
                time.sleep(0.01)

    def stop(self):
        """Ferma il thread di detection alla chiusura"""
        self.running = False
        if self.detection_thread.is_alive():
            self.detection_thread.join(timeout=1.0)

    def _process_rgb_image(self, carla_image):
        array = np.frombuffer(carla_image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_image.height, carla_image.width, 4))
        array_bgr = array[:, :, :3]
        return array_bgr

    def _process_depth_image(self, carla_image):
        # ... (codice invariato per depth)
        array = np.frombuffer(carla_image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_image.height, carla_image.width, 4))
        array = array.astype(np.float64)
        distance = array[:, :, 2] + array[:, :, 1] * 256 + array[:, :, 0] * 256 * 256
        distance_meters = distance / (256 * 256 * 256 - 1) * 1000.0
        normalized_frame = np.clip(distance_meters / 100.0, 0.0, 1.0) * 255.0
        normalized_frame = normalized_frame.astype(np.uint8)
        display_frame = cv2.cvtColor(normalized_frame, cv2.COLOR_GRAY2BGR)
        return distance_meters, display_frame

    def _calculate_dynamic_ttc(self, depth_map, carla_image, camera_side):
        # ... (codice invariato per TTC)
        height = depth_map.shape[0]
        roi_top = int(height * 0.25)
        roi_bottom = int(height * 0.75)
        roi_depth_map = depth_map[roi_top:roi_bottom, :]
        if roi_depth_map.size > 0:
            current_dist = np.min(roi_depth_map)
        else:
            current_dist = float('inf')
        current_time = carla_image.timestamp
        prev_dist = self.previous_data[camera_side]['dist']
        prev_time = self.previous_data[camera_side]['time']
        ttc = float('inf')
        if prev_time > 0.0:
            delta_t = current_time - prev_time
            delta_d = prev_dist - current_dist
            if delta_t > 0.01:
                v_relative = delta_d / delta_t
                if v_relative > 0.1:
                    ttc = current_dist / v_relative
        self.previous_data[camera_side]['dist'] = current_dist
        self.previous_data[camera_side]['time'] = current_time
        return current_dist, ttc

    # --- CALLBACKS RGB MODIFICATI (Non bloccanti) ---
    def rear_rgb_callback(self, image):
        np_image = self._process_rgb_image(image)
        # Aggiornamento immediato per display fluido
        self.current_rgb_frames['rear'] = np_image
        # Passaggio al thread di detection
        with self.lock:
            self.latest_rgb_for_yolo['rear'] = np_image
            self.has_new_frame['rear'] = True

    def left_rgb_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.current_rgb_frames['left'] = np_image
        with self.lock:
            self.latest_rgb_for_yolo['left'] = np_image
            self.has_new_frame['left'] = True

    def right_rgb_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.current_rgb_frames['right'] = np_image
        with self.lock:
            self.latest_rgb_for_yolo['right'] = np_image
            self.has_new_frame['right'] = True

    # --- CALLBACKS DEPTH (Invariati, opzionali per ora) ---
    def rear_depth_callback(self, image):
        depth_map, display_frame = self._process_depth_image(image)
        dist, ttc = self._calculate_dynamic_ttc(depth_map, image, 'rear')
        self.perception_data['rear'] = {'dist': dist, 'ttc': ttc}
        self.current_depth_frames['rear'] = display_frame

    def left_depth_callback(self, image):
        depth_map, display_frame = self._process_depth_image(image)
        dist, ttc = self._calculate_dynamic_ttc(depth_map, image, 'left')
        self.perception_data['left'] = {'dist': dist, 'ttc': ttc}
        self.current_depth_frames['left'] = display_frame

    def right_depth_callback(self, image):
        depth_map, display_frame = self._process_depth_image(image)
        dist, ttc = self._calculate_dynamic_ttc(depth_map, image, 'right')
        self.perception_data['right'] = {'dist': dist, 'ttc': ttc}
        self.current_depth_frames['right'] = display_frame

    def get_perception_data(self):
        # Restituisce una copia sicura dei dati attuali
        with self.lock:
            final_data = {}
            for side in ['rear', 'left', 'right']:
                final_data[side] = {
                    # Usiamo .copy() se sono liste per sicurezza thread,
                    # anche se qui stiamo solo leggendo reference
                    'objects': list(self.detected_objects[side]),
                    'dist': self.perception_data[side]['dist'],
                    'ttc': self.perception_data[side]['ttc']
                }
        return final_data