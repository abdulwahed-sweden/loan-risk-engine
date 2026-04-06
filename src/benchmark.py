import time
import statistics
import json
from decimal import Decimal
from clarax_core import Schema, Field, serialize_many, validate_many

from src.schema import loan_schema
from src.generator import generate_batch


def serialize_pure_python(data: list[dict]) -> list[dict]:
    results = []
    for row in data:
        results.append({
            k: str(v) if isinstance(v, Decimal) else v
            for k, v in row.items()
        })
    return results


def run_benchmark(count: int, runs: int = 5):
    print(f"\n{'='*52}")
    print(f"  Benchmark — {count:,} loan applications")
    print(f"{'='*52}")

    data = generate_batch(count)

    # ── Serialize ──
    py_times = []
    cx_times = []

    for _ in range(runs):
        t = time.perf_counter()
        serialize_pure_python(data)
        py_times.append(time.perf_counter() - t)

        t = time.perf_counter()
        serialize_many(data, loan_schema)
        cx_times.append(time.perf_counter() - t)

    py_ms = statistics.median(py_times) * 1000
    cx_ms = statistics.median(cx_times) * 1000
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"\n  Serialization:")
    print(f"    Pure Python : {py_ms:.1f}ms")
    print(f"    ClaraX      : {cx_ms:.1f}ms")
    print(f"    Speedup     : {speedup:.1f}x")

    # ── Validate ──
    py_times = []
    cx_times = []

    for _ in range(runs):
        t = time.perf_counter()
        for row in data:
            age = row["age"]
            cs = row["credit_score"]
            _ = 18 <= age <= 100 and 300 <= cs <= 850
        py_times.append(time.perf_counter() - t)

        t = time.perf_counter()
        validate_many(data, loan_schema)
        cx_times.append(time.perf_counter() - t)

    py_ms = statistics.median(py_times) * 1000
    cx_ms = statistics.median(cx_times) * 1000
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"\n  Validation:")
    print(f"    Pure Python : {py_ms:.1f}ms")
    print(f"    ClaraX      : {cx_ms:.1f}ms")
    print(f"    Speedup     : {speedup:.1f}x")
    print(f"\n{'='*52}")


if __name__ == "__main__":
    run_benchmark(1_000)
    run_benchmark(10_000)
    run_benchmark(50_000)