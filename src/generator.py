import random
import uuid
from decimal import Decimal

NAMES = [
    "Erik Andersson", "Sara Lindqvist", "Mohammed Al-Hassan",
    "Anna Karlsson",  "Lars Eriksson",  "Fatima Bergström",
    "Johan Nilsson",  "Maria Svensson", "Ahmed Mansour",
    "Ingrid Johansson", "Omar Khalid", "Astrid Magnusson",
]

EMPLOYMENT_TYPES = ["employed", "self_employed", "retired", "unemployed"]


def generate_application() -> dict:
    return {
        "applicant_name":    random.choice(NAMES),
        "national_id":       f"{random.randint(19500101,20051231)}-{random.randint(1000,9999)}",
        "age":               random.randint(18, 75),
        "monthly_income":    Decimal(str(round(random.uniform(15000, 120000), 2))),
        "existing_debt":     Decimal(str(round(random.uniform(0, 500000), 2))),
        "credit_score":      random.randint(300, 850),
        "loan_amount":       Decimal(str(round(random.uniform(50000, 2000000), 2))),
        "loan_term_months":  random.choice([12, 24, 36, 60, 120, 240]),
        "employment_type":   random.choice(EMPLOYMENT_TYPES),
        "is_homeowner":      random.choice([True, False]),
        "bank_account_uuid": str(uuid.uuid4()),
    }


def generate_batch(count: int) -> list[dict]:
    return [generate_application() for _ in range(count)]