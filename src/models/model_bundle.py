from dataclasses import dataclass
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

@dataclass
class ModelBundle:
    classifier: Pipeline
    anomaly_model: Pipeline
    features: list[str]
