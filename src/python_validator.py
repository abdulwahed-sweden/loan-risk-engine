"""Pure-Python heavy validation for loan applications.

Exercises the workloads Python is slowest at:
  - Character-by-character string scanning (isdigit, isalpha, isspace)
  - Regex pattern matching
  - Decimal arithmetic (division, comparison)
  - Float math (risk scoring)
  - Statistics (mean, median, stdev)
"""

import math
import re
import statistics
from decimal import Decimal

APPROVED_PURPOSES = frozenset({
    "home_purchase", "refinancing", "renovation", "vehicle",
    "education", "business", "debt_consolidation", "other",
})

NATIONAL_ID_RE = re.compile(r"^\d{8}-\d{4}$")
BRANCH_CODE_RE = re.compile(r"^[A-Z]{2}-\d{4}$")


# ── Per-record validation ────────────────────────────────────────────────────

def validate_name(name: str) -> list[str]:
    """Validate a person's name — character scanning is expensive in Python."""
    errors = []
    if not isinstance(name, str):
        return ["not a string"]
    if len(name) > 120:
        errors.append("exceeds 120 characters")
    if not any(c == " " for c in name):
        errors.append("must contain a space")
    if any(c.isdigit() for c in name):
        errors.append("must not contain digits")
    if not all(c.isalpha() or c.isspace() or c == "-" for c in name):
        errors.append("contains invalid characters")
    return errors


def validate_application(record: dict) -> dict:
    """Full validation of a single loan application record."""
    errors = {}

    # ── Name validation (character scanning — Python's weakness) ──
    for field in ("full_name", "employer_name", "guarantor_name"):
        name = record.get(field, "")
        name_errors = validate_name(name)
        if name_errors:
            errors[field] = name_errors

    # ── Pattern matching (regex) ──
    nid = record.get("national_id", "")
    if not NATIONAL_ID_RE.match(nid):
        errors["national_id"] = "invalid format"

    branch = record.get("branch_code", "")
    if not BRANCH_CODE_RE.match(branch):
        errors["branch_code"] = "invalid format"

    # ── Email validation ──
    email = record.get("email", "")
    if email.count("@") != 1 or len(email) > 200:
        errors["email"] = "invalid"

    # ── Phone validation ──
    phone = record.get("phone", "")
    if not phone.startswith("+46") or len(phone) > 20:
        errors["phone"] = "invalid"

    # ── Numeric bounds ──
    age = record.get("age", 0)
    if not isinstance(age, int) or not (18 <= age <= 100):
        errors["age"] = "out of range"

    credit_score = record.get("credit_score", 0)
    if not isinstance(credit_score, int) or not (300 <= credit_score <= 850):
        errors["credit_score"] = "out of range"

    loan_term = record.get("loan_term_months", 0)
    if not isinstance(loan_term, int) or not (6 <= loan_term <= 360):
        errors["loan_term_months"] = "out of range"

    # ── Decimal fields ──
    for field in ("monthly_income", "existing_debt", "monthly_expenses",
                  "loan_amount", "monthly_payment"):
        val = record.get(field)
        if not isinstance(val, Decimal):
            errors[field] = "must be Decimal"

    # ── Cross-field: debt-to-income ratio ──
    income = record.get("monthly_income", Decimal("0"))
    debt = record.get("existing_debt", Decimal("0"))
    if isinstance(income, Decimal) and isinstance(debt, Decimal) and income > 0:
        dti = float(debt / income)
        if dti > 0.5:
            errors["debt_to_income"] = f"ratio {dti:.2f} exceeds 0.5"

    # ── Cross-field: monthly payment affordability ──
    payment = record.get("monthly_payment", Decimal("0"))
    if isinstance(income, Decimal) and isinstance(payment, Decimal) and income > 0:
        payment_ratio = float(payment / income)
        if payment_ratio > 0.4:
            errors["payment_ratio"] = f"{payment_ratio:.2f} exceeds 0.4"

    # ── Purpose must be in approved set ──
    purpose = record.get("purpose", "")
    if purpose not in APPROVED_PURPOSES:
        errors["purpose"] = "not approved"

    # ── Float bounds ──
    rate = record.get("interest_rate", 0.0)
    if not isinstance(rate, (int, float)) or not (1.0 <= rate <= 25.0):
        errors["interest_rate"] = "out of range"

    risk = record.get("risk_score", 0.0)
    if not isinstance(risk, (int, float)) or not (0.0 <= risk <= 100.0):
        errors["risk_score"] = "out of range"

    return {"valid": len(errors) == 0, "errors": errors}


def validate_batch(records: list[dict]) -> list[dict]:
    """Validate a batch of records — pure Python loop."""
    return [validate_application(r) for r in records]


# ── Batch name validation ────────────────────────────────────────────────────

def validate_names_batch(names: list[str]) -> list[dict]:
    """Validate a list of names. Returns list of {valid, errors}."""
    results = []
    for name in names:
        errs = validate_name(name)
        results.append({"valid": len(errs) == 0, "errors": errs})
    return results


# ── Batch pattern matching ───────────────────────────────────────────────────

def validate_ids_batch(ids: list[str]) -> list[bool]:
    """Validate national IDs against regex pattern."""
    return [bool(NATIONAL_ID_RE.match(s)) for s in ids]


# ── Risk score computation ───────────────────────────────────────────────────

def compute_risk_score(record: dict) -> float:
    """Compute a risk score from multiple fields — float math heavy."""
    credit = record.get("credit_score", 500)
    dti = record.get("debt_to_income_ratio", 0.3)
    loan = record.get("loan_amount", Decimal("100000"))
    age = record.get("age", 30)
    rate = record.get("interest_rate", 5.0)

    score = (
        100.0
        - credit / 10.0
        + dti * 50.0
        + math.log1p(float(loan)) * 2.0
        - (5.0 if age >= 25 else 0.0)
        + rate * 0.5
        - math.sqrt(max(0.0, credit - 300)) * 0.3
    )
    return max(0.0, min(100.0, score))


def compute_risk_batch(records: list[dict]) -> list[float]:
    """Compute risk scores for a batch — sequential Python loop."""
    return [compute_risk_score(r) for r in records]


# ── Batch statistics ─────────────────────────────────────────────────────────

def batch_stats(values: list[float]) -> dict:
    """Compute mean, median, stdev, min, max of a list of floats."""
    return {
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values),
        "min": min(values),
        "max": max(values),
        "count": len(values),
    }
