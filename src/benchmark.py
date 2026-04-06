import time
import statistics
from decimal import Decimal
from clarax_core import serialize_many, validate_many

from schema import loan_schema
from generator import generate_batch


def serialize_pure_python(data: list[dict]) -> list[dict]:
    results = []
    for row in data:
        record = {}
        for k, v in row.items():
            record[k] = str(v) if isinstance(v, Decimal) else v
        results.append(record)
    return results


def validate_pure_python(data: list[dict]) -> list[dict]:
    results = []
    for row in data:
        errors = {}

        name = row.get("applicant_name", "")
        if not isinstance(name, str) or len(name) > 120:
            errors["applicant_name"] = "invalid"

        nid = row.get("national_id", "")
        if not isinstance(nid, str) or len(nid) > 20:
            errors["national_id"] = "invalid"

        age = row.get("age", 0)
        if not isinstance(age, int) or not (18 <= age <= 100):
            errors["age"] = "out of range"

        income = row.get("monthly_income")
        if not isinstance(income, Decimal):
            errors["monthly_income"] = "invalid type"

        debt = row.get("existing_debt")
        if not isinstance(debt, Decimal):
            errors["existing_debt"] = "invalid type"

        cs = row.get("credit_score", 0)
        if not isinstance(cs, int) or not (300 <= cs <= 850):
            errors["credit_score"] = "out of range"

        loan = row.get("loan_amount")
        if not isinstance(loan, Decimal):
            errors["loan_amount"] = "invalid type"

        term = row.get("loan_term_months", 0)
        if not isinstance(term, int) or not (6 <= term <= 360):
            errors["loan_term_months"] = "out of range"

        emp = row.get("employment_type", "")
        if not isinstance(emp, str) or len(emp) > 30:
            errors["employment_type"] = "invalid"

        owner = row.get("is_homeowner")
        if not isinstance(owner, bool):
            errors["is_homeowner"] = "invalid type"

        uid = row.get("bank_account_uuid", "")
        if not isinstance(uid, str) or len(uid) > 36:
            errors["bank_account_uuid"] = "invalid"

        results.append({"valid": len(errors) == 0, "errors": errors})
    return results


def run(count: int, runs: int = 5):
    print(f"\n{'='*54}")
    print(f"  {count:,} loan applications — {runs} runs median")
    print(f"{'='*54}")

    data = generate_batch(count)

    # ── Serialization ──
    py_t, cx_t = [], []
    for _ in range(runs):
        t = time.perf_counter()
        serialize_pure_python(data)
        py_t.append(time.perf_counter() - t)

        t = time.perf_counter()
        serialize_many(data, loan_schema)
        cx_t.append(time.perf_counter() - t)

    py_ms = statistics.median(py_t) * 1000
    cx_ms = statistics.median(cx_t) * 1000
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"\n  Serialization:")
    print(f"    Pure Python : {py_ms:>8.1f} ms")
    print(f"    ClaraX      : {cx_ms:>8.1f} ms")
    print(f"    Speedup     : {speedup:>8.1f}x")

    # ── Validation ──
    py_t, cx_t = [], []
    for _ in range(runs):
        t = time.perf_counter()
        validate_pure_python(data)
        py_t.append(time.perf_counter() - t)

        t = time.perf_counter()
        validate_many(data, loan_schema)
        cx_t.append(time.perf_counter() - t)

    py_ms = statistics.median(py_t) * 1000
    cx_ms = statistics.median(cx_t) * 1000
    speedup = py_ms / cx_ms if cx_ms > 0 else 0

    print(f"\n  Validation:")
    print(f"    Pure Python : {py_ms:>8.1f} ms")
    print(f"    ClaraX      : {cx_ms:>8.1f} ms")
    print(f"    Speedup     : {speedup:>8.1f}x")

    print(f"\n{'='*54}")


if __name__ == "__main__":
    run(1_000)
    run(10_000)
    run(50_000)