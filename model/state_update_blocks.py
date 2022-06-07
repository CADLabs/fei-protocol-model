"""
cadCAD model State Update Block structure, composed of Policy and State Update Functions
"""


import model.parts.price_processes as price_processes
import model.parts.pcv_management as pcv_management
import model.parts.user_circulating_fei as user_circulating_fei

from model.system_parameters import parameters
from model.utils import update_from_signal
from model.parts.assorted_system_metrics import *


state_update_blocks = [
    {
        "description": """
            a test block
        """,
        "policies": {},
        "variables": {"test_variable": s_test_variable},
    },
    # placeholder block, just sets total user fei to a constant
    {
        "description": """
            User Circulating FEI
        """,
        "policies": {},
        "variables": {
            "total_user_circulating_fei": user_circulating_fei.update_total_user_circulating_fei,
        },
    },
    {
        "description": """
            assorted price updates
        """,
        "policies": {},
        "variables": {
            "fei_price": price_processes.update_fei_price,
            "stable_asset_price": price_processes.update_stable_asset_price,
            "volatile_asset_price": price_processes.update_volatile_asset_price,
        },
    },
    # if this isnt split into multiple series blocks the first element of the time series will be NaN
    # because no previously initialized value for first timestep
    {
        "description": """
            PCV rebalancing
        """,
        "policies": {
            "pcv_rebalancing": pcv_management.policy_pcv_rebalancing,
        },
        "variables": {
            "total_stable_asset_pcv_amount": pcv_management.update_total_stable_asset_pcv_amount,
            "total_volatile_asset_pcv_amount": pcv_management.update_total_volatile_asset_pcv_amount,
            "total_stable_asset_pcv_value": pcv_management.update_total_stable_asset_pcv_value,
            "total_volatile_asset_pcv_value": pcv_management.update_total_volatile_asset_pcv_value,
            #             "total_pcv_value": pcv_management.update_total_pcv_value,
            #             "stable_backing_ratio": pcv_management.update_stable_backing_ratio,
            #             "collateralization_ratio": pcv_management.update_collateralization_ratio,
        },
    },
    {
        "description": """
            PCV rebalancing pt2
        """,
        "policies": {},
        "variables": {
            "total_pcv_value": pcv_management.update_total_pcv_value,
            "stable_backing_ratio": pcv_management.update_stable_backing_ratio,
            "collateralization_ratio": pcv_management.update_collateralization_ratio,
        },
    },
    {
        "description": """
            assorted calculations
        """,
        "policies": {},
        "variables": {
            "protocol_equity": user_circulating_fei.update_protocol_equity,
        },
    },
]
