import numpy as np
import config
from ultralytics import YOLO



class ObjectDetector:
    """
    Wrapper for the model YOLOv8
    """
    def __init__(self, model_path = config.YOLO_MODEL_PATH):
        """
        Charges the model from the path
        """
        print(f"loading of YOLO model from {model_path}")
        try:
            self.model = YOLO(model_path)
            self.class_names = self.model.names
            self.target_classes = {'person', 'bicycle', 'car', 'bus', 'truck'}

            # Converti i nomi delle classi target in indici numerici
            self.target_class_indices = [
                k for k, v in self.class_names.items() if v in self.target_classes
            ]

            print(f"YOLOv8 model loaded. Target classes: {self.target_classes}")

        except Exception as e:
            print(f"ERROR: Yolov8 not found from:  {model_path}.")
            print(f"Error: {e}")
            self.model = None

    def detect(self, bgr_image):
        """
        Catalogues a single image, NumPy format BGR

        :param brg_image: image in NumPy format
        :return: List of detected dictionary
        """
        if self.model is None:
            return[]

        # YOLO = RGB --> OpenCV (e CARLA) usa BGR.
        rgb_image = bgr_image[:, :, ::-1]

        # Esegui l'inferenza
        # Filtriamo già qui per classi e confidenza per essere più veloci
        results = self.model.predict(
            rgb_image,
            verbose=False,
            classes=self.target_class_indices,
            conf=0.5
        )

        detections = []

        # Estrai i risultati
        # results[0] contiene i rilevamenti per la prima (e unica) immagine
        for box in results[0].boxes.cpu().numpy():
            # Estrai le coordinate del Bounding Box
            bbox = [int(coord) for coord in box.xyxy[0]]

            # Estrai la confidenza
            conf = float(box.conf[0])

            # Estrai l'ID della classe e ottieni il nome
            class_id = int(box.cls[0])
            class_name = self.class_names[class_id]

            detections.append({
                'class': class_name,
                'confidence': conf,
                'bbox': bbox
            })

        return detections
