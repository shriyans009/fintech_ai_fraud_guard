def explain_transaction(row: dict) -> list[str]:
    factors = []

    amount = float(row["amount"])
    avg = float(row["avg_amount_30d"])
    if avg > 0 and amount > 3 * avg:
        factors.append("Transaction amount is much higher than the 30-day average.")

    if int(row["is_new_device"]) == 1:
        factors.append("Transaction originated from a new device.")

    if int(row["is_foreign"]) == 1:
        factors.append("Transaction is marked as international/foreign.")

    if float(row["distance_from_home_km"]) > 100:
        factors.append("Transaction location is far from the usual home location.")

    if int(row["failed_logins_24h"]) >= 3:
        factors.append("Multiple failed login attempts were observed in the last 24 hours.")

    if int(row["transactions_last_1h"]) >= 6:
        factors.append("High transaction velocity was observed in the last hour.")

    if float(row["merchant_risk"]) >= 0.6:
        factors.append("Merchant risk indicator is relatively high.")

    if float(row["velocity_ratio"]) >= 4:
        factors.append("Transaction velocity/amount ratio is unusually high.")

    if int(row["hour"]) <= 4:
        factors.append("Transaction occurred during a low-activity overnight period.")

    return factors or ["No strong rule-based risk factor was detected; model probability is the primary signal."]
