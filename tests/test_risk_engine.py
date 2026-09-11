from src.services.risk_engine import calculate_risk, anomaly_to_score

def test_high_risk():
    result = calculate_risk(0.95, 90)
    assert result["risk_category"] == "HIGH"
    assert result["risk_score"] >= 75

def test_low_risk():
    result = calculate_risk(0.05, 10)
    assert result["risk_category"] == "LOW"
    assert result["risk_score"] < 45

def test_anomaly_score_is_bounded():
    assert 0 <= anomaly_to_score(-2) <= 100
    assert 0 <= anomaly_to_score(2) <= 100
