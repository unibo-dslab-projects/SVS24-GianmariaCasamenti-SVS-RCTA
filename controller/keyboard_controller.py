import carla
import pygame
import config


class KeyboardController:
    def __init__(self):
        self._control = carla.VehicleControl()
        self._throttle = 0.6
        self._steer_increment = 0.05
        self._steer = 0.0
        self._brake_strength = 1.0
        self._max_throttle = 0.8
        self._min_throttle = 0.3
        self._steer_damping = 0.15

    def parse_input(self, keys):
        self._control.throttle = 0.0
        self._control.brake = 0.0
        self._control.reverse = False

        forward = keys[pygame.K_w]
        backward = keys[pygame.K_s]
        left = keys[pygame.K_a]
        right = keys[pygame.K_d]
        brake = keys[pygame.K_SPACE]

        if forward and not backward:
            self._control.throttle = self._throttle
            self._control.reverse = False
        elif backward and not forward:
            self._control.throttle = self._throttle
            self._control.reverse = True

        if brake:
            self._control.brake = self._brake_strength
            self._control.throttle = 0.0

        if left and not right:
            self._steer = max(self._steer - self._steer_increment, -1.0)
        elif right and not left:
            self._steer = min(self._steer + self._steer_increment, 1.0)
        else:
            if abs(self._steer) > 0.01:
                self._steer *= (1.0 - self._steer_damping)
            else:
                self._steer = 0.0

        self._control.steer = round(self._steer, 3)
        self._control.hand_brake = False
        self._control.manual_gear_shift = False

        return self._control