"""
Chapter 18 - Performance Benchmarks and Testing for MCP Systems

Demonstrates a benchmarking suite that measures MCP performance across four
dimensions: capability discovery, cross-component coordination, adaptive
performance, and end-to-end user scenarios.  Results are persisted in SQLite
for historical comparison.
"""

import asyncio
import time
import json
import statistics
import random
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass
import sqlite3


# ---------------------------------------------------------------------------
# Part 1: Data model and benchmark suite setup
# Sets up the BenchmarkResult dataclass, SQLite persistence layer, and
# simulator methods that stand in for real MCP server calls.
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    """Stores the outcome of a single benchmark run."""
    benchmark_name: str
    metrics: Dict[str, float]
    metadata: Dict[str, Any]
    timestamp: str
    duration: float


class MCPBenchmarkSuite:
    """Measures MCP system performance across multiple dimensions."""

    def __init__(self, db_path: str = "mcp_benchmarks.db"):
        self.db_path = db_path
        self.results: List[BenchmarkResult] = []
        self._setup_database()

    # -- database -----------------------------------------------------------

    def _setup_database(self):
        """Create tables for persisting benchmark results."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS benchmark_results (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   benchmark_name TEXT, metrics TEXT, metadata TEXT,
                   timestamp TEXT, duration REAL)"""
        )
        cur.execute(
            """CREATE TABLE IF NOT EXISTS benchmark_sessions (
                   session_id TEXT PRIMARY KEY, start_time TEXT,
                   end_time TEXT, total_benchmarks INTEGER,
                   summary_metrics TEXT)"""
        )
        conn.commit()
        conn.close()
        print("Benchmark database initialized")

    def _store_result(self, result: BenchmarkResult, session_id: str):
        """Persist a single benchmark result."""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO benchmark_results "
            "(benchmark_name,metrics,metadata,timestamp,duration) "
            "VALUES (?,?,?,?,?)",
            (result.benchmark_name, json.dumps(result.metrics),
             json.dumps(result.metadata), result.timestamp, result.duration),
        )
        conn.commit()
        conn.close()

    def _store_session(self, session_id, start, end, count, summary):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "INSERT INTO benchmark_sessions VALUES (?,?,?,?,?)",
            (session_id, start.isoformat(), end.isoformat(),
             count, json.dumps(summary)),
        )
        conn.commit()
        conn.close()

    # -- simulators (stand-ins for real MCP calls) --------------------------

    async def _sim_server_discovery(self) -> List[str]:
        await asyncio.sleep(0.02 + random.random() * 0.03)
        return ["file_server", "search_server", "analytics_server",
                "knowledge_server", "transform_server"]

    async def _sim_capability_enum(self, server: str) -> List[str]:
        await asyncio.sleep(0.01 + random.random() * 0.02)
        cap_map = {
            "file_server": ["read", "write", "list"],
            "search_server": ["search", "index", "rank"],
            "analytics_server": ["analyze", "summarize", "classify"],
            "knowledge_server": ["query", "reason", "explain", "learn"],
            "transform_server": ["convert", "validate"],
        }
        return cap_map.get(server, ["basic"])

    async def _sim_coordination(self, servers: List[str]) -> float:
        t = 0.02 * len(servers) + random.random() * 0.01
        await asyncio.sleep(t)
        return t

    async def _sim_workflow(self, servers: List[str]) -> bool:
        t = 0.03 * len(servers) ** 1.2
        await asyncio.sleep(t + random.random() * 0.02)
        if len(servers) > 3 and random.random() < 0.1:
            raise RuntimeError("coordination timeout")
        return True

    async def _sim_user_request(self) -> float:
        t = 0.05 + random.random() * 0.1
        await asyncio.sleep(t)
        if random.random() < 0.05:
            raise RuntimeError("request failed")
        return t

    async def _sim_scenario(self, steps: int, complexity: float) -> bool:
        await asyncio.sleep(steps * 0.02 * complexity + random.random() * 0.03)
        return random.random() > (0.02 * complexity)

    # -----------------------------------------------------------------------
    # Part 2: Capability discovery and coordination benchmarks
    # These two benchmarks measure how fast the system discovers servers and
    # enumerates their tools, and how reliably multi-server workflows execute.
    # -----------------------------------------------------------------------

    async def benchmark_capability_discovery(self) -> BenchmarkResult:
        """Measure discovery latency, enumeration throughput, and reliability."""
        print("Running capability discovery benchmark...")
        t0 = time.time()

        # 1. Discovery latency (20 iterations)
        disc_times = []
        for _ in range(20):
            ts = time.time()
            await self._sim_server_discovery()
            disc_times.append(time.time() - ts)

        # 2. Capability enumeration
        enum_times, cap_counts = [], []
        for srv in (await self._sim_server_discovery()):
            ts = time.time()
            caps = await self._sim_capability_enum(srv)
            enum_times.append(time.time() - ts)
            cap_counts.append(len(caps))

        # 3. Concurrent discovery reliability
        tasks = [asyncio.create_task(self._sim_server_discovery())
                 for _ in range(15)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        ok = sum(1 for r in results if not isinstance(r, Exception))

        metrics = {
            "discovery_latency_mean": statistics.mean(disc_times),
            "discovery_latency_p95": sorted(disc_times)[int(0.95 * len(disc_times))],
            "enumeration_throughput": len(enum_times) / sum(enum_times),
            "avg_capabilities_per_server": statistics.mean(cap_counts),
            "concurrent_reliability": ok / 15,
        }
        return BenchmarkResult("capability_discovery", metrics,
                               {"iterations": 20}, datetime.now().isoformat(),
                               time.time() - t0)

    async def benchmark_coordination(self) -> BenchmarkResult:
        """Measure cross-component coordination overhead."""
        print("Running coordination benchmark...")
        t0 = time.time()

        # Simple coordination latency
        coord_times = []
        for _ in range(20):
            ts = time.time()
            await self._sim_coordination(["a", "b"])
            coord_times.append(time.time() - ts)

        # Complex workflow success rate
        workflows = [["a","b","c"], ["a","b","c","d"], ["x","y"]]
        wf_success = []
        for wf in workflows:
            ok = 0
            for _ in range(10):
                try:
                    await self._sim_workflow(wf)
                    ok += 1
                except RuntimeError:
                    pass
            wf_success.append(ok / 10)

        metrics = {
            "coord_latency_mean": statistics.mean(coord_times),
            "coord_latency_p95": sorted(coord_times)[int(0.95 * len(coord_times))],
            "workflow_success_mean": statistics.mean(wf_success),
            "workflow_success_min": min(wf_success),
        }
        return BenchmarkResult("coordination", metrics,
                               {"workflows": len(workflows)},
                               datetime.now().isoformat(), time.time() - t0)

    # -----------------------------------------------------------------------
    # Part 3: Scalability and end-to-end benchmarks, plus the scoring helper
    # The scalability benchmark ramps concurrency from 1 to 50 users while
    # the end-to-end benchmark runs realistic multi-step MCP scenarios.
    # -----------------------------------------------------------------------

    async def benchmark_scalability(self) -> BenchmarkResult:
        """Measure throughput and success rate under increasing concurrency."""
        print("Running scalability benchmark...")
        t0 = time.time()
        scale_data = []

        for n_users in (1, 5, 10, 25, 50):
            ts = time.time()
            tasks = [asyncio.create_task(self._sim_user_request())
                     for _ in range(n_users)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - ts
            ok = sum(1 for r in results if not isinstance(r, Exception))
            scale_data.append({
                "users": n_users, "success_rate": ok / n_users,
                "throughput": ok / elapsed,
            })

        metrics = {
            "peak_throughput": max(d["throughput"] for d in scale_data),
            "min_success_rate": min(d["success_rate"] for d in scale_data),
            "throughput_at_50": next(d["throughput"] for d in scale_data
                                     if d["users"] == 50),
        }
        return BenchmarkResult("scalability", metrics,
                               {"max_users": 50},
                               datetime.now().isoformat(), time.time() - t0)

    async def benchmark_end_to_end(self) -> BenchmarkResult:
        """Run realistic multi-step scenarios and measure success/latency."""
        print("Running end-to-end benchmark...")
        t0 = time.time()

        scenarios = [
            {"name": "doc_search",     "steps": 3, "cx": 1.0},
            {"name": "multimodal",     "steps": 4, "cx": 2.0},
            {"name": "simple_query",   "steps": 2, "cx": 1.0},
            {"name": "collab_analysis","steps": 5, "cx": 2.0},
        ]
        scenario_metrics = []
        for sc in scenarios:
            times, successes = [], []
            for _ in range(10):
                ts = time.time()
                ok = await self._sim_scenario(sc["steps"], sc["cx"])
                times.append(time.time() - ts)
                successes.append(ok)
            scenario_metrics.append({
                "name": sc["name"],
                "mean_time": statistics.mean(times),
                "success_rate": sum(successes) / len(successes),
            })

        metrics = {
            "overall_success": statistics.mean(
                s["success_rate"] for s in scenario_metrics),
            "avg_latency": statistics.mean(
                s["mean_time"] for s in scenario_metrics),
            "worst_success": min(
                s["success_rate"] for s in scenario_metrics),
        }
        return BenchmarkResult("end_to_end", metrics,
                               {"scenarios": len(scenarios)},
                               datetime.now().isoformat(), time.time() - t0)

    # -- scoring helpers ----------------------------------------------------

    @staticmethod
    def _score(result: BenchmarkResult, weights: Dict[str, float]) -> float:
        """Weighted average of selected metrics (higher is better)."""
        total_w = sum(weights.values())
        return sum(result.metrics.get(k, 0) * w
                   for k, w in weights.items()) / total_w

    # -----------------------------------------------------------------------
    # Part 4: Suite orchestrator and entry point
    # Runs all four benchmarks in sequence, computes per-dimension scores,
    # and prints a summary report before persisting the session to SQLite.
    # -----------------------------------------------------------------------

    async def run_suite(self) -> Dict[str, Any]:
        """Execute all benchmarks and produce a summary report."""
        session_id = f"bench_{datetime.now():%Y%m%d_%H%M%S}"
        start = datetime.now()

        print(f"Starting benchmark session: {session_id}")
        print("=" * 60)

        results = []
        for coro in (self.benchmark_capability_discovery(),
                     self.benchmark_coordination(),
                     self.benchmark_scalability(),
                     self.benchmark_end_to_end()):
            r = await coro
            results.append(r)
            self._store_result(r, session_id)
            print(f"  {r.benchmark_name} completed in {r.duration:.2f}s")

        # Compute per-dimension scores (0-1 scale)
        scores = {
            "capability_discovery": self._score(
                results[0],
                {"concurrent_reliability": 0.5,
                 "enumeration_throughput": 0.5}),
            "coordination": self._score(
                results[1],
                {"workflow_success_mean": 0.6,
                 "workflow_success_min": 0.4}),
            "scalability": self._score(
                results[2],
                {"min_success_rate": 0.5,
                 "peak_throughput": 0.01}),
            "end_to_end": self._score(
                results[3],
                {"overall_success": 0.6,
                 "worst_success": 0.4}),
        }
        overall = statistics.mean(scores.values())

        end = datetime.now()
        summary = {"scores": scores, "overall": overall,
                   "duration": (end - start).total_seconds()}
        self._store_session(session_id, start, end, len(results), summary)

        print("=" * 60)
        print(f"Session {session_id} finished - {summary['duration']:.1f}s")
        print(f"Overall score: {overall:.2f}/1.0")
        for name, sc in scores.items():
            print(f"  {name}: {sc:.2f}")

        return {"session_id": session_id, "results": results,
                "summary": summary}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main():
    suite = MCPBenchmarkSuite()
    await suite.run_suite()

if __name__ == "__main__":
    asyncio.run(main())
