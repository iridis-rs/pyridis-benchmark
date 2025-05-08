from typing import Any, Dict

import asyncio
import time

from pyridis_api import Node, Input, Inputs, Outputs, Queries, Queryables, Header
from message import SIZES, BENCH_LEN, Image

class MySink(Node):
    latency: Input
    throughput: Input

    def __init__(self):
        pass

    async def new(self, inputs: Inputs, outputs: Outputs, queries: Queries, queryables: Queryables, config: Dict[str, Any]):
        self.prefix = config["prefix"]
        self.suffix = config["suffix"]

        self.latency = await inputs.with_input("latency")
        self.throughput = await inputs.with_input("throughput")

    async def start(self):
        latencies_map = {}

        for size in SIZES:
            latencies = []

            for _ in range(BENCH_LEN):
                message = await self.latency.recv()
                latencies.append(message.header.elapsed)

            avg_latency = sum(latencies) / len(latencies)
            latencies_map[size] = avg_latency / 1000.0 # nanos to micros

        throughputs_map = {}

        for size in SIZES:
            throughputs = []

            for _ in range (BENCH_LEN):
                message = await self.throughput.recv()
                throughputs.append(message.header.timestamp)

            intervals = [
                (throughputs[i + 1] - throughputs[i]).microseconds
                for i in range(len(throughputs) - 1)
            ]
            avg_duration = sum(intervals) / len(intervals)

            avg_throughput = 1.0 / (avg_duration / 1_000_000.0) # micro to sec

            throughputs_map[size] = avg_throughput

        headers = ["Latency (µs)", "Throughput (msg/s)", "Throughput (GB/s)", "Size (bytes)"]
        print(f"{headers[0]:<15} {headers[1]:>15} {headers[2]:>15} {headers[3]:>15}")

        for size in SIZES:
            latency = latencies_map[size]
            throughput = throughputs_map[size]
            throughput_gbps = throughput * size / 1_000_000_000.0 # bytes to giga bytes

            print(f"{latency:<15.3f} {throughput:>15.3f} {throughput_gbps:>15.6f} {size:>15}")

        filename = f"{self.suffix}" if not self.prefix else f"{self.prefix}-{self.suffix}"

        file_path = f"out/{filename}.csv"
        file = await asyncio.to_thread(open, file_path, "w")

        file.write("latency_us,throughput_ops,throughput_gbps,size\n")

        for size in SIZES:
            avg_latency = latencies_map.get(size, 0.0)
            throughput = throughputs_map.get(size, 0.0)
            throughput_gbps = throughput * size / 1_000_000_000.0

            line = f"{avg_latency:.3f},{throughput:.3f},{throughput_gbps:.6f},{size}\n"
            file.write(line)

        file.close()

def pyridis_node():
    return MySink
