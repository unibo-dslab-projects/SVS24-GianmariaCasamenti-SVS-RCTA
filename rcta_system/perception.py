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

        self.perception_data = {'rear': [], 'left': float('inf'), 'right': float('inf')}
        self.detected_objects = {'rear': [], 'left': [], 'right': []}
        self.current_frames = {'rear': None, 'left': None, 'right': None}

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

    def rear_cam_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.detected_objects['rear'] = self.detector.detect(np_image)
        self.current_frames['rear'] = np_image

    def left_cam_callback(self, image):
        """left depth camera callback"""
        depth_map, display_frame = self._process_depth_image(image)
        # Trova la distanza minima rilevata da questa telecamera
        min_distance = np.min(depth_map)
        self.perception_data['left'] = min_distance
        self.current_frames['left'] = display_frame

    def right_cam_callback(self, image):
        """right depth camera callback"""
        depth_map, display_frame = self._process_depth_image(image)
        # Trova la distanza minima rilevata da questa telecamera
        min_distance = np.min(depth_map)
        self.perception_data['right'] = min_distance
        self.current_frames['right'] = display_frame

    def get_perception_data(self):
        """
        Restituisce un dizionario con tutti i dati di percezione:
        {
            'rear': [lista_rilevamenti_yolo],
            'left': distanza_minima_float,
            'right': distanza_minima_float
        }
        """
        return self.perception_data