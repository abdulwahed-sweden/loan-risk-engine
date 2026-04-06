# Loan Risk Engine

Benchmark project for [ClaraX](https://github.com/abdulwahed-sweden/clarax) -- measures Rust-accelerated serialization and validation against pure Python on realistic loan application data.

## What this project does

Generates loan application records (applicant info, financials, risk scoring, metadata) and benchmarks ClaraX against pure Python across two workload types:

**Schema operations** (dict serialization and validation):

| Operation (50K records) | Python | ClaraX | Speedup |
|---|---|---|---|
| Serialize (11 fields) | 115 ms | 53 ms | **2.2x** |
| Validate (11 fields) | 80 ms | 59 ms | **1.4x** |

**Batch operations** (where Rust dominates):

| Operation (50K records) | Python | ClaraX | Speedup |
|---|---|---|---|
| Name validation (150K strings) | 888 ms | 122 ms | **7.3x** |
| Pattern matching (50K IDs) | 24 ms | 3 ms | **7.3x** |
| Risk computation (Rayon parallel) | 98 ms | 32 ms | **3.1x** |
| Batch statistics | 46 ms | 1.4 ms | **32.7x** |
| Full validation combined | 1,187 ms | 191 ms | **6.2x** |

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Run benchmarks

```bash
cd src

# Schema serialization and validation (11-field loan records)
python3 benchmark.py

# Heavy workload (25-field records, character scanning, pattern matching, Rayon parallel)
python3 heavy_benchmark.py
```

## Project structure

```
src/
  schema.py           -- ClaraX schema definition (11 loan fields)
  generator.py        -- Simple loan record generator
  benchmark.py        -- Schema serialize/validate benchmark
  heavy_generator.py  -- Complex 25-field record generator
  python_validator.py -- Pure Python validation (character scanning, regex, Decimal)
  heavy_benchmark.py  -- Batch operations benchmark (names, IDs, risk, stats)
```

## Requirements

- Python 3.11+
- [clarax-core](https://pypi.org/project/clarax-core/) 1.0.1
- Faker 40.12.0

## Author

[Abdulwahed Mansour](https://github.com/abdulwahed-sweden)
