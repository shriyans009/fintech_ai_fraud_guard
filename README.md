# AI Fraud Guard --- AI-Based FinTech Fraud Detection & Risk Scoring

AI Fraud Guard is a FinTech software prototype that uses AI and machine
learning to detect potentially fraudulent transactions, identify
anomalous behaviour, calculate transaction risk, and provide explainable
risk factors.

It combines a **Random Forest fraud classifier** with an **Isolation
Forest anomaly detector** and provides both a **Streamlit web
application** and a **FastAPI REST API**.

> **Academic prototype:** The project uses synthetic transaction data
> and is intended for learning, demonstration and software evaluation.
> It must not be used for real financial decisions.

## Features

### AI and risk detection

-   Random Forest supervised fraud classifier
-   Isolation Forest unsupervised anomaly detector
-   Fraud probability
-   Anomaly score
-   Combined 0--100 risk score
-   LOW / MEDIUM / HIGH classification
-   Human-readable risk factors
-   Recommended action

### Application modules

-   Real-time transaction scoring
-   Fraud and risk analytics dashboard
-   Batch CSV transaction analysis
-   Transaction analysis history
-   Scored CSV export
-   Model evaluation overview
-   FastAPI REST API
-   Swagger/OpenAPI documentation
-   Automated tests
-   Reproducible synthetic dataset generator

## Current demonstration results

  Item                       Result
  ----------------------- ---------
  Total transactions        100,000
  Training transactions      80,000
  Test transactions          20,000
  Fraud transactions          7,949
  Fraud rate                  7.95%
  Accuracy                   0.7951
  Precision                  0.1867
  Recall                     0.4698
  F1 Score                   0.2672
  ROC-AUC                    0.7194

### Batch demonstration

  Risk category     Count
  --------------- -------
  HIGH                  2
  MEDIUM              285
  LOW                 713

Automated tests:

``` text
3 passed in 0.15s
```

These are results from the current synthetic-data prototype.

## Risk calculation

``` text
Risk Score = 0.75 × Fraud Probability Score
           + 0.25 × Anomaly Score
```

``` text
LOW       0–44.99
MEDIUM   45–74.99
HIGH     75–100
```

## Project structure

``` text
fintech_ai_fraud_guard/
│
├── README.md
├── requirements.txt
├── Dockerfile
├── .gitignore
├── examples.json
│
├── data/
│   └── transactions.csv
│
├── artifacts/
│   ├── .gitkeep
│   ├── metrics.json
│   └── model_bundle.joblib
│
├── src/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── dashboard.py
│   ├── data_generator.py
│   ├── predict.py
│   ├── train.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── model_bundle.py
│   └── services/
│       ├── __init__.py
│       ├── explain.py
│       └── risk_engine.py
│
├── tests/
│   ├── __init__.py
│   └── test_risk_engine.py
│
└── docs/
    └── REPORT.md
```

`.venv`, Python caches and other generated files are excluded by
`.gitignore`.

## Setup on Windows with VS Code

Open the project folder in VS Code and open **Terminal → New Terminal**.

Create the environment:

``` powershell
python -m venv .venv
```

Activate:

``` powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation:

``` powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then activate again.

Install dependencies:

``` powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

VS Code may automatically activate `.venv` in new terminals when it is
selected as the Python interpreter. This is normal.

## Generate the dataset

For the current 100,000-row demonstration:

``` powershell
python -m src.data_generator --rows 100000 --output data/transactions.csv
```

For a smaller development run:

``` powershell
python -m src.data_generator --rows 30000 --output data/transactions.csv
```

## Train the AI models

``` powershell
python -m src.train
```

This generates:

``` text
artifacts/model_bundle.joblib
artifacts/metrics.json
```

## Run the Streamlit application

``` powershell
streamlit run src/dashboard.py
```

Normally open:

``` text
http://localhost:8501
```

The dashboard contains:

1.  Transaction Scoring
2.  Analytics Dashboard
3.  Batch Analysis
4.  Transaction History
5.  Model Overview

## Run the REST API

Open another VS Code terminal:

``` powershell
uvicorn src.api:app --reload
```

Normally the API runs at:

``` text
http://127.0.0.1:8000
```

Swagger documentation:

``` text
http://127.0.0.1:8000/docs
```

## API endpoint

### POST `/score`

Example JSON:

``` json
{
  "amount": 85000,
  "hour": 2,
  "distance_from_home_km": 420,
  "distance_from_last_transaction_km": 380,
  "is_foreign": 1,
  "is_new_device": 1,
  "failed_logins_24h": 4,
  "transactions_last_1h": 8,
  "avg_amount_30d": 2500,
  "account_age_days": 120,
  "merchant_risk": 0.85,
  "velocity_ratio": 5.2
}
```

The response contains risk score, category, recommended action, fraud
probability, anomaly score and risk factors.

## Batch CSV format

Required columns:

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

The application validates the CSV, scores the transactions, displays the
results and provides a scored CSV download.

## Run tests

``` powershell
pytest -q
```

Current result:

``` text
3 passed in 0.15s
```

## Architecture

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
```

Training:

``` text
Synthetic Data
      ↓
CSV Dataset
      ↓
Training / Test Split
      ↓
Random Forest + Isolation Forest
      ↓
Model Evaluation
      ↓
Saved Model Bundle
```

## Git workflow

Check the repository:

``` powershell
git status
```

Add files:

``` powershell
git add .
```

Review:

``` powershell
git status
```

Commit:

``` powershell
git commit -m "Initial AI Fraud Guard implementation"
```

Then connect the local repository to the required private GitHub
repository and push the `main` branch.

## Academic scope and limitations

This is an academic prototype using synthetic data. It does not connect
to real bank accounts, payment gateways, customer records or
core-banking systems.

Production deployment would require appropriate security, privacy,
authentication, authorization, monitoring, model validation, governance,
compliance and human-review controls.

## Future scope

-   real or anonymized transaction datasets
-   real-time transaction streaming
-   Kafka/event-based processing
-   database-backed transaction history
-   analyst case management
-   graph-based fraud detection
-   SHAP-based explanations
-   model drift monitoring
-   automatic retraining
-   role-based access control
-   cloud deployment
-   alert notifications
-   model versioning and governance
