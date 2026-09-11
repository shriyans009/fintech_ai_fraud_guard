import sys
from pathlib import Path

# Make the project root importable when Streamlit launches this file directly.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
import pandas as pd
import streamlit as st

from src.config import METRICS_PATH, DATA_PATH, MODEL_PATH, FEATURES
from src.predict import (
    score_transaction,
    score_transactions_batch,
    load_bundle,
)

st.set_page_config(
    page_title="AI Fraud Guard",
    page_icon="🛡️",
    layout="wide",
)

# ---------- Helpers ----------
def ensure_history():
    if "transaction_history" not in st.session_state:
        st.session_state.transaction_history = []

def risk_label(score):
    if score >= 75:
        return "HIGH"
    if score >= 45:
        return "MEDIUM"
    return "LOW"

def risk_color_text(category):
    return {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(category, "⚪")

def score_uploaded_dataframe(df):
    missing = [c for c in FEATURES if c not in df.columns]

    if missing:
        return None, missing

    try:
        # Load the model ONCE
        bundle = load_bundle()

        # Score all transactions efficiently
        scored = score_transactions_batch(
            df,
            bundle=bundle
        )

        return scored, []

    except Exception as exc:
        return None, [f"Batch scoring error: {exc}"]

# ---------- Initial checks ----------
ensure_history()

st.title("🛡️ AI Fraud Guard")
st.caption(
    "AI-powered FinTech transaction fraud detection, anomaly analysis and risk scoring"
)

if not DATA_PATH.exists() or not MODEL_PATH.exists() or not METRICS_PATH.exists():
    st.error(
        "Required data/model files are missing. Run the following from the project root:"
    )
    st.code(
        "python -m src.data_generator --rows 100000 --output data/transactions.csv\n"
        "python -m src.train"
    )
    st.stop()

metrics = json.loads(METRICS_PATH.read_text())

# ---------- Sidebar ----------
with st.sidebar:
    st.header("System Status")
    st.success("AI Model: Online")
    st.success("Risk Engine: Online")
    st.success("Explainability: Online")
    st.success("Batch Scoring: Ready")

    st.divider()
    st.subheader("Risk thresholds")
    st.write("🟢 LOW: 0–44")
    st.write("🟡 MEDIUM: 45–74")
    st.write("🔴 HIGH: 75–100")

    st.divider()
    st.caption(
        "Academic prototype. Synthetic data only. "
        "Not intended for real financial decisions."
    )

# ---------- Navigation ----------
tabs = st.tabs([
    "🛡️ Transaction Scoring",
    "📊 Analytics Dashboard",
    "📁 Batch Analysis",
    "🧾 Transaction History",
    "🤖 Model Overview",
])

# =========================================================
# TAB 1: REAL-TIME TRANSACTION SCORING
# =========================================================
with tabs[0]:
    st.header("Real-Time Transaction Scoring")
    st.write("Enter a transaction and let the AI risk engine evaluate it.")

    c1, c2, c3 = st.columns(3)

    with c1:
        amount = st.number_input(
            "Amount",
            min_value=10.0,
            value=2500.0,
            step=100.0,
        )
        hour = st.slider("Hour of day", 0, 23, 14)
        avg_amount = st.number_input(
            "30-day average amount",
            min_value=20.0,
            value=2000.0,
            step=100.0,
        )
        account_age = st.number_input(
            "Account age (days)",
            min_value=1,
            value=600,
            step=1,
        )

    with c2:
        distance_home = st.number_input(
            "Distance from home (km)",
            min_value=0.0,
            value=8.0,
            step=1.0,
        )
        distance_last = st.number_input(
            "Distance from last transaction (km)",
            min_value=0.0,
            value=4.0,
            step=1.0,
        )
        failed_logins = st.number_input(
            "Failed logins in 24h",
            min_value=0,
            value=0,
            step=1,
        )
        tx_1h = st.number_input(
            "Transactions in last 1h",
            min_value=0,
            value=1,
            step=1,
        )

    with c3:
        foreign = st.selectbox(
            "Foreign transaction",
            [0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
        )
        new_device = st.selectbox(
            "New device",
            [0, 1],
            format_func=lambda x: "No" if x == 0 else "Yes",
        )
        merchant_risk = st.slider(
            "Merchant risk",
            0.0,
            1.0,
            0.15,
            0.01,
        )
        velocity_ratio = st.number_input(
            "Velocity ratio",
            min_value=0.0,
            value=1.5,
            step=0.1,
        )

    if st.button("🔍 Analyze Transaction", type="primary", use_container_width=True):
        transaction = {
            "amount": amount,
            "hour": hour,
            "distance_from_home_km": distance_home,
            "distance_from_last_transaction_km": distance_last,
            "is_foreign": foreign,
            "is_new_device": new_device,
            "failed_logins_24h": failed_logins,
            "transactions_last_1h": tx_1h,
            "avg_amount_30d": avg_amount,
            "account_age_days": account_age,
            "merchant_risk": merchant_risk,
            "velocity_ratio": velocity_ratio,
        }

        result = score_transaction(transaction)

        st.session_state.transaction_history.insert(
            0,
            {
                "timestamp": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                "amount": amount,
                "fraud_probability": result["fraud_probability"],
                "anomaly_score": result["anomaly_score"],
                "risk_score": result["risk_score"],
                "risk_category": result["risk_category"],
            },
        )
        st.session_state.transaction_history = (
            st.session_state.transaction_history[:100]
        )

        st.divider()

        a, b, c, d = st.columns(4)
        a.metric("Risk Score", f'{result["risk_score"]}/100')
        b.metric("Risk Category", f'{risk_color_text(result["risk_category"])} {result["risk_category"]}')
        c.metric("Fraud Probability", f'{result["fraud_probability"]:.1%}')
        d.metric("Anomaly Score", f'{result["anomaly_score"]:.1f}')

        if result["risk_category"] == "HIGH":
            st.error("🚨 " + result["recommended_action"])
        elif result["risk_category"] == "MEDIUM":
            st.warning("⚠️ " + result["recommended_action"])
        else:
            st.success("✅ " + result["recommended_action"])

        st.subheader("Why was this transaction flagged?")
        for factor in result["risk_factors"]:
            st.write("• " + factor)

        st.subheader("AI Decision Summary")
        summary = pd.DataFrame({
            "Signal": ["Fraud probability", "Anomaly score", "Combined risk score"],
            "Value": [
                f'{result["fraud_probability"]:.1%}',
                f'{result["anomaly_score"]:.1f}/100',
                f'{result["risk_score"]:.2f}/100',
            ],
        })
        st.table(summary)

# =========================================================
# TAB 2: ANALYTICS DASHBOARD
# =========================================================
with tabs[1]:
    st.header("📊 Fraud & Risk Analytics")

    df = pd.read_csv(DATA_PATH)

    total = len(df)
    fraud_count = int(df["is_fraud"].sum())
    fraud_rate = df["is_fraud"].mean() * 100
    avg_amount = df["amount"].mean()

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Transactions", f"{total:,}")
    k2.metric("Fraud Transactions", f"{fraud_count:,}")
    k3.metric("Fraud Rate", f"{fraud_rate:.2f}%")
    k4.metric("Average Amount", f"{avg_amount:,.2f}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Fraud Distribution")
        fraud_chart = (
            df["is_fraud"]
            .value_counts()
            .rename(index={0: "Normal", 1: "Fraud"})
            .to_frame("Transactions")
        )
        st.bar_chart(fraud_chart)

    with right:
        st.subheader("Transaction Amount by Class")
        amount_chart = df.groupby("is_fraud")["amount"].mean()
        amount_chart.index = ["Normal", "Fraud"]
        st.bar_chart(amount_chart)

    st.subheader("Fraud Rate by Hour")
    hourly = df.groupby("hour")["is_fraud"].mean() * 100
    st.line_chart(hourly)

    st.subheader("Fraud Rate by Device Type")
    device = df.groupby("is_new_device")["is_fraud"].mean() * 100
    device.index = ["Existing Device", "New Device"]
    st.bar_chart(device)

# =========================================================
# TAB 3: BATCH ANALYSIS
# =========================================================
with tabs[2]:
    st.header("📁 Batch Transaction Analysis")
    st.write(
        "Upload a CSV containing transaction features. The AI model will score every row."
    )

    st.info(
        "Required columns: " + ", ".join(FEATURES)
    )

    uploaded = st.file_uploader(
        "Upload transaction CSV",
        type=["csv"],
        key="batch_csv",
    )

    if uploaded is not None:
        batch_df = pd.read_csv(uploaded)

        st.write(f"Uploaded **{len(batch_df):,} transactions**.")
        st.dataframe(batch_df.head(10), use_container_width=True)

        if st.button("🤖 Run Batch AI Analysis", type="primary"):
            with st.spinner("Scoring transactions..."):
                scored, missing = score_uploaded_dataframe(batch_df)

            if missing:
                st.error("Missing required columns:")
                st.code("\n".join(missing))
            else:
                st.success(f"Successfully scored {len(scored):,} transactions.")

                b1, b2, b3, b4 = st.columns(4)
                b1.metric("Transactions", f"{len(scored):,}")
                b2.metric(
                    "High Risk",
                    f"{(scored['risk_category'] == 'HIGH').sum():,}",
                )
                b3.metric(
                    "Medium Risk",
                    f"{(scored['risk_category'] == 'MEDIUM').sum():,}",
                )
                b4.metric(
                    "Low Risk",
                    f"{(scored['risk_category'] == 'LOW').sum():,}",
                )

                st.subheader("Scored Transactions")
                st.dataframe(scored, use_container_width=True)

                csv_bytes = scored.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Download Scored CSV",
                    data=csv_bytes,
                    file_name="fraud_analysis_results.csv",
                    mime="text/csv",
                )

                st.subheader("Risk Distribution")
                risk_counts = scored["risk_category"].value_counts()
                st.bar_chart(risk_counts)

# =========================================================
# TAB 4: TRANSACTION HISTORY
# =========================================================
with tabs[3]:
    st.header("🧾 Transaction Analysis History")

    if not st.session_state.transaction_history:
        st.info(
            "No transactions have been analyzed in this browser session yet. "
            "Use the Transaction Scoring tab first."
        )
    else:
        history = pd.DataFrame(st.session_state.transaction_history)

        h1, h2, h3 = st.columns(3)
        h1.metric("Analyzed", len(history))
        h2.metric(
            "High Risk",
            int((history["risk_category"] == "HIGH").sum()),
        )
        h3.metric(
            "Average Risk",
            f'{history["risk_score"].mean():.1f}',
        )

        st.dataframe(history, use_container_width=True)

        csv_history = history.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Session History",
            data=csv_history,
            file_name="transaction_history.csv",
            mime="text/csv",
        )

        if st.button("🗑️ Clear History"):
            st.session_state.transaction_history = []
            st.rerun()

# =========================================================
# TAB 5: MODEL OVERVIEW
# =========================================================
with tabs[4]:
    st.header("🤖 AI Model Overview")

    st.write(
        "AI Fraud Guard combines a supervised Random Forest classifier "
        "with an unsupervised Isolation Forest anomaly detector."
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Accuracy", metrics["accuracy"])
    m2.metric("Precision", metrics["precision"])
    m3.metric("Recall", metrics["recall"])
    m4.metric("F1 Score", metrics["f1"])
    m5.metric("ROC-AUC", metrics["roc_auc"])

    st.divider()

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Training Information")
        st.write(f'**Training rows:** {metrics["train_rows"]:,}')
        st.write(f'**Test rows:** {metrics["test_rows"]:,}')
        st.write(f'**Synthetic fraud rate:** {metrics["fraud_rate"]:.2%}')
        st.write("**Classifier:** Random Forest")
        st.write("**Anomaly detector:** Isolation Forest")

    with c2:
        st.subheader("Risk Calculation")
        st.code(
            "Risk Score = 0.75 × Fraud Probability Score\n"
            "           + 0.25 × Anomaly Score"
        )
        st.write("🟢 LOW: score < 45")
        st.write("🟡 MEDIUM: 45 ≤ score < 75")
        st.write("🔴 HIGH: score ≥ 75")

    st.subheader("Input Features")
    st.dataframe(
        pd.DataFrame({"Feature": FEATURES}),
        use_container_width=True,
    )

    st.info(
        "The training data is synthetic and the thresholds are demonstration values. "
        "A production banking system would require real validation data, security, "
        "privacy, model governance, monitoring and regulatory controls."
    )
