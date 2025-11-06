from symtable import Class

import carla
import config

class SensorManager:
    """Manages creation and configuration about sensors"""
    def __init__(self, world, actor_list):
        self.world = world
        self.actor_list = actor_list
        self.blueprint_library = world.get_blueprint_library()

    def setup_rcta_cameras(self, parent_vehicle):
        """ Creates and fittings 3 cameras for the system RCTA
        :param parent_vehicle: vehicle actor to attach cameras
        :return: tupla of 3 RGBD sensors (rear_rgb_cam, rear_depth_cam,left_rgb_cam, left_depth_cam,
        right_rgb_cam, right_depth_cam)
        """
        rgb_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        rgb_camera_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
        rgb_camera_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
        rgb_camera_bp.set_attribute('fov', config.CAMERA_FOV)

        depth_camera_bp = self.blueprint_library.find('sensor.camera.depth')
        depth_camera_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
        depth_camera_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
        depth_camera_bp.set_attribute('fov', config.CAMERA_FOV)

        print("SENSOR_MANAGER [Spawning REAR camera]")
        rear_rgb_cam = self.world.try_spawn_actor(
            rgb_camera_bp,
            config.REAR_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        rear_depth_cam = self.world.try_spawn_actor(
            depth_camera_bp,
            config.REAR_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if rear_rgb_cam and rear_depth_cam:
            self.actor_list.extend([rear_rgb_cam, rear_depth_cam])
            print(f"SENSOR_MANAGER [REAR camera spawned successfully]")
        else:
            print(f"SENSOR_MANAGER [ERROR: Spawn REAR camera failed]")

        print("SENSOR_MANAGER [Spawning LEFT camera]")
        rgb_camera_bp.set_attribute('fov', config.CAMERA_FOV)
        left_rgb_cam = self.world.try_spawn_actor(
            rgb_camera_bp,
            config.LEFT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        depth_camera_bp.set_attribute('fov', config.CAMERA_FOV)
        left_depth_cam = self.world.try_spawn_actor(
            depth_camera_bp,
            config.LEFT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if left_rgb_cam and left_depth_cam:
            self.actor_list.extend([left_rgb_cam, left_depth_cam])
            print(f"SENSOR_MANAGER [LEFT camera spawned successfully]")
        else:
            print(f"SENSOR_MANAGER [ERROR: Spawn LEFT camera failed]")


        print("SENSOR_MANAGER [Spawning RIGHT camera]")
        rgb_camera_bp.set_attribute('fov', config.CAMERA_FOV)
        right_rgb_cam = self.world.try_spawn_actor(
            rgb_camera_bp,
            config.RIGHT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        depth_camera_bp.set_attribute('fov', config.CAMERA_FOV)
        right_depth_cam = self.world.try_spawn_actor(
            depth_camera_bp,
            config.RIGHT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if right_rgb_cam and right_depth_cam:
            self.actor_list.extend([right_rgb_cam, right_depth_cam])
            print(f"SENSOR_MANAGER [RIGHT camera spawned successfully]")
        else:
            print(f"SENSOR_MANAGER [ERROR: Spawn RIGHT camera failed]")

        return (
            rear_rgb_cam, rear_depth_cam,
            left_rgb_cam, left_depth_cam,
            right_rgb_cam, right_depth_cam
        )


