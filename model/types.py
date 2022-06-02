"""
Various Python types used in the model
"""

import numpy as np
import sys

# See https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field
from enum import Enum

# If Python version is greater than equal to 3.8, import from typing module
# Else also import from typing_extensions module
if sys.version_info >= (3, 8):
    from typing import TypedDict, List, Callable, NamedTuple
else:
    from typing import List, NamedTuple
    from typing_extensions import TypedDict, Callable


# Simulation types
Timestep = int
Run = int
