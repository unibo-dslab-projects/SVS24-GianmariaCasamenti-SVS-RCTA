import config

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
        dangerous_alerts = []
        if not is_reversing:
            return []

        for side, data in perception_data_all_channels.items():
            if data['ttc'] < self.ttc_threshold:
                dangerous_alerts.append(f"{side}:approaching_fast")

            elif data['dist'] < self.dist_threshold:
                closest_obj_type = "unknown"
                min_obj_dist = float('inf')

                for obj in data['objects']:
                    # Se l'oggetto ha una distanza valida ed è il più vicino finora
                    if obj.get('dist', float('inf')) < min_obj_dist:
                        min_obj_dist = obj['dist']
                        closest_obj_type = obj['class']

                if min_obj_dist < self.dist_threshold:
                    dangerous_alerts.append(f"{side}:{closest_obj_type}_near")

        return list(set(dangerous_alerts))