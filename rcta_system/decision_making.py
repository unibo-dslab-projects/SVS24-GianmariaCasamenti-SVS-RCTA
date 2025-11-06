import config


class DecisionMaker:
    """
    Analizza i dati di percezione (da tutti e 3 i canali RGBD) e lo stato del veicolo
    per determinare se ci sono oggetti pericolosi.
    """

    def __init__(self):
        print("DecisionMaker initialized.")
        self.ttc_threshold = config.TTC_THRESHOLD
        # Soglia di distanza minima per considerare un oggetto pericoloso anche senza TTC basso
        self.min_dist_threshold = 5.0

    def evaluate(self, perception_data_all_channels, is_reversing):
        """
        Valuta il pericolo basandosi sui dati di tutti i canali.

        :param perception_data_all_channels: Dizionario { 'rear': {...}, 'left': {...}, 'right': {...} }
        :param is_reversing: Booleano, true se il veicolo sta andando in retromarcia.
        :return: Lista di stringhe che descrivono i pericoli (es. ['rear:car', 'left:approaching']).
        """
        dangerous_alerts = []

        # Se non siamo in retromarcia, per ora assumiamo nessun pericolo RCTA
        if not is_reversing:
            return []

        for side, data in perception_data_all_channels.items():
            # 1. Controllo TTC del settore (veicoli in avvicinamento veloce)
            if data['ttc'] < self.ttc_threshold:
                dangerous_alerts.append(f"{side}:approaching_fast")

            # 2. Controllo oggetti statici o lenti molto vicini
            # Se la distanza minima del settore è inferiore alla soglia
            elif data['dist'] < self.min_dist_threshold:
                # Cerchiamo quale tipo di oggetto è vicino
                closest_obj_type = "unknown"
                min_obj_dist = float('inf')

                for obj in data['objects']:
                    # Se l'oggetto ha una distanza valida ed è il più vicino finora
                    if obj.get('dist', float('inf')) < min_obj_dist:
                        min_obj_dist = obj['dist']
                        closest_obj_type = obj['class']

                if min_obj_dist < self.min_dist_threshold:
                    dangerous_alerts.append(f"{side}:{closest_obj_type}_near")

        return list(set(dangerous_alerts))