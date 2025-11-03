import numpy as np
from rcta_system.object_detector import ObjectDetector
import config
import cv2

class RctaPerception:
    """
    Manages vision-only perception for the rcta system.
    contains sensor callback.
    """
    def __init__(self):
        print("Strating RctaPerception..")
        self.detector = ObjectDetector()

        self.perception_data = {
            'rear': [],
            'left': {'dist': float('inf'), 'ttc': float('inf')},
            'right': {'dist': float('inf'), 'ttc': float('inf')}
        }

        self.detected_objects = {
            'rear': [],
            'left': [],
            'right': []
        }

        self.current_frames = {'rear': None, 'left': None, 'right': None}

        self.previous_data = {
            'left' : {'dist': float('inf'), 'time': 0.0},
            'right': {'dist': float('inf'), 'time': 0.0}
        }

    def _process_rgb_image(self, carla_image):
        """
         Convert CARLA image in an NumPy array BGR
        """
        array = np.frombuffer(carla_image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_image.height, carla_image.width, 4))  # RGBA
        array_bgr = array[:, :, :3]  # Prendi solo RGB (che è BGR in OpenCV)
        return array_bgr

    def _process_depth_image(self, carla_image):
        """
         Convert a CARLA depth image in a depth map (meters).
         Retrurn also a normalized image.
        """
        # I dati grezzi sono RGBA, dove la profondità è codificata in R, G, B
        array = np.frombuffer(carla_image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (carla_image.height, carla_image.width, 4))
        array = array.astype(np.float64)  # Usa float64 per evitare overflow

        # Distanza = (R + G * 256 + B * 256 * 256) / (256^3 - 1) * 1000
        distance = array[:, :, 2] + array[:, :, 1] * 256 + array[:, :, 0] * 256 * 256
        distance_meters = distance / (256 * 256 * 256 - 1) * 1000.0

        # Log-scale è migliore, ma per semplicità usiamo una normalizzazione lineare
        normalized_frame = np.clip(distance_meters / 100.0, 0.0, 1.0) * 255.0
        normalized_frame = normalized_frame.astype(np.uint8)
        # Converti in 3 canali (BGR) per poterci disegnare sopra
        display_frame = cv2.cvtColor(normalized_frame, cv2.COLOR_GRAY2BGR)

        return distance_meters, display_frame

    def _calculate_dynamic_ttc(self, depth_map, carla_image ,camera_side):
        """
         Calculate TTC in dynamic mode, based on distance variation
        """

        # --- NUOVA SOLUZIONE: ROI ---
        # Ottieni le dimensioni dell'immagine
        height = depth_map.shape[0]

        # Definisci la tua ROI: ignora il 25% superiore e il 25% inferiore
        roi_top = int(height * 0.25)
        roi_bottom = int(height * 0.75)

        # "Ritaglia" la mappa di profondità solo alla tua ROI
        roi_depth_map = depth_map[roi_top:roi_bottom, :]

        # Calcola la distanza minima SOLO in quella regione
        if roi_depth_map.size > 0:
            current_dist = np.min(roi_depth_map)
        else:
            current_dist = float('inf')  # Se la ROI è vuota, nessuna distanza
        # --- FINE SOLUZIONE ---

        #current_dist = np.min(depth_map)
        current_time = carla_image.timestamp

        prev_dist = self.previous_data[camera_side]['dist']
        prev_time = self.previous_data[camera_side]['time']

        ttc = float('inf')

        if prev_time > 0.0:
            delta_t = current_time -prev_time
            delta_d = prev_dist - current_dist
            if delta_t > 0.01:
                v_relative = delta_d/delta_t  #m/s
                if v_relative > 0.1:  #soglia per evitare rumore
                    ttc = current_dist / v_relative
                else:
                    #ci stiamo allontanando
                    ttc = float('inf')
        self.previous_data[camera_side]['dist'] = current_dist
        self.previous_data[camera_side]['time'] = current_time

        return current_dist, ttc

    def rear_cam_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.detected_objects['rear'] = self.detector.detect(np_image)
        self.current_frames['rear'] = np_image

    def left_cam_callback(self, image):
        """left depth camera callback"""
        depth_map, display_frame = self._process_depth_image(image)
        dist, ttc = self._calculate_dynamic_ttc(depth_map, image, 'left')

        # Salva entrambi i valori
        self.perception_data['left'] = {'dist': dist, 'ttc': ttc}
        self.current_frames['left'] = display_frame

    def right_cam_callback(self, image):
        """right depth camera callback"""
        depth_map, display_frame = self._process_depth_image(image)
        # Calcola dinamicamente dist e ttc
        dist, ttc = self._calculate_dynamic_ttc(depth_map, image, 'right')

        # Salva entrambi i valori
        self.perception_data['right'] = {'dist': dist, 'ttc': ttc}
        self.current_frames['right'] = display_frame

    def get_perception_data(self):
        """
        Return a dictionary
        {
            'rear': [lista_rilevamenti_yolo],
            'left': {'dist': N, 'ttc': N},
            'right': {'dist': N, 'ttc': N}
        }
        """
        # NOTA: non resettiamo i valori qui.
        # I callback li sovrascriveranno continuamente.
        # Se un oggetto scompare, il 'min_distance' diventerà 'inf'
        # e il calcolo del TTC risulterà 'inf'
        self.perception_data['rear'] = self.detected_objects['rear']
        return self.perception_data