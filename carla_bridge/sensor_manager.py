import carla
import config


class SensorManager:
    """
    Manages camera sensors for RCTA system.
    In async mode, sensors update at their natural rate.
    """
    def __init__(self, world, actor_list):
        self.world = world
        self.actor_list = actor_list
        self.blueprint_library = world.get_blueprint_library()

    def setup_rcta_cameras(self, parent_vehicle):
        """
        Setup RGB and Depth cameras for RCTA (Rear Cross Traffic Alert).
        Creates 3 pairs of cameras: REAR, LEFT, RIGHT.
        """
        # RGB camera blueprint
        rgb_camera_bp = self.blueprint_library.find('sensor.camera.rgb')
        rgb_camera_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
        rgb_camera_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
        rgb_camera_bp.set_attribute('fov', config.CAMERA_FOV)

        # Depth camera blueprint
        depth_camera_bp = self.blueprint_library.find('sensor.camera.depth')
        depth_camera_bp.set_attribute('image_size_x', str(config.CAMERA_IMAGE_WIDTH))
        depth_camera_bp.set_attribute('image_size_y', str(config.CAMERA_IMAGE_HEIGHT))
        depth_camera_bp.set_attribute('fov', config.CAMERA_FOV)

        # Spawn REAR cameras
        print("SENSOR_MANAGER [Spawning REAR cameras]")
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
            print(f"SENSOR_MANAGER [REAR cameras spawned successfully]")
        else:
            print(f"SENSOR_MANAGER [ERROR: REAR cameras spawn failed]")

        # Spawn LEFT cameras
        print("SENSOR_MANAGER [Spawning LEFT cameras]")
        left_rgb_cam = self.world.try_spawn_actor(
            rgb_camera_bp,
            config.LEFT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        left_depth_cam = self.world.try_spawn_actor(
            depth_camera_bp,
            config.LEFT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if left_rgb_cam and left_depth_cam:
            self.actor_list.extend([left_rgb_cam, left_depth_cam])
            print(f"SENSOR_MANAGER [LEFT cameras spawned successfully]")
        else:
            print(f"SENSOR_MANAGER [ERROR: LEFT cameras spawn failed]")

        # Spawn RIGHT cameras
        print("SENSOR_MANAGER [Spawning RIGHT cameras]")
        right_rgb_cam = self.world.try_spawn_actor(
            rgb_camera_bp,
            config.RIGHT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        right_depth_cam = self.world.try_spawn_actor(
            depth_camera_bp,
            config.RIGHT_CAMERA_TRANSFORM,
            attach_to=parent_vehicle
        )
        if right_rgb_cam and right_depth_cam:
            self.actor_list.extend([right_rgb_cam, right_depth_cam])
            print(f"SENSOR_MANAGER [RIGHT cameras spawned successfully]")
        else:
            print(f"SENSOR_MANAGER [ERROR: RIGHT cameras spawn failed]")

        return (
            rear_rgb_cam, rear_depth_cam,
            left_rgb_cam, left_depth_cam,
            right_rgb_cam, right_depth_cam
        )