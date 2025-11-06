import numpy as np
from rcta_system.object_detector import ObjectDetector
import cv2

class RctaPerception:
    """
    Manages vision-only perception for the rcta system.
    Handles 3 RGBD pairs (6 sensors total).
    """
    def __init__(self):
        print("PERCEPTION [Starting RctaPerception]")
        self.detector = ObjectDetector()
        # Dati processati (distanze, ttc)
        self.perception_data = {
            'rear': {'dist': float('inf'), 'ttc': float('inf')},
            'left': {'dist': float('inf'), 'ttc': float('inf')},
            'right': {'dist': float('inf'), 'ttc': float('inf')}
        }
        # Oggetti rilevati da YOLO
        self.detected_objects = {
            'rear': [],
            'left': [],
            'right': []
        }
        # Frame per visualizzazione RGB
        self.current_rgb_frames = {
            'rear': None,
            'left': None,
            'right': None
        }
        # Frame per visualizzazione Depth (opzionale per questa fase, ma lo manteniamo)
        self.current_depth_frames = {
            'rear': None,
            'left': None,
            'right': None
        }
        self.previous_data = {
            'rear': {'dist': float('inf'), 'time': 0.0},  # Aggiunto rear
            'left': {'dist': float('inf'), 'time': 0.0},
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
        current_dist = 10
        ttc = 5
        return current_dist, ttc

    # CALLBACKS RGB
    def rear_rgb_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.detected_objects['rear'] = self.detector.detect(np_image)
        self.current_rgb_frames['rear'] = np_image

    def left_rgb_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.detected_objects['left'] = self.detector.detect(np_image)
        self.current_rgb_frames['left'] = np_image

    def right_rgb_callback(self, image):
        np_image = self._process_rgb_image(image)
        self.detected_objects['right'] = self.detector.detect(np_image)
        self.current_rgb_frames['right'] = np_image

    #CALLBACKS DEPTH
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
        # Uniamo i dati: oggetti rilevati (RGB) + dati metrici (Depth)
        final_data = {}
        for side in ['rear', 'left', 'right']:
             final_data[side] = {
                 'objects': self.detected_objects[side],
                 'dist': self.perception_data[side]['dist'],
                 'ttc': self.perception_data[side]['ttc']
             }
        return final_data