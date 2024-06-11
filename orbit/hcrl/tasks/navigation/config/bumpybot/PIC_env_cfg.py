# Copyright (c) 2022-2024, The ORBIT Project Developers.
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import math
from dataclasses import MISSING

import omni.isaac.orbit.sim as sim_utils
from omni.isaac.orbit.assets import ArticulationCfg, AssetBaseCfg, RigidObjectCfg
from omni.isaac.orbit.envs import BaseEnvCfg, RLTaskEnvCfg
from omni.isaac.orbit.managers import CurriculumTermCfg as CurrTerm
from omni.isaac.orbit.managers import ObservationGroupCfg as ObsGroup
from omni.isaac.orbit.managers import ObservationTermCfg as ObsTerm
from omni.isaac.orbit.managers import EventTermCfg as EventTerm
from omni.isaac.orbit.managers import RewardTermCfg as RewTerm
from omni.isaac.orbit.managers import SceneEntityCfg
from omni.isaac.orbit.managers import TerminationTermCfg as DoneTerm
from omni.isaac.orbit.scene import InteractiveSceneCfg
from omni.isaac.orbit.sensors import ContactSensorCfg, RayCasterCfg, patterns
from omni.isaac.orbit.terrains import TerrainImporterCfg
from omni.isaac.orbit.envs import ViewerCfg
from omni.isaac.orbit.utils import configclass
from omni.isaac.orbit.utils.noise import AdditiveUniformNoiseCfg as Unoise
from omni.isaac.orbit.utils.noise import AdditiveGaussianNoiseCfg as Gnoise
from omni.isaac.orbit.utils.assets import ISAAC_NUCLEUS_DIR

import omni.isaac.orbit.envs.mdp as mdp
import orbit.hcrl.tasks.navigation.mdp as hcrl_mdp

##
# Pre-defined configs
##
from orbit.hcrl.assets import (
    BUMPYBOT_CFG, CUBE_CFG, CUBE0_CFG, CUBE1_CFG, CUBE2_CFG, CUBE3_CFG,
    CAR_CFG, SPHERE_CFG, UNICYCLE_CFG
  )  # isort: skip

##
# Scene definition
##


@configclass
class UnicycleSceneCfg(InteractiveSceneCfg):
    """Configuration for the terrain scene with a legged robot."""

    # ground terrain
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane", #usd
        terrain_generator=None,
        max_init_terrain_level=5,
        collision_group=-1,
        usd_path=None,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
        ),
        visual_material=sim_utils.MdlFileCfg(
            mdl_path="{NVIDIA_NUCLEUS_DIR}/Materials/Base/Architecture/Shingles_01.mdl",
            project_uvw=True,
        ),
        debug_vis=True,
    )
    # robots
    robot: ArticulationCfg = UNICYCLE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    # objects
    box0: RigidObjectCfg = CUBE0_CFG.replace(prim_path="{ENV_REGEX_NS}/Box0")
    box1: RigidObjectCfg = CUBE1_CFG.replace(prim_path="{ENV_REGEX_NS}/Box1")
    # lights
    light = AssetBaseCfg(
        prim_path="/World/light",
        spawn=sim_utils.DistantLightCfg(color=(0.75, 0.75, 0.75), intensity=3000.0),
    )
    sky_light = AssetBaseCfg(
        prim_path="/World/skyLight",
        spawn=sim_utils.DomeLightCfg(color=(0.13, 0.13, 0.13), intensity=1000.0),
    )

@configclass
class IntegratorSceneCfg(UnicycleSceneCfg):
    # robots
    robot: ArticulationCfg = SPHERE_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    box0 = CUBE2_CFG.replace(prim_path="{ENV_REGEX_NS}/Box0")
    box1 = None

@configclass
class CarSceneCfg(UnicycleSceneCfg):
    # robots
    robot: ArticulationCfg = CAR_CFG.replace(prim_path="{ENV_REGEX_NS}/Robot")
    box0 = CUBE3_CFG.replace(prim_path="{ENV_REGEX_NS}/Box0")
    box1 = CUBE3_CFG.replace(prim_path="{ENV_REGEX_NS}/Box1")

##
# MDP settings
##

@configclass
class ActionsCfg:
    """Action specifications for the MDP."""
    velocity = hcrl_mdp.HolonomicActionCfg(
        asset_name="robot",
        x_joint_name=["dummy_prismatic_x_joint"],
        y_joint_name=["dummy_prismatic_y_joint"],
        yaw_joint_name=["dummy_revolute_yaw_joint"],
        body_name=["robot_link"],
        scale=(1.0, 0.0, 1.0), offset=(0.0, 0.0, 0.0),
    )

    """pose = mdp.JointPositionActionCfg(
        asset_name="robot",
        joint_names=["dummy_prismatic_x_joint","dummy_prismatic_y_joint","dummy_revolute_yaw_joint"],
        scale=0.0, offset=0.0,
        use_default_offset=False
    )"""

@configclass
class ObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy group."""

        # observation terms (order preserved)
        base_pose = ObsTerm(func=hcrl_mdp.body_pos_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        #base_pose = ObsTerm(func=mdp.joint_pos_rel,
        #    params={"asset_cfg": SceneEntityCfg("robot", joint_names=["dummy_prismatic_x_joint", "dummy_prismatic_y_joint", "dummy_revolute_yaw_joint"])})
        base_heading = ObsTerm(func=hcrl_mdp.body_heading_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        base_lin_vel = ObsTerm(func=hcrl_mdp.body_lin_vel_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        base_ang_vel = ObsTerm(func=hcrl_mdp.body_ang_vel_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        box0_pose = ObsTerm(func=hcrl_mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("box0")})
        box1_pose = ObsTerm(func=hcrl_mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("box1")})

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()


@configclass
class IntegratorObservationsCfg:
    """Observation specifications for the MDP."""

    @configclass
    class PolicyCfg(ObsGroup):
        """Observations for policy group."""

        # observation terms (order preserved)
        base_pose = ObsTerm(func=hcrl_mdp.body_pos_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        #base_pose = ObsTerm(func=mdp.joint_pos_rel,
        #    params={"asset_cfg": SceneEntityCfg("robot", joint_names=["dummy_prismatic_x_joint", "dummy_prismatic_y_joint", "dummy_revolute_yaw_joint"])})
        base_heading = ObsTerm(func=hcrl_mdp.body_heading_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        base_lin_vel = ObsTerm(func=hcrl_mdp.body_lin_vel_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        base_ang_vel = ObsTerm(func=hcrl_mdp.body_ang_vel_w, 
            params={"asset_cfg": SceneEntityCfg("robot", body_names="robot_link")})
        box0_pose = ObsTerm(func=hcrl_mdp.root_pos_w, params={"asset_cfg": SceneEntityCfg("box0")})

        def __post_init__(self):
            self.enable_corruption = False
            self.concatenate_terms = True

    # observation groups
    policy: PolicyCfg = PolicyCfg()

@configclass
class UnicycleEventsCfg:
    """Configuration for events."""

    # reset
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-4, -4), "y": (-4, -4), "yaw": (-0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "yaw": (-0.0, 0.0)},
        },
    )

    reset_box0 = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "z": (0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0)},
            "asset_cfg": SceneEntityCfg("box0")
        },
    )

    reset_box1 = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "z": (0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0)},
            "asset_cfg": SceneEntityCfg("box1")
        },
    )

@configclass
class IntegratorEventsCfg:
    # reset
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-3, -3), "y": (3, 3), "yaw": (-0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "yaw": (-0.0, 0.0)},
        },
    )

    reset_box0 = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "z": (0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0)},
            "asset_cfg": SceneEntityCfg("box0")
        },
    )

@configclass
class CarEventsCfg:
    """Configuration for events."""

    # reset
    reset_base = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-5, -5), "y": (-5, -5), "yaw": (-0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0), "yaw": (-0.0, 0.0)},
        },
    )

    reset_box0 = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-1.25, -1.25), "y": (-1.25, -1.25), "z": (0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0)},
            "asset_cfg": SceneEntityCfg("box0")
        },
    )

    reset_box1 = EventTerm(
        func=mdp.reset_root_state_uniform,
        mode="reset",
        params={
            "pose_range": {"x": (-2.75, -2.75), "y": (-2.75, -2.75), "z": (0.0, 0.0)},
            "velocity_range": {"x": (-0.0, 0.0), "y": (-0.0, 0.0)},
            "asset_cfg": SceneEntityCfg("box1")
        },
    )

@configclass
class CommandsCfg:
    pass

@configclass
class RewardsCfg:
    pass

@configclass
class CurriculumCfg:
    """Curriculum terms for the MDP."""
    pass

@configclass
class TerminationsCfg:
    """Termination terms for the MDP."""

    time_out = DoneTerm(func=mdp.time_out, time_out=True)

##
# Environment configuration
##

@configclass
class UnicycleEnvCfg(RLTaskEnvCfg):
    """Configuration for the locomotion velocity-tracking environment."""

    # Scene settings
    scene: UnicycleSceneCfg = UnicycleSceneCfg(num_envs=1, env_spacing=5.0, replicate_physics=True)
    viewer: ViewerCfg = ViewerCfg(eye=(0, -10, 10), origin_type="world") # side
    #viewer: ViewerCfg = ViewerCfg(eye=(0.0, 0.0, 20.0), origin_type="world") # top down
    # MDP settings
    events: UnicycleEventsCfg = UnicycleEventsCfg()
    observations: ObservationsCfg = ObservationsCfg()
    actions: ActionsCfg = ActionsCfg()
    commands: CommandsCfg = CommandsCfg()
    terminations: TerminationsCfg = TerminationsCfg()
    rewards: RewardsCfg = RewardsCfg()
    curriculum: CurriculumCfg = CurriculumCfg()

    def __post_init__(self):
        """Post initialization."""
        # general settings
        self.decimation = 5
        self.episode_length_s = 60.0
        # simulation settings
        self.sim.dt = 0.002
        self.sim.disable_contact_processing = True
        self.sim.physics_material = self.scene.terrain.physics_material

@configclass
class IntegratorEnvCfg(UnicycleEnvCfg):
    scene: IntegratorSceneCfg = IntegratorSceneCfg(num_envs=1, env_spacing=5.0, replicate_physics=True)
    # MDP settings
    events: IntegratorEventsCfg = IntegratorEventsCfg()
    observations: IntegratorObservationsCfg = IntegratorObservationsCfg()
    
@configclass
class CarEnvCfg(UnicycleEnvCfg):
    scene: CarSceneCfg = CarSceneCfg(num_envs=1, env_spacing=5.0, replicate_physics=True)
    # MDP settings
    events: CarEventsCfg = CarEventsCfg()