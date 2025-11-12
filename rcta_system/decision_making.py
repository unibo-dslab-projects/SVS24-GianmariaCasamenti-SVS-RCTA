import config
import time


class DecisionMaker:
    def __init__(self):
        print("DECISION_MAKER [initialized.]")
        self.ttc_threshold = config.TTC_THRESHOLD
        self.dist_threshold = config.DIST_THRESHOLD

    def evaluate(self, perception_data_all_channels, is_reversing):
        if not is_reversing:
            return []

        dangerous_objects_list = []

        for side, data in perception_data_all_channels.items():
            # Se TTC pericoloso → DANGER
            if data['ttc'] < self.ttc_threshold:
                # Trova l'oggetto con il TTC minimo
                dangerous_obj = min(
                    data['objects'],
                    key=lambda obj: obj.get('ttc_obj', float('inf')),
                    default=None
                )

                if dangerous_obj:
                    dangerous_objects_list.append({
                        "zone": side,
                        "alert_level": "danger",
                        "class": dangerous_obj['class'],
                        "distance": dangerous_obj['dist'],
                        "ttc": dangerous_obj['ttc_obj']
                    })
                else:
                    # Fallback: oggetto veloce non tracciato
                    dangerous_objects_list.append({
                        "zone": side,
                        "alert_level": "danger",
                        "class": "FAST",
                        "distance": data['dist'],
                        "ttc": data['ttc']
                    })
                continue  # Skip warning check per questa zona

            # Se nessun TTC pericoloso ma oggetto vicino → WARNING
            if data['dist'] < self.dist_threshold:
                closest_obj = min(
                    data['objects'],
                    key=lambda obj: obj.get('dist', float('inf')),
                    default=None
                )

                if closest_obj:
                    dangerous_objects_list.append({
                        "zone": side,
                        "alert_level": "warning",
                        "class": closest_obj['class'],
                        "distance": closest_obj['dist'],
                        "ttc": float('inf')
                    })

        return dangerous_objects_list