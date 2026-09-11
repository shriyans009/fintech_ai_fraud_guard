from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.predict import score_transaction

app = FastAPI(
    title="AI Fraud Guard API",
    description="AI-powered FinTech transaction fraud and risk scoring API.",
    version="1.0.0",
)

class Transaction(BaseModel):
    amount: float = Field(gt=0)
    hour: int = Field(ge=0, le=23)
    distance_from_home_km: float = Field(ge=0)
    distance_from_last_transaction_km: float = Field(ge=0)
    is_foreign: int = Field(ge=0, le=1)
    is_new_device: int = Field(ge=0, le=1)
    failed_logins_24h: int = Field(ge=0)
    transactions_last_1h: int = Field(ge=0)
    avg_amount_30d: float = Field(gt=0)
    account_age_days: int = Field(ge=1)
    merchant_risk: float = Field(ge=0, le=1)
    velocity_ratio: float = Field(ge=0)

@app.get("/")
def root():
    return {"service": "AI Fraud Guard", "status": "running"}

@app.post("/score")
def score(transaction: Transaction):
    return score_transaction(transaction.model_dump())
