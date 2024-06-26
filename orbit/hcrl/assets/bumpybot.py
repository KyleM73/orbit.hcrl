"""Configuration for Draco robots.

The following configurations are available:

* :obj:`BUMPYBOT_CFG`: HCRL Bumpybot robot with Nonholonomic controller

Reference: TODO add link to urdf etc.
"""

from __future__ import annotations
import os

import omni.isaac.lab.sim as sim_utils
from omni.isaac.lab.actuators import IdealPDActuatorCfg, ImplicitActuatorCfg
from omni.isaac.lab.assets import ArticulationCfg, RigidObjectCfg

from isaac.lab.hcrl import EXT_DIR

##
# Configuration
##

BUMPYBOT_CFG = ArticulationCfg(
    spawn=sim_utils.UrdfFileCfg(
        fix_base=True,
        merge_fixed_joints=False,
        make_instanceable=True,
        force_usd_conversion=True,
        activate_contact_sensors=False,
        self_collision=False,
        convex_decompose_mesh=True,
        link_density=1e-5,
        visible=True,
        asset_path=os.path.abspath(os.path.join(EXT_DIR, "resources/hcrl_robots/bumpybot/bumpybot.urdf")),
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            disable_gravity=True,
            retain_accelerations=False,
            linear_damping=0.0,
            angular_damping=0.0,
            max_linear_velocity=1000.0,
            max_angular_velocity=1000.0,
            max_depenetration_velocity=1.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=4,
            solver_velocity_iteration_count=0,
        ),
    ),
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 0.343),
        joint_pos={"dummy_prismatic.*" : 0.000, "dummy_revolute.*" : 3.141},
        joint_vel={"dummy_prismatic.*" : 0.000, "dummy_revolute.*" : 0.000},
    ),
    soft_joint_pos_limit_factor=1.0,
    collision_group=0,
    actuators={
        "prismatic": IdealPDActuatorCfg(
            joint_names_expr=["dummy_prismatic.*"],
            effort_limit=1000.0,
            velocity_limit=10.0,
            stiffness={"dummy_prismatic.*": 0},
            damping={"dummy_prismatic.*": 1000},
            friction={"dummy_prismatic.*": 0.0},
        ),
         "revolute": IdealPDActuatorCfg(
            joint_names_expr=["dummy_revolute.*"],
            effort_limit=1000.0,
            velocity_limit=10.0,
            stiffness={"dummy_revolute.*": 0},
            damping={"dummy_revolute.*": 1000},
            friction={"dummy_revolute.*": 0.0},
         ),
         #"passive": IdealPDActuatorCfg(
         #   joint_names_expr=["passive_prismatic_z_joint"],
         #   effort_limit=0.0,
         #   velocity_limit=10.0,
         #   stiffness={"passive_prismatic_z_joint": 0},
         #   damping={"passive_prismatic_z_joint": 0},
         #   friction={"passive_prismatic_z_joint": 0},
         #)
    },
    debug_vis=True,
)