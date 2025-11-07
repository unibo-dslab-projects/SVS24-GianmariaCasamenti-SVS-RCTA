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
            # data['ttc'] ora è il min_ttc_obj di quel settore
            if data['ttc'] < self.ttc_threshold:

                # --- MODIFICA: Trova l'oggetto che ha causato il DANGER ---
                dangerous_obj = None
                for obj in data['objects']:
                    # Cerca l'oggetto il cui TTC ha triggerato l'allarme
                    # Usiamo una piccola tolleranza per i float
                    if abs(obj.get('ttc_obj', float('inf')) - data['ttc']) < 0.01:
                        dangerous_obj = obj
                        break

                # Fallback: se non lo troviamo, prendi il primo oggetto sotto soglia
                if dangerous_obj is None:
                    for obj in data['objects']:
                        if obj.get('ttc_obj', float('inf')) < self.ttc_threshold:
                            dangerous_obj = obj
                            break

                # Ora abbiamo l'oggetto specifico che causa il pericolo
                if dangerous_obj:
                    obj_class = dangerous_obj['class']
                    obj_dist = dangerous_obj['dist']
                else:
                    # Fallback estremo (dovuto a discrepanze di float)
                    obj_class = "FAST"  # Classe generica per oggetto veloce
                    obj_dist = data.get('dist', float('inf'))
                # ----------------------------------------------------

                dangerous_objects_list.append({
                    "zone": side,
                    "alert_level": "danger",
                    "class": obj_class,  # Ora è la classe dell'oggetto pericoloso
                    "distance": obj_dist,  # La sua distanza
                    "ttc": data['ttc']
                })
                has_danger_alert_for_side = True

            # 2. Controllo WARNING (Distanza bassa)
            # Questa logica era già corretta e non ha bisogno di modifiche
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