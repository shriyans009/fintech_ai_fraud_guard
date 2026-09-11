import joblib
import pandas as pd

from src.config import MODEL_PATH, FEATURES
from src.services.risk_engine import anomaly_to_score, calculate_risk
from src.services.explain import explain_transaction


def load_bundle():
    """Load the trained AI model bundle once."""
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model not found. Run:\n"
            "python -m src.data_generator --rows 100000 --output data/transactions.csv\n"
            "python -m src.train"
        )

    return joblib.load(MODEL_PATH)


def score_transaction(transaction: dict, bundle=None) -> dict:
    """
    Score a single transaction.

    If a model bundle is supplied, it is reused instead of being
    loaded from disk again.
    """
    if bundle is None:
        bundle = load_bundle()

    row = {f: transaction[f] for f in FEATURES}
    X = pd.DataFrame([row])

    fraud_probability = float(
        bundle.classifier.predict_proba(X)[0, 1]
    )

    raw_anomaly = float(
        bundle.anomaly_model.decision_function(X)[0]
    )

    anomaly_score = anomaly_to_score(raw_anomaly)

    result = calculate_risk(
        fraud_probability,
        anomaly_score
    )

    result.update({
        "fraud_probability": round(fraud_probability, 4),
        "anomaly_score": round(anomaly_score, 2),
        "risk_factors": explain_transaction(row),
    })

    return result


def score_transactions_batch(df: pd.DataFrame, bundle=None) -> pd.DataFrame:
    """
    Efficiently score an entire DataFrame.

    The model is loaded only once and prediction is performed
    in batches instead of loading the model for every row.
    """

    if bundle is None:
        bundle = load_bundle()

    X = df[FEATURES].copy()

    # -----------------------------
    # Random Forest predictions
    # -----------------------------
    fraud_probabilities = (
        bundle.classifier.predict_proba(X)[:, 1]
    )

    # -----------------------------
    # Isolation Forest predictions
    # -----------------------------
    raw_anomaly_scores = (
        bundle.anomaly_model.decision_function(X)
    )

    anomaly_scores = [
        anomaly_to_score(float(x))
        for x in raw_anomaly_scores
    ]

    # -----------------------------
    # Combine results
    # -----------------------------
    results = []

    for fraud_probability, anomaly_score in zip(
        fraud_probabilities,
        anomaly_scores
    ):
        risk = calculate_risk(
            float(fraud_probability),
            float(anomaly_score)
        )

        results.append({
            "fraud_probability": round(
                float(fraud_probability), 4
            ),
            "anomaly_score": round(
                float(anomaly_score), 2
            ),
            "risk_score": risk["risk_score"],
            "risk_category": risk["risk_category"],
            "recommended_action": risk["recommended_action"],
        })

    result_df = pd.DataFrame(results)

    # Keep original transaction data and append AI results
    output = df.reset_index(drop=True).copy()

    output["fraud_probability"] = result_df[
        "fraud_probability"
    ]

    output["anomaly_score"] = result_df[
        "anomaly_score"
    ]

    output["risk_score"] = result_df[
        "risk_score"
    ]

    output["risk_category"] = result_df[
        "risk_category"
    ]

    output["recommended_action"] = result_df[
        "recommended_action"
    ]

    return output