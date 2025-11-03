import numpy as np
import config

class DecisionMaker:
    """
     Analyze perception datas (Yolo and depth) and vehicle state to determinate
     dangerous object detected
    """

    def __init__(self):
        print("DecisionMaker initialized.")
        self.ttc_threshold = config.TTC_THRESHOLD
        self.cross_speed = config.CROSS_TRAFFIC_SPEED_MS  # m/s

    def evaluate(self, perception_data, is_reversing):
        """
        Main decision-making function

        :param perception_data: Dictionary of RctaPerception
                                {'rear': [], 'left': float, 'right': float}
        :param is_reversing: Boolean
        :return: List of string for the dangerous classes (es. ['car', 'depth_left'])
        """
        dangerous_alerts = []
        if not is_reversing:
            return []

        #rear camera
        rear_detections = perception_data.get('rear', [])
        if rear_detections:
            rear_classes = {obj['class'] for obj in rear_detections}
            dangerous_alerts.extend(list(rear_classes))

        # Left depth camera
        left_distance = perception_data.get('left', float('inf'))
        if left_distance < 100.0:
            # TTC = Distanza (m) / Velocità (m/s)
            ttc_left = left_distance / self.cross_speed

            if ttc_left < self.ttc_threshold:
                # print(f"PERICOLO SINISTRA: TTC {ttc_left:.2f}s")
                dangerous_alerts.append("depth_left")

        # Right depth camera
        right_distance = perception_data.get('right', float('inf'))
        if right_distance < 100.0:
            ttc_right = right_distance / self.cross_speed

            if ttc_right < self.ttc_threshold:
                # print(f"PERICOLO DESTRA: TTC {ttc_right:.2f}s")
                dangerous_alerts.append("depth_right")

        return list(set(dangerous_alerts))