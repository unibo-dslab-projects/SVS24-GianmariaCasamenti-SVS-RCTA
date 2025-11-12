from time import perf_counter
import numpy as np
import config
from ultralytics import YOLO
import time


class ObjectDetector:
    def __init__(self, model_path=config.YOLO_MODEL_PATH):
        print(f"OBJECT_DETECTOR [loading of YOLO model from {model_path}]")
        try:
            self.model = YOLO(model_path)
            self.class_names = self.model.names
            self.target_classes = {'person', 'bicycle', 'car', 'bus', 'truck'}

            self.target_class_indices = [
                k for k, v in self.class_names.items() if v in self.target_classes
            ]

            print(f"OBJECT_DETECTOR [YOLOv8 nano model loaded. Target classes: {self.target_classes}]")

            try:
                print("OBJECT_DETECTOR [Warming up model...]")
                dummy_img = np.zeros(
                    (config.CAMERA_IMAGE_HEIGHT, config.CAMERA_IMAGE_WIDTH, 3),
                    dtype=np.uint8
                )
                self.model.track(dummy_img, verbose=False, persist=False)
                print("OBJECT_DETECTOR [Model is ready.]")
            except Exception as e:
                print(f"OBJECT_DETECTOR [Warning: Model warm-up failed: {e}]")

        except Exception as e:
            print(f"OBJECT_DETECTOR [Error: {e}]")
            self.model = None

    def detect(self, rgb_image):
        if self.model is None:
            return []

        results = self.model.track(
            rgb_image,
            verbose=False,
            classes=self.target_class_indices,
            conf=0.5,
            persist=True,
            half = True  # Usa FP16 se hai GPU compatibile (velocizza ~2x)
        )

        if not results or results[0].boxes.id is None:
            return []

        #vectorizzazione
        boxes = results[0].boxes.cpu().numpy()
        detections = []

        for box in boxes:
            if box.id is None:
                continue

            detections.append({
                'id': int(box.id[0]),
                'class': self.class_names[int(box.cls[0])],
                'confidence': float(box.conf[0]),
                'bbox': box.xyxy[0].astype(int).tolist()
            })

        return detections