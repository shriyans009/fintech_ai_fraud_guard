# AI Fraud Guard: AI-Based FinTech Fraud Detection and Risk Scoring

## 1. Need Analysis / Statement of Need

Digital banking and online payments generate large numbers of
transactions that must be processed quickly. Suspicious activity can
involve unusually large amounts, unfamiliar devices, unusual locations,
repeated failed logins, high transaction velocity, foreign transactions,
or high-risk merchants.

Manual checking of every transaction is impractical. AI can assist by
assigning a risk level to transactions and prioritizing those that
require additional verification or review.

**AI Fraud Guard** is an academic FinTech prototype for this purpose. It
combines a supervised Random Forest fraud classifier with an
unsupervised Isolation Forest anomaly detector. Their outputs are
combined into a risk score and accompanied by human-readable risk
factors and a recommended action.

The project demonstrates an AI-assisted transaction-monitoring workflow.
It is not intended to replace a production banking fraud platform or
make real financial decisions.

## 2. Technical Functionality

### 2.1 Synthetic transaction data

The current development dataset contains **100,000 synthetic
transactions**. Features include:

-   transaction amount
-   transaction hour
-   distance from home
-   distance from the previous transaction
-   foreign transaction indicator
-   new-device indicator
-   failed logins in the previous 24 hours
-   transactions in the previous hour
-   30-day average amount
-   account age
-   merchant risk
-   velocity ratio
-   fraud label for model training

### 2.2 Supervised AI model

A **Random Forest classifier** produces a fraud probability. It was
selected because it can capture nonlinear relationships between
transaction and behavioural features while remaining practical for this
academic prototype.

### 2.3 Anomaly detection

An **Isolation Forest** provides a second, unsupervised signal by
identifying transactions that appear unusual compared with the learned
transaction distribution.

### 2.4 Risk engine

The prototype calculates:

**Risk Score = 0.75 × Fraud Probability Score + 0.25 × Anomaly Score**

The result is represented on a 0--100 scale.

        Score Category   Action
  ----------- ---------- ------------------------------------------------
     0--44.99 LOW        Allow and continue passive monitoring
    45--74.99 MEDIUM     Step-up authentication or manual review
      75--100 HIGH       Hold/block and require additional verification

These are demonstration thresholds, not production banking policy.

### 2.5 Explainability

The application produces readable risk factors such as:

-   amount substantially above the 30-day average
-   new device
-   foreign transaction
-   unusual distance
-   repeated failed logins
-   high transaction velocity
-   high merchant risk
-   unusual transaction time

The explanation layer is rule-based and supplements the numerical model
outputs.

### 2.6 Real-time scoring

The Streamlit dashboard accepts transaction details and displays:

1.  risk score
2.  risk category
3.  fraud probability
4.  anomaly score
5.  recommended action
6.  risk factors
7.  AI decision summary

### 2.7 Analytics dashboard

The dashboard provides total transactions, fraud transactions, fraud
rate, average amount, fraud distribution, amount by class, fraud rate by
hour, and fraud rate by device status.

Current dataset results:

  Measure                  Result
  -------------------- ----------
  Total transactions      100,000
  Fraud transactions        7,949
  Fraud rate                7.95%
  Average amount         2,212.38

### 2.8 Batch analysis

The application accepts a CSV containing the transaction features,
validates it, scores all rows, shows risk counts and a risk-distribution
chart, and allows the scored CSV to be downloaded.

The batch implementation loads the trained model once and performs
predictions over the complete DataFrame rather than loading the model
for every row.

A 1,000-transaction demonstration produced:

  Category        Count
  ------------- -------
  Total           1,000
  High risk           2
  Medium risk       285
  Low risk          713

### 2.9 Transaction history

The Streamlit application maintains session-level history containing
timestamp, amount, fraud probability, anomaly score, risk score, and
risk category. The history can be downloaded or cleared.

### 2.10 Model evaluation

The current model run used 80,000 training rows and 20,000 test rows.

  Metric        Result
  ----------- --------
  Accuracy      0.7951
  Precision     0.1867
  Recall        0.4698
  F1 Score      0.2672
  ROC-AUC       0.7194

These are prototype results on synthetic data and should not be
interpreted as production performance.

### 2.11 REST API

FastAPI exposes `POST /score`. It accepts transaction features as JSON
and returns the risk score, category, recommended action, fraud
probability, anomaly score, and risk factors.

Swagger/OpenAPI documentation is available at:

`http://127.0.0.1:8000/docs`

The endpoint was tested successfully with an HTTP 200 response.

### 2.12 Automated testing

The current automated test run produced:

`3 passed in 0.15s`

## 3. Architecture

``` text
                         User / Analyst
                              |
                 +------------+------------+
                 |                         |
                 v                         v
        Streamlit Dashboard          FastAPI REST API
                 |                         |
                 +------------+------------+
                              |
                              v
                     Prediction Service
                              |
                 +------------+------------+
                 |                         |
                 v                         v
          Random Forest            Isolation Forest
          Fraud Probability       Anomaly Detection
                 |                         |
                 +------------+------------+
                              |
                              v
                         Risk Engine
                              |
                              v
                    Risk + Explanation
                              |
                              v
                    User / API Response

Training:
Synthetic Generator -> CSV -> Train/Test Split
                    -> Random Forest + Isolation Forest
                    -> Saved Model Bundle
```

### Main modules

  Module                Purpose
  --------------------- ------------------------------------------
  `data_generator.py`   Generates synthetic transaction data
  `train.py`            Trains and evaluates the AI models
  `predict.py`          Scores individual and batch transactions
  `risk_engine.py`      Calculates risk score and category
  `explain.py`          Produces readable risk factors
  `model_bundle.py`     Stores trained model components
  `dashboard.py`        Streamlit interface
  `api.py`              FastAPI interface
  `tests/`              Automated tests

## 4. Usage / Scope

### Windows / VS Code setup

``` powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

VS Code may automatically activate `.venv` when a new terminal is
opened.

### Generate data

``` powershell
python -m src.data_generator --rows 100000 --output data/transactions.csv
```

### Train

``` powershell
python -m src.train
```

This creates `artifacts/model_bundle.joblib` and
`artifacts/metrics.json`.

### Run dashboard

``` powershell
streamlit run src/dashboard.py
```

Open the displayed local address, normally `http://localhost:8501`.

### Run API

``` powershell
uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000/docs`.

### Run tests

``` powershell
pytest -q
```

### Batch input

Required CSV columns:

``` text
amount
hour
distance_from_home_km
distance_from_last_transaction_km
is_foreign
is_new_device
failed_logins_24h
transactions_last_1h
avg_amount_30d
account_age_days
merchant_risk
velocity_ratio
```

### Scope

The prototype demonstrates transaction fraud screening,
suspicious-transaction prioritization, anomaly detection, batch
analysis, risk workflows, and API integration for FinTech applications.

## 5. Impact Overview

The system demonstrates how AI can support transaction monitoring by
assigning risk levels and helping prioritize suspicious activity.

Potential benefits include:

-   faster identification of suspicious activity
-   prioritization of alerts
-   combination of supervised and unsupervised AI signals
-   readable explanations
-   batch processing
-   API-based integration
-   modular software architecture

A real banking deployment would require security, privacy, compliance,
monitoring, model governance and human-review controls.

## 6. Limitations

1.  The training data is synthetic.
2.  Fraud labels are artificially generated.
3.  The model has not been validated on real customer behaviour.
4.  Risk thresholds are demonstration values.
5.  No real banking or payment system is connected.
6.  Explainability is rule-based.
7.  Transaction history is session-based rather than database-backed.
8.  Production use would require authentication, authorization,
    encryption, monitoring, drift detection, retraining and governance.

## 7. Future Scope

-   real or anonymized transaction datasets
-   streaming transaction scoring
-   Kafka/event-based processing
-   database-backed history
-   analyst case management
-   graph-based fraud detection
-   SHAP-based explanations
-   model drift monitoring
-   automatic retraining
-   role-based access control
-   cloud deployment
-   alert notifications
-   model versioning and governance

## 8. Conclusion

AI Fraud Guard is a working academic FinTech application combining
Random Forest classification, Isolation Forest anomaly detection, risk
scoring, rule-based explanations, a Streamlit dashboard, batch CSV
processing, transaction history, model evaluation, automated tests and a
FastAPI REST interface.

The current implementation demonstrates real-time scoring, batch scoring
of 1,000 transactions, evaluation on a 100,000-transaction synthetic
dataset, API scoring and automated testing. The modular structure allows
future replacement of the synthetic data and individual models when
suitable real-world data and production controls are available.
