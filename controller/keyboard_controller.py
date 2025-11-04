import  carla

class KeyboardController:
    """
    Basic controller for keyboard WASD

    - W: Accelerator (forward)
    - S: Accelerator (reverse)
    - A: Turn left
    - D: Turn right
    - Space bar: Brake
    - Q: Exit simulation (managed in main)
    """
    def __init__(self):
        self._control = carla.VehicleControl()
        self._throttle = 0.7
        self._steer_increment = 0.05
        self._steer = 0.0

    def parse_input(self, key):
        """
        Take a pressed button and update a Carla vehicle
        Return object updated
        """
        #reset
        self._control.throttle = 0.0
        self._control.brake = 0.0
        self._control.reverse = False

        #accelerazione, retro,  freno
        if key == ord('w'):
            self._control.throttle = self._throttle
        elif key == ord('s'):
            self._control.throttle = self._throttle
            self._control.reverse = True
        elif key == ord(' '):
            self._control.brake = 1.0

        #sterzo
        if key == ord('a'):
            # Sterza a sinistra
            self._steer = max(self._steer - self._steer_increment, -1.0)
        elif key == ord('d'):
            # Sterza a destra
            self._steer = min(self._steer + self._steer_increment, 1.0)
        else:
            # Auto-centra lo sterzo se non si preme A o D
            if self._steer > 0.0:
                self._steer = max(self._steer - self._steer_increment, 0.0)
            elif self._steer < 0.0:
                self._steer = min(self._steer + self._steer_increment, 0.0)

        self._control.steer = round(self._steer, 2)  # Arrotonda per stabilità

        # Restituisce l'oggetto di controllo
        return self._control

