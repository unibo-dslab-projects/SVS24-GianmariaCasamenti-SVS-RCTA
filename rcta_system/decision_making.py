import config


class DecisionMaker:
    def __init__(self, zone_name):
        self.zone_name = zone_name
        self.ttc_threshold = config.TTC_THRESHOLD
        self.dist_threshold = config.DIST_THRESHOLD
        print(
            f"DECISION_MAKER-{zone_name.upper()} [Initialized with TTC={self.ttc_threshold}s, DIST={self.dist_threshold}m]")

    def evaluate(self, fused_objects):
        if not fused_objects:
            return []

        dangerous_objects_list = []

        # oggetto con TTC minimo
        min_ttc_obj = min(
            fused_objects,
            key=lambda obj: obj.get('ttc_obj', float('inf'))
        )

        # Check DANGER (TTC)
        if min_ttc_obj['ttc_obj'] < self.ttc_threshold:
            dangerous_objects_list.append({
                "zone": self.zone_name,
                "alert_level": "danger",
                "class": min_ttc_obj['class'],
                "distance": min_ttc_obj['dist'],
                "ttc": min_ttc_obj['ttc_obj']
            })
            print(f"[ALERT] {min_ttc_obj}")
            return dangerous_objects_list

        # Check distanza
        min_dist_obj = min(
            fused_objects,
            key=lambda obj: obj.get('dist', float('inf'))
        )

        if min_dist_obj['dist'] < self.dist_threshold:
            dangerous_objects_list.append({
                "zone": self.zone_name,
                "alert_level": "warning",
                "class": min_dist_obj['class'],
                "distance": min_dist_obj['dist'],
                "ttc": min_dist_obj['ttc_obj']
            })

        return dangerous_objects_list