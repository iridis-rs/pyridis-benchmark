from pyridis_message import ArrowMessage

from dataclasses import dataclass
from typing import Optional

import numpy as np

SIZES = [
    1,
    8,
    64,
    512,
    2048,
    4096,
    4 * 4096,
    10 * 4096,
    100 * 4096,
    1000 * 4096,
]

BENCH_LEN = 100

@dataclass
class Metadata(ArrowMessage):
    name: Optional[str]
    width: np.uint32
    height: np.uint32

@dataclass
class Image(ArrowMessage):
    data: np.ndarray
    metadata: Optional[Metadata]
