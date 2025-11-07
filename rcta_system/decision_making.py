import config
import time

class DecisionMaker:
    """
    Analyze perception data from all 3 RGBD channel and vehicle state,
    to determinate dangerous object
    """

    def __init__(self):
        print("DECISION_MAKER [initialized.]")
        self.ttc_threshold = config.TTC_THRESHOLD
        self.dist_threshold = config.DIST_THRESHOLD

    def evaluate(self, perception_data_all_channels, is_reversing):
        """
        Evaluates the danger based on data from all channels.

        :param perception_data_all_channels: Dictionary { “rear”: {...}, “left”: {...}, “right”: {...} }
        :param is_reversing: Boolean, true if the vehicle is reversing.
        :return: List of strings describing the hazards (e.g. [“rear:car”, “left:approaching”]).
        """
        dangerous_objects_list = []
        if not is_reversing:
            return []  # Restituisce una lista vuota

        for side, data in perception_data_all_channels.items():

            has_danger_alert_for_side = False

            # 1. Controllo DANGER (TTC basso)
            if data['ttc'] < self.ttc_threshold:
                min_dist_in_sector = data.get('dist', float('inf'))

                # --- FIX: INIZIALIZZARE LA VARIABILE QUI ---
                closest_obj_class = "unknown"
                # -------------------------------------------

                # Questo loop cerca di trovare il nome dell'oggetto più vicino
                for obj in data['objects']:
                    # Usiamo <= per assicurarci che venga assegnato se le distanze sono uguali
                    if obj.get('dist', float('inf')) <= min_dist_in_sector:
                        min_dist_in_sector = obj['dist']
                        closest_obj_class = obj['class']

                dangerous_objects_list.append({
                    "zone": side,
                    "alert_level": "danger",
                    # Ora 'closest_obj_class' esisterà sempre
                    "class": closest_obj_class if closest_obj_class != "unknown" else "FAST",
                    "distance": min_dist_in_sector,
                    "ttc": data['ttc']
                })
                has_danger_alert_for_side = True

            # 2. Controllo WARNING (Distanza bassa)
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

