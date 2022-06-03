"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""


import model.parts.price_processes as price_processes

from model.system_parameters import parameters
from model.utils import update_from_signal


state_update_blocks = [
    {
        "description": """
        Update FEI and PCV asset prices
        """,
        "policies": {},
        "variables": {
            "stable_asset_price": price_processes.update_stable_asset_price,
            "volatile_asset_price": price_processes.update_volatile_asset_price,
        },
    },
]
