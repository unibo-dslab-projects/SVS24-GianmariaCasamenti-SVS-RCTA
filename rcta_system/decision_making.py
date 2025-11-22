import config


class DecisionMaker:
    """
    Decision maker for a single RCTA zone.
    Each pipeline has its own DecisionMaker instance.
    """

    def __init__(self, zone_name):
        """
        Args:
            zone_name: "rear", "left", or "right"
        """
        self.zone_name = zone_name
        self.ttc_threshold = config.TTC_THRESHOLD
        self.dist_threshold = config.DIST_THRESHOLD
        print(
            f"DECISION_MAKER-{zone_name.upper()} [Initialized with TTC={self.ttc_threshold}s, DIST={self.dist_threshold}m]")

    def evaluate(self, perception_data):
        """
        Evaluate perception data for this zone and return alerts if needed.

        Args:
            perception_data: Dict with 'dist', 'ttc', 'objects'

        Returns:
            List of dangerous objects (empty if safe)
        """
        dangerous_objects_list = []

        # Check TTC threshold (DANGER)
        if perception_data['ttc'] < self.ttc_threshold:
            # Find object with minimum TTC
            dangerous_obj = min(
                perception_data['objects'],
                key=lambda obj: obj.get('ttc_obj', float('inf')),
                default=None
            )

            if dangerous_obj:
                dangerous_objects_list.append({
                    "zone": self.zone_name,
                    "alert_level": "danger",
                    "class": dangerous_obj['class'],
                    "distance": dangerous_obj['dist'],
                    "ttc": dangerous_obj['ttc_obj']
                })
            else:
                # Fallback: fast untracked object
                dangerous_objects_list.append({
                    "zone": self.zone_name,
                    "alert_level": "danger",
                    "class": "FAST",
                    "distance": perception_data['dist'],
                    "ttc": perception_data['ttc']
                })

            return dangerous_objects_list  # Return immediately, skip warning check

        # Check distance threshold (WARNING)
        if perception_data['dist'] < self.dist_threshold:
            # Find closest object
            closest_obj = min(
                perception_data['objects'],
                key=lambda obj: obj.get('dist', float('inf')),
                default=None
            )

            if closest_obj:
                dangerous_objects_list.append({
                    "zone": self.zone_name,
                    "alert_level": "warning",
                    "class": closest_obj['class'],
                    "distance": closest_obj['dist'],
                    "ttc": float('inf')
                })

        return dangerous_objects_list