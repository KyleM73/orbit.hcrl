from omni.isaac.lab.utils import configclass
from omni.isaac.lab_tasks.locomotion.velocity.velocity_env_cfg import LocomotionVelocityRoughEnvCfg

##
# Pre-defined configs
##
from isaac.lab.hcrl.assets import DRACO_CFG  # isort: skip


@configclass
class DracoRoughEnvCfg(LocomotionVelocityRoughEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        self.scene.robot = DRACO_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
        self.scene.height_scanner = None
        self.observations.policy.height_scan = None
        # scale down the terrains because the robot is small
        self.scene.terrain.terrain_type = "plane"
        self.scene.terrain.terrain_generator = None

        # reduce action scale
        self.actions.joint_pos.scale = 0.0

        # randomization
        self.randomization.push_robot = None
        self.randomization.add_base_mass.params["mass_range"] = (-0.0, 0.0)
        self.randomization.add_base_mass.params["asset_cfg"].body_names = "torso_link"
        self.randomization.base_external_force_torque.params["asset_cfg"].body_names = "torso_link"
        self.randomization.reset_robot_joints.params["position_range"] = (-0.0, 0.0)
        self.randomization.reset_base.params = {
            "pose_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "yaw": (-0, 0), "pitch": (0.25, 0.25)}, #0.27
            "velocity_range": {
                "x": (0.0, 0.0),
                "y": (0.0, 0.0),
                "z": (0.0, 0.0),
                "roll": (0.0, 0.0),
                "pitch": (0.0, 0.0),
                "yaw": (0.0, 0.0),
            },
        }

        # rewards
        self.rewards.undesired_contacts = None

        # terminations
        self.terminations.base_contact.params["sensor_cfg"].body_names = "torso_link"


@configclass
class DracoRoughEnvCfg_PLAY(DracoRoughEnvCfg):
    def __post_init__(self):
        # post init of parent
        super().__post_init__()

        # make a smaller scene for play
        self.scene.num_envs = 1
        self.scene.env_spacing = 2.5
        # spawn the robot randomly in the grid (instead of their terrain levels)
        self.scene.terrain.max_init_terrain_level = None
        # reduce the number of terrains to save memory
        if self.scene.terrain.terrain_generator is not None:
            self.scene.terrain.terrain_generator.num_rows = 5
            self.scene.terrain.terrain_generator.num_cols = 5
            self.scene.terrain.terrain_generator.curriculum = False

        # disable randomization for play
        self.observations.policy.enable_corruption = False
        # remove random pushing
        self.randomization.base_external_force_torque = None
        self.randomization.push_robot = None
