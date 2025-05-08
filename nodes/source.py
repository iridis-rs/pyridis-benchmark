from typing import Any, Dict

import pyarrow as pa
import numpy as np
import asyncio
import time

from pyridis_api import Node, Output, Inputs, Outputs, Queries, Queryables
from message import SIZES, BENCH_LEN, Image, Metadata

class MySource(Node):
    latency: Output
    throughput: Output
    data: dict[int, np.ndarray]

    def __init__(self):
        self.data = {}

        for size in SIZES:
            random_bytes = np.random.randint(0, 256, size, dtype=np.uint8)
            self.data[size] = random_bytes

    async def new(self, inputs: Inputs, outputs: Outputs, queries: Queries, queryables: Queryables, config: Dict[str, Any]):
        self.prefix = config["prefix"]
        self.suffix = config["suffix"]

        self.latency = await outputs.with_output("latency")
        self.throughput = await outputs.with_output("throughput")

    async def start(self):
        for size in SIZES:
            for _ in range(BENCH_LEN):
                if self.prefix == "":
                    image = Image(
                        data=self.data[size],
                        metadata=None
                    )

                    try:
                        await self.latency.send(image.to_arrow())
                    except:
                        return
                elif self.prefix == "raw":
                    try:
                        await self.latency.send(pa.array(self.data[size]))
                    except:
                        return

                await asyncio.sleep(0.003)

        await asyncio.sleep(1.0)

        for size in SIZES:
            for _ in range(BENCH_LEN):
                if self.prefix == "":
                    image = Image(
                        data=self.data[size],
                        metadata=None
                    )

                    try:
                        await self.throughput.send(image.to_arrow())
                    except:
                        return
                elif self.prefix == "raw":
                    try:
                        await self.throughput.send(pa.array(self.data[size]))
                    except:
                        return


def pyridis_node():
    return MySource
