from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ARTIFACT_DIR = ROOT / "artifacts"
DATA_PATH = DATA_DIR / "transactions.csv"
MODEL_PATH = ARTIFACT_DIR / "model_bundle.joblib"
METRICS_PATH = ARTIFACT_DIR / "metrics.json"

FEATURES = [
    "amount",
    "hour",
    "distance_from_home_km",
    "distance_from_last_transaction_km",
    "is_foreign",
    "is_new_device",
    "failed_logins_24h",
    "transactions_last_1h",
    "avg_amount_30d",
    "account_age_days",
    "merchant_risk",
    "velocity_ratio",
]

RANDOM_STATE = 42
