"""
Chapter 19 - Optimization Strategies for MCP Systems

Demonstrates server-side and client-side optimization techniques for MCP
systems: context-aware caching, capability-aware load balancing, intelligent
request orchestration, and continuous performance monitoring.
"""

import asyncio
import time
import json
import statistics
import random
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import sqlite3


# ---------------------------------------------------------------------------
# Part 1: Data model and context-aware cache
# Defines the OptimizationMetrics dataclass and implements an LRU cache
# that keys entries on both the query string and the user context.
# ---------------------------------------------------------------------------

@dataclass
class OptimizationMetrics:
    """Tracks the effect of an optimization strategy."""
    strategy_name: str
    baseline_latency: float
    optimized_latency: float
    improvement_pct: float
    cache_hit_rate: float = 0.0
    throughput_gain: float = 0.0


class ContextAwareCache:
    """Cache whose validity depends on user context (permissions, scope)."""

    def __init__(self, max_size: int = 256):
        self.max_size = max_size
        self._store: Dict[str, Any] = {}
        self._access_order: List[str] = []
        self.hits = 0
        self.misses = 0

    def _make_key(self, query: str, context: Dict[str, Any]) -> str:
        ctx_sig = json.dumps(context, sort_keys=True)
        return f"{query}::{ctx_sig}"

    def get(self, query: str, context: Dict[str, Any]) -> Optional[Any]:
        key = self._make_key(query, context)
        if key in self._store:
            self.hits += 1
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._store[key]
        self.misses += 1
        return None

    def put(self, query: str, context: Dict[str, Any], value: Any):
        key = self._make_key(query, context)
        if len(self._store) >= self.max_size and key not in self._store:
            oldest = self._access_order.pop(0)
            del self._store[oldest]
        self._store[key] = value
        if key not in self._access_order:
            self._access_order.append(key)

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


# ---------------------------------------------------------------------------
# Part 2: Capability-aware load balancer
# Routes each request to the least-loaded server that possesses every
# capability the request requires, avoiding misrouting and hotspots.
# ---------------------------------------------------------------------------

class CapabilityAwareLoadBalancer:
    """Routes requests to the server best suited by capability and load."""

    def __init__(self):
        self.servers: Dict[str, Dict[str, Any]] = {}

    def register_server(self, name: str, capabilities: List[str]):
        self.servers[name] = {
            "capabilities": set(capabilities),
            "current_load": 0,
            "total_handled": 0,
        }

    def select_server(self, required_caps: List[str]) -> Optional[str]:
        """Pick the least-loaded server that has every required capability."""
        candidates = []
        for name, info in self.servers.items():
            if set(required_caps).issubset(info["capabilities"]):
                candidates.append((name, info["current_load"]))
        if not candidates:
            return None
        candidates.sort(key=lambda c: c[1])
        chosen = candidates[0][0]
        self.servers[chosen]["current_load"] += 1
        self.servers[chosen]["total_handled"] += 1
        return chosen

    def release(self, server_name: str):
        if server_name in self.servers:
            self.servers[server_name]["current_load"] = max(
                0, self.servers[server_name]["current_load"] - 1
            )

    def load_distribution(self) -> Dict[str, int]:
        return {n: s["total_handled"] for n, s in self.servers.items()}


# ---------------------------------------------------------------------------
# Part 3: Request orchestrator and performance monitor
# The orchestrator executes a DAG of tasks with maximum parallelism,
# while the monitor tracks latency in a sliding window and flags regressions.
# ---------------------------------------------------------------------------

class RequestOrchestrator:
    """Batches independent requests and pipelines dependent ones."""

    def __init__(self):
        self.total_requests = 0
        self.total_batches = 0

    async def execute_dag(
        self, dag: Dict[str, List[str]], execute_fn
    ) -> Dict[str, Any]:
        """Execute a DAG of tasks, parallelising independent ones.

        *dag* maps task names to lists of dependency names.
        *execute_fn(task_name)* is an async callable that runs one task.
        """
        completed: Dict[str, Any] = {}
        remaining = dict(dag)

        while remaining:
            # Find tasks whose dependencies are all satisfied
            ready = [
                t for t, deps in remaining.items()
                if all(d in completed for d in deps)
            ]
            if not ready:
                raise RuntimeError("Cycle detected in task DAG")

            self.total_batches += 1
            batch_results = await asyncio.gather(
                *(execute_fn(t) for t in ready)
            )
            for task, result in zip(ready, batch_results):
                completed[task] = result
                del remaining[task]
                self.total_requests += 1

        return completed


class PerformanceMonitor:
    """Records latency samples and detects regressions."""

    def __init__(self, window: int = 50):
        self.window = window
        self._samples: List[float] = []

    def record(self, latency: float):
        self._samples.append(latency)
        if len(self._samples) > self.window * 2:
            self._samples = self._samples[-self.window * 2:]

    @property
    def mean_latency(self) -> float:
        return statistics.mean(self._samples) if self._samples else 0.0

    @property
    def p95_latency(self) -> float:
        if not self._samples:
            return 0.0
        s = sorted(self._samples)
        return s[int(0.95 * len(s))]

    def regression_detected(self) -> bool:
        """True when the recent window is >20 % slower than the prior one."""
        if len(self._samples) < self.window * 2:
            return False
        old = self._samples[-self.window * 2:-self.window]
        new = self._samples[-self.window:]
        return statistics.mean(new) > statistics.mean(old) * 1.2


# ---------------------------------------------------------------------------
# Part 4: Interactive demos and entry point
# Runs four short demonstrations - caching, load balancing, DAG orchestration,
# and regression monitoring - to show each optimization strategy in action.
# ---------------------------------------------------------------------------

async def _sim_tool_call(name: str) -> Dict[str, Any]:
    """Simulate an MCP tool call with variable latency."""
    latency = 0.02 + random.random() * 0.04
    await asyncio.sleep(latency)
    return {"tool": name, "latency": latency, "ok": True}


async def demo_caching():
    """Show how context-aware caching reduces repeated-query latency."""
    print("\n--- Context-Aware Caching Demo ---")
    cache = ContextAwareCache(max_size=64)
    contexts = [
        {"user": "alice", "role": "admin"},
        {"user": "bob",   "role": "viewer"},
    ]
    queries = ["search:logs", "search:metrics", "search:logs"]

    for ctx in contexts:
        for q in queries:
            cached = cache.get(q, ctx)
            if cached is None:
                result = await _sim_tool_call(q)
                cache.put(q, ctx, result)
            else:
                result = cached

    print(f"  Cache hit rate : {cache.hit_rate:.0%}")
    print(f"  Hits / misses  : {cache.hits} / {cache.misses}")


async def demo_load_balancing():
    """Show capability-aware load balancing across heterogeneous servers."""
    print("\n--- Capability-Aware Load Balancing Demo ---")
    lb = CapabilityAwareLoadBalancer()
    lb.register_server("nlp_server",   ["search", "summarize"])
    lb.register_server("data_server",  ["search", "aggregate"])
    lb.register_server("ml_server",    ["classify", "predict"])

    requests = [
        (["search"], 20),
        (["summarize"], 5),
        (["classify", "predict"], 8),
    ]
    for caps, count in requests:
        for _ in range(count):
            srv = lb.select_server(caps)
            if srv:
                await asyncio.sleep(0.005)
                lb.release(srv)

    print("  Load distribution:", lb.load_distribution())


async def demo_orchestration():
    """Show DAG-based request orchestration with parallelism."""
    print("\n--- Request Orchestration Demo ---")
    orch = RequestOrchestrator()

    dag = {
        "fetch_docs":   [],
        "fetch_schema": [],
        "analyze":      ["fetch_docs", "fetch_schema"],
        "summarize":    ["analyze"],
    }
    results = await orch.execute_dag(dag, _sim_tool_call)

    print(f"  Tasks completed : {orch.total_requests}")
    print(f"  Parallel batches: {orch.total_batches}")
    for task, res in results.items():
        print(f"    {task}: latency={res['latency']:.3f}s")


async def demo_monitoring():
    """Show regression detection via a sliding-window monitor."""
    print("\n--- Performance Monitoring Demo ---")
    mon = PerformanceMonitor(window=20)

    # Normal period
    for _ in range(25):
        mon.record(0.03 + random.random() * 0.01)
    print(f"  Mean after normal period   : {mon.mean_latency:.4f}s")
    print(f"  Regression detected?       : {mon.regression_detected()}")

    # Degraded period
    for _ in range(25):
        mon.record(0.06 + random.random() * 0.02)
    print(f"  Mean after degraded period : {mon.mean_latency:.4f}s")
    print(f"  Regression detected?       : {mon.regression_detected()}")


async def main():
    print("=" * 60)
    print("MCP Optimization Strategies - Demonstrations")
    print("=" * 60)

    await demo_caching()
    await demo_load_balancing()
    await demo_orchestration()
    await demo_monitoring()

    print("\n" + "=" * 60)
    print("All optimization demos completed.")


if __name__ == "__main__":
    asyncio.run(main())
