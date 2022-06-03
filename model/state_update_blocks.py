"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""


import model.parts.price_processes as price_processes

from model.system_parameters import parameters
from model.utils import update_from_signal
from model.parts.assorted_system_metrics import *
from model.parts.price_processes import *


state_update_blocks = [
    {
        "description": """
            a test block
        """,
        "policies": {},
        "variables": {
            "test_variable": s_test_variable
        },
    },
    {
        {
        "policies": {},
        "variables": {
            "stable_asset_price": price_processes.update_stable_asset_price,
            "volatile_asset_price": price_processes.update_volatile_asset_price,
        },
    },
    }
]
