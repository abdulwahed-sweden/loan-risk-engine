"""Generate complex loan application records for heavy benchmarking.

Each record has 25+ fields across nested sections: applicant info,
financials, loan request, and metadata. Designed to stress-test
string scanning, regex patterns, Decimal arithmetic, and cross-field
validation — workloads where Rust has a genuine advantage over Python.
"""

import math
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal

FIRST_NAMES = [
    "Erik", "Sara", "Mohammed", "Anna", "Lars", "Fatima", "Johan",
    "Maria", "Ahmed", "Ingrid", "Omar", "Astrid", "Karl", "Linnea",
    "Ali", "Elsa", "Fredrik", "Hanna", "Ibrahim", "Sigrid",
]

LAST_NAMES = [
    "Andersson", "Lindqvist", "Al-Hassan", "Karlsson", "Eriksson",
    "Bergstrom", "Nilsson", "Svensson", "Mansour", "Johansson",
    "Khalid", "Magnusson", "Pettersson", "Gustafsson", "Olsson",
]

APPROVED_PURPOSES = [
    "home_purchase", "refinancing", "renovation", "vehicle",
    "education", "business", "debt_consolidation", "other",
]

BRANCH_CODES = [
    "ST-1001", "GB-2045", "MM-3012", "UP-4077", "LK-5033",
    "NO-6018", "VX-7099", "HJ-8042", "QR-9001", "ZA-1234",
]

TAG_OPTIONS = [
    "first_time_buyer", "returning_customer", "premium", "referral",
    "online", "branch_visit", "pre_approved", "urgent", "seasonal",
    "government_program", "green_loan", "fixed_rate", "variable_rate",
]


def _random_decimal(low: float, high: float, places: int = 2) -> Decimal:
    return Decimal(str(round(random.uniform(low, high), places)))


def generate_heavy_application() -> dict:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    full_name = f"{first} {last}"
    age = random.randint(18, 75)
    birth_year = 2026 - age
    national_id = f"{birth_year}{random.randint(1, 12):02d}{random.randint(1, 28):02d}-{random.randint(1000, 9999)}"

    monthly_income = _random_decimal(15_000, 120_000)
    existing_debt = _random_decimal(0, 500_000)
    monthly_expenses = _random_decimal(5_000, 60_000)
    credit_score = random.randint(300, 850)

    dti = float(existing_debt / monthly_income) if monthly_income > 0 else 99.0

    loan_amount = _random_decimal(50_000, 5_000_000)
    loan_term = random.choice([12, 24, 36, 60, 120, 180, 240, 300, 360])
    interest_rate = round(random.uniform(1.5, 15.0), 2)

    # Monthly payment: simple amortization approximation
    monthly_rate = interest_rate / 100.0 / 12.0
    if monthly_rate > 0:
        payment = float(loan_amount) * monthly_rate / (1 - math.pow(1 + monthly_rate, -loan_term))
    else:
        payment = float(loan_amount) / loan_term
    monthly_payment = Decimal(str(round(payment, 2)))

    # Risk scoring
    risk_score = max(0.0, min(100.0,
        100.0
        - credit_score / 10.0
        + dti * 50.0
        + math.log1p(float(loan_amount)) * 2.0
        - (1.0 if age >= 25 else 0.0) * 5.0
    ))
    if risk_score < 30:
        risk_cat = "LOW"
    elif risk_score < 60:
        risk_cat = "MEDIUM"
    elif risk_score < 80:
        risk_cat = "HIGH"
    else:
        risk_cat = "REJECTED"

    approval_prob = max(0.0, min(1.0, 1.0 - risk_score / 100.0))

    submitted = datetime.now() - timedelta(days=random.randint(0, 365))
    num_tags = random.randint(0, 5)

    return {
        # ── Applicant ──
        "full_name": full_name,
        "national_id": national_id,
        "age": age,
        "email": f"{first.lower()}.{last.lower()}@example.com",
        "phone": f"+46{random.randint(700000000, 799999999)}",
        # ── Financials ──
        "monthly_income": monthly_income,
        "existing_debt": existing_debt,
        "credit_score": credit_score,
        "debt_to_income_ratio": round(dti, 4),
        "monthly_expenses": monthly_expenses,
        # ── Loan request ──
        "loan_amount": loan_amount,
        "loan_term_months": loan_term,
        "interest_rate": interest_rate,
        "monthly_payment": monthly_payment,
        "purpose": random.choice(APPROVED_PURPOSES),
        # ── Risk assessment ──
        "risk_score": round(risk_score, 2),
        "risk_category": risk_cat,
        "approval_probability": round(approval_prob, 4),
        # ── Metadata ──
        "application_id": str(uuid.uuid4()),
        "submitted_at": submitted.isoformat(),
        "branch_code": random.choice(BRANCH_CODES),
        "notes": f"Application from {full_name}, {risk_cat} risk" if random.random() > 0.3 else None,
        "tags": random.sample(TAG_OPTIONS, num_tags),
        # ── Extra string fields (make name validation heavier) ──
        "employer_name": f"{random.choice(LAST_NAMES)} & {random.choice(LAST_NAMES)} AB",
        "guarantor_name": f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
    }


def generate_heavy_batch(count: int) -> list[dict]:
    return [generate_heavy_application() for _ in range(count)]
