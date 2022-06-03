"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""

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
        "description": """
            FEI price update
        """,
        "policies": {},
        "variables": {
            "fei_price": s_fei_price
        },
    },
]
