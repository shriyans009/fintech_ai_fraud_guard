import argparse
from pathlib import Path
import numpy as np
import pandas as pd

from src.config import DATA_PATH, RANDOM_STATE

def generate_transactions(rows=30000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    n = rows

    amount = np.round(np.exp(rng.normal(7.2, 1.0, n)), 2).clip(10, 250000)
    hour = rng.integers(0, 24, n)
    distance_home = np.round(rng.gamma(2.0, 12.0, n), 2)
    distance_last = np.round(rng.gamma(2.0, 9.0, n), 2)
    is_foreign = rng.binomial(1, 0.08, n)
    is_new_device = rng.binomial(1, 0.12, n)
    failed_logins = rng.poisson(0.25, n).clip(0, 8)
    tx_1h = rng.poisson(1.4, n).clip(0, 15)
    avg_amount = np.round(np.exp(rng.normal(7.0, 0.75, n)), 2).clip(20, 100000)
    account_age = rng.integers(15, 3650, n)
    merchant_risk = np.round(rng.beta(2, 8, n), 3)
    velocity_ratio = np.round((amount / (avg_amount + 1)) * (1 + tx_1h / 5), 3)

    # Synthetic fraud mechanism: deliberately mixes behavioral, geographic,
    # device, velocity and merchant signals.
    logit = (
        -5.2
        + 0.000018 * amount
        + 0.95 * is_foreign
        + 1.15 * is_new_device
        + 0.34 * failed_logins
        + 0.12 * tx_1h
        + 0.018 * distance_home
        + 0.012 * distance_last
        + 2.8 * merchant_risk
        + 0.55 * np.log1p(velocity_ratio)
        + 0.55 * (hour <= 4)
        + 0.45 * (account_age < 60)
    )
    probability = 1 / (1 + np.exp(-np.clip(logit, -20, 20)))
    is_fraud = rng.binomial(1, probability)

    return pd.DataFrame({
        "amount": amount,
        "hour": hour,
        "distance_from_home_km": distance_home,
        "distance_from_last_transaction_km": distance_last,
        "is_foreign": is_foreign,
        "is_new_device": is_new_device,
        "failed_logins_24h": failed_logins,
        "transactions_last_1h": tx_1h,
        "avg_amount_30d": avg_amount,
        "account_age_days": account_age,
        "merchant_risk": merchant_risk,
        "velocity_ratio": velocity_ratio,
        "is_fraud": is_fraud,
    })

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=30000)
    parser.add_argument("--output", type=str, default=str(DATA_PATH))
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df = generate_transactions(args.rows)
    df.to_csv(out, index=False)
    print(f"Generated {len(df):,} transactions -> {out}")
    print(f"Fraud rate: {df.is_fraud.mean():.2%}")

if __name__ == "__main__":
    main()
