from symtable import Class

import carla
import config

class SensorManager:
    """
    manages creation and configuration about sensors
    """
    def __init__(self, world, actor_list):
        self.world = world
        self.actor_list = actor_list
        self.blueprint_library = world.get_blueprint_library()

    def setup_rcta_cameras(self, parent_vehicle):
        """
        creates and fittings 3 cameras for the system RCTA

        :param parent_vehicle: vehicle actor to attach cameras
        :return: tupla of 3 sensors (rear_cam, left_cam, right_cam)
        """
        rear_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        rear_camera_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
        rear_camera_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
        rear_camera_bp.set_attribute('fov', config.REAR_CAMERA_FOV)

        rcta_camera_bp = self.blueprint_library.find('sensor.camera.depth')
        rcta_camera_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
        rcta_camera_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
        rcta_camera_bp.set_attribute('fov', config.RCTA_CAMERA_FOV)

        rear_camera = self.world.try_spawn_actor(
                rear_camera_bp,
                config.REAR_CAMERA_TRANSFORM,
                attach_to = parent_vehicle
            )
        if rear_camera:
            self.actor_list.append(rear_camera)
            print(f"rear camera spawned with successfully")
        else:
            print(f"Error, spawn rear camera failed")

        right_rcta_camera = self.world.try_spawn_actor(
            rcta_camera_bp,
            config.RCTA_RIGHT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if right_rcta_camera:
            self.actor_list.append(right_rcta_camera)
            print(f"right camera spawned with successfully")
        else:
            print(f"Error, spawn right camera failed")

        left_rcta_camera = self.world.try_spawn_actor(
            rcta_camera_bp,
            config.RCTA_LEFT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if left_rcta_camera:
            self.actor_list.append(left_rcta_camera)
            print(f"left camera spawned with successfully")
        else:
            print(f"Error, spawn left camera failed")

        return(
           rear_camera,
           left_rcta_camera,
           right_rcta_camera
        )


