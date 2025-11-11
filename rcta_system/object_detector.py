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

    def detect(self, bgr_image):
        if self.model is None:
            return []

        rgb_image = bgr_image[:, :, ::-1]

        results = self.model.track(
            rgb_image,
            verbose=False,
            classes=self.target_class_indices,
            conf=0.5,
            persist=True
        )

        detections = []

        if results[0].boxes.id is None:
            return []

        for box in results[0].boxes.cpu().numpy():
            if box.id is None:
                continue

            track_id = int(box.id[0])
            bbox = [int(coord) for coord in box.xyxy[0]]
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.class_names[class_id]
            detections.append({
                'id': track_id,
                'class': class_name,
                'confidence': conf,
                'bbox': bbox
            })
        return detections