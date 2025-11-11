import config
import time


class DecisionMaker:
    def __init__(self):
        print("DECISION_MAKER [initialized.]")
        self.ttc_threshold = config.TTC_THRESHOLD
        self.dist_threshold = config.DIST_THRESHOLD

    def evaluate(self, perception_data_all_channels, is_reversing):
        dangerous_objects_list = []
        if not is_reversing:
            return []

        for side, data in perception_data_all_channels.items():
            has_danger_alert_for_side = False

            if data['ttc'] < self.ttc_threshold:
                dangerous_obj = None
                for obj in data['objects']:
                    if abs(obj.get('ttc_obj', float('inf')) - data['ttc']) < 0.01:
                        dangerous_obj = obj
                        break

                if dangerous_obj is None:
                    for obj in data['objects']:
                        if obj.get('ttc_obj', float('inf')) < self.ttc_threshold:
                            dangerous_obj = obj
                            break

                if dangerous_obj:
                    obj_class = dangerous_obj['class']
                    obj_dist = dangerous_obj['dist']
                else:
                    obj_class = "FAST"
                    obj_dist = data.get('dist', float('inf'))

                dangerous_objects_list.append({
                    "zone": side,
                    "alert_level": "danger",
                    "class": obj_class,
                    "distance": obj_dist,
                    "ttc": data['ttc']
                })
                has_danger_alert_for_side = True

            if not has_danger_alert_for_side:
                closest_obj_in_zone = None
                min_dist_for_warning = self.dist_threshold

                for obj in data['objects']:
                    obj_dist = obj.get('dist', float('inf'))
                    if obj_dist < min_dist_for_warning:
                        min_dist_for_warning = obj_dist
                        closest_obj_in_zone = obj

                if closest_obj_in_zone:
                    dangerous_objects_list.append({
                        "zone": side,
                        "alert_level": "warning",
                        "class": closest_obj_in_zone['class'],
                        "distance": min_dist_for_warning,
                        "ttc": float('inf')
                    })

        return dangerous_objects_list