"""Heavy benchmark: ClaraX vs pure Python on complex loan workloads.

Tests workloads where Rust has a genuine advantage:
  1. Name validation   — character scanning (Python: ~7us/name, Rust: ~50ns/name)
  2. Pattern matching   — regex / hand-written validators
  3. Risk computation   — parallel float math with Rayon
  4. Batch statistics   — parallel sum/sort vs Python's pure-Python statistics module
  5. Full validation    — all of the above combined
"""

import statistics
import time

from heavy_generator import generate_heavy_batch
from python_validator import (
    batch_stats as py_batch_stats,
    compute_risk_batch as py_compute_risk,
    validate_batch as py_validate_batch,
    validate_ids_batch as py_validate_ids,
    validate_names_batch as py_validate_names,
)

from clarax_core import (
    batch_stats as cx_batch_stats,
    compute_risk_batch as cx_compute_risk,
    validate_ids_batch as cx_validate_ids,
    validate_names_batch as cx_validate_names,
)

COUNT = 50_000
RUNS = 5


def bench(fn, *args, runs=RUNS):
    """Returns median time in milliseconds."""
    times = []
    for _ in range(runs):
        t = time.perf_counter()
        fn(*args)
        times.append(time.perf_counter() - t)
    return statistics.median(times) * 1000


def main():
    print(f"\nGenerating {COUNT:,} complex loan applications...")
    data = generate_heavy_batch(COUNT)

    # Extract columns for targeted benchmarks
    all_names = [r["full_name"] for r in data]
    all_names += [r["employer_name"] for r in data]
    all_names += [r["guarantor_name"] for r in data]
    name_count = len(all_names)

    all_ids = [r["national_id"] for r in data]
    all_scores = [r["risk_score"] for r in data]

    print(f"Generated. Starting benchmarks ({RUNS} runs each, median).\n")

    # ── Scenario 1: Name Validation (character scanning) ─────────────────
    print("=" * 62)
    print(f"  Scenario 1: Name validation ({name_count:,} names)")
    print("  Character scanning: isdigit, isalpha, isspace per char")
    print("=" * 62)

    py_ms = bench(py_validate_names, all_names)
    cx_ms = bench(cx_validate_names, all_names)
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"  Pure Python : {py_ms:>8.1f} ms")
    print(f"  ClaraX Rust : {cx_ms:>8.1f} ms")
    print(f"  Speedup     : {speedup:>8.1f}x")

    # ── Scenario 2: Pattern Matching (national ID regex) ─────────────────
    print(f"\n{'=' * 62}")
    print(f"  Scenario 2: National ID validation ({COUNT:,} IDs)")
    print(r"  Pattern: ^\d{8}-\d{4}$")
    print("=" * 62)

    py_ms = bench(py_validate_ids, all_ids)
    cx_ms = bench(cx_validate_ids, all_ids)
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"  Pure Python : {py_ms:>8.1f} ms")
    print(f"  ClaraX Rust : {cx_ms:>8.1f} ms")
    print(f"  Speedup     : {speedup:>8.1f}x")

    # ── Scenario 3: Risk Score Computation (parallel float math) ─────────
    print(f"\n{'=' * 62}")
    print(f"  Scenario 3: Risk score computation ({COUNT:,} records)")
    print("  Float math: log, sqrt, clamp — Rayon parallel")
    print("=" * 62)

    py_ms = bench(py_compute_risk, data)
    cx_ms = bench(cx_compute_risk, data)
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"  Pure Python : {py_ms:>8.1f} ms")
    print(f"  ClaraX Rust : {cx_ms:>8.1f} ms")
    print(f"  Speedup     : {speedup:>8.1f}x")

    # ── Scenario 4: Batch Statistics (parallel reduce + sort) ────────────
    print(f"\n{'=' * 62}")
    print(f"  Scenario 4: Batch statistics ({COUNT:,} values)")
    print("  mean, median, stdev, min, max — Rayon parallel")
    print("=" * 62)

    py_ms = bench(py_batch_stats, all_scores)
    cx_ms = bench(cx_batch_stats, all_scores)
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"  Pure Python : {py_ms:>8.1f} ms")
    print(f"  ClaraX Rust : {cx_ms:>8.1f} ms")
    print(f"  Speedup     : {speedup:>8.1f}x")

    # ── Scenario 5: Full Validation (all rules combined) ─────────────────
    print(f"\n{'=' * 62}")
    print(f"  Scenario 5: Full application validation ({COUNT:,} records)")
    print("  Names + patterns + types + cross-field + Decimal arithmetic")
    print("=" * 62)

    py_ms = bench(py_validate_batch, data)
    # ClaraX full validation: names + IDs + field checks
    def cx_full_validate(data):
        names = [r["full_name"] for r in data]
        names += [r["employer_name"] for r in data]
        names += [r["guarantor_name"] for r in data]
        ids = [r["national_id"] for r in data]
        cx_validate_names(names)
        cx_validate_ids(ids)
        cx_compute_risk(data)

    cx_ms = bench(cx_full_validate, data)
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"  Pure Python : {py_ms:>8.1f} ms")
    print(f"  ClaraX Rust : {cx_ms:>8.1f} ms")
    print(f"  Speedup     : {speedup:>8.1f}x")

    print(f"\n{'=' * 62}")
    print()


if __name__ == "__main__":
    main()
