import numpy as np

def anomaly_to_score(anomaly_value: float) -> float:
    # IsolationForest decision_function is larger for normal observations.
    # Convert it to a bounded risk contribution.
    return float(np.clip(50 - anomaly_value * 100, 0, 100))

def calculate_risk(fraud_probability: float, anomaly_score: float) -> dict:
    ml_score = fraud_probability * 100
    combined = float(np.clip(0.75 * ml_score + 0.25 * anomaly_score, 0, 100))

    if combined >= 75:
        category = "HIGH"
        action = "Block/hold transaction and require additional verification."
    elif combined >= 45:
        category = "MEDIUM"
        action = "Request step-up authentication or manual review."
    else:
        category = "LOW"
        action = "Allow transaction and continue passive monitoring."

    return {
        "risk_score": round(combined, 2),
        "risk_category": category,
        "recommended_action": action,
    }
