import json
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from src.config import (
    DATA_PATH,
    MODEL_PATH,
    METRICS_PATH,
    FEATURES,
    RANDOM_STATE,
    ARTIFACT_DIR,
)
from src.models.model_bundle import ModelBundle

def train():
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    X = df[FEATURES]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    classifier = Pipeline([
        ("scaler", StandardScaler()),
        ("model", RandomForestClassifier(
            n_estimators=180,
            max_depth=12,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])
    classifier.fit(X_train, y_train)

    anomaly_model = Pipeline([
        ("scaler", StandardScaler()),
        ("model", IsolationForest(
            n_estimators=150,
            contamination=0.03,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])
    anomaly_model.fit(X_train)

    proba = classifier.predict_proba(X_test)[:, 1]
    pred = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, pred)), 4),
        "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "fraud_rate": round(float(y.mean()), 4),
    }

    bundle = ModelBundle(classifier=classifier, anomaly_model=anomaly_model, features=FEATURES)
    joblib.dump(bundle, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    print(json.dumps(metrics, indent=2))
    print(f"Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
