from decimal import Decimal
from clarax_core import Schema, Field

loan_schema = Schema({
    "applicant_name":    Field(str,     max_length=120),
    "national_id":       Field(str,     max_length=20),
    "age":               Field(int,     min_value=18,  max_value=100),
    "monthly_income":    Field(Decimal, max_digits=10, decimal_places=2),
    "existing_debt":     Field(Decimal, max_digits=12, decimal_places=2),
    "credit_score":      Field(int,     min_value=300, max_value=850),
    "loan_amount":       Field(Decimal, max_digits=12, decimal_places=2),
    "loan_term_months":  Field(int,     min_value=6,   max_value=360),
    "employment_type":   Field(str,     max_length=30),
    "is_homeowner":      Field(bool),
    "bank_account_uuid": Field(str,     max_length=36),
})