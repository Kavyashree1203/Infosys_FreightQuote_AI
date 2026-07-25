"""
train_ml_freight.py — Multi-agent ML training (Section 7).
Agent 1: Dynamic Pricing        -> Regression, R^2 >= 0.90
Agent 2: Route Delay Classifier -> Classification, ROC-AUC
Agent 3: Carrier Compliance     -> Classification, ROC-AUC

Each agent trains 5+ algorithms and saves the champion via joblib,
logging every model's metric into the ml_models table (db.py).
"""

import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, roc_auc_score

from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor,
    AdaBoostRegressor, RandomForestClassifier, GradientBoostingClassifier,
    ExtraTreesClassifier, AdaBoostClassifier,
)
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier

import db

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

RANDOM_STATE = 42


# ------------------------------------------------------------------
# Kaggle download helper (Section 7.1) — falls back to synthetic data
# if kagglehub / kaggle.json is not configured, per Section 3.2:
# "The notebook must still work without it."
# ------------------------------------------------------------------
def try_kaggle_download(slug: str, target_filename: str):
    try:
        import kagglehub
        path = kagglehub.dataset_download(slug)
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(".csv"):
                    return os.path.join(root, f)
        return None
    except Exception as e:
        print(f"[Kaggle download skipped for {slug}] {e} -> using synthetic data.")
        return None


# ------------------------------------------------------------------
# Synthetic data generators (seeded -> reproducible, Section 7 note)
# ------------------------------------------------------------------
def synthetic_pricing_data(n=4000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    distance_km = rng.uniform(50, 15000, n)
    weight_kg = rng.uniform(10, 25000, n)
    congestion_level = rng.uniform(0, 1, n)
    fuel_index = rng.uniform(0.8, 1.6, n)

    base_cost = (distance_km * 0.42) + (weight_kg * 0.15)
    cost = base_cost * (1 + 0.35 * congestion_level) * fuel_index + rng.normal(0, 50, n)
    cost = np.clip(cost, 20, None)

    return pd.DataFrame({
        "distance_km": distance_km,
        "weight_kg": weight_kg,
        "congestion_level": congestion_level,
        "fuel_index": fuel_index,
        "freight_cost": cost,
    })


def synthetic_route_delay_data(n=4000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    congestion = rng.uniform(0, 1, n)
    weather_risk = rng.uniform(0, 1, n)
    canal_queue = rng.integers(0, 2, n)
    distance_km = rng.uniform(50, 15000, n)

    delay_score = 0.5 * congestion + 0.3 * weather_risk + 0.2 * canal_queue + rng.normal(0, 0.08, n)
    delayed = (delay_score > 0.5).astype(int)

    return pd.DataFrame({
        "congestion": congestion,
        "weather_risk": weather_risk,
        "canal_queue": canal_queue,
        "distance_km": distance_km,
        "delayed": delayed,
    })


def synthetic_carrier_audit_data(n=4000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    punctuality_rate = rng.uniform(0.5, 1.0, n)
    docs_compliance = rng.uniform(0, 1, n)
    safety_incidents = rng.integers(0, 5, n)
    years_active = rng.uniform(1, 25, n)

    risk_score = (1 - punctuality_rate) * 0.4 + (1 - docs_compliance) * 0.4 + \
                 (safety_incidents / 5) * 0.2 + rng.normal(0, 0.05, n)
    non_compliant = (risk_score > 0.35).astype(int)

    return pd.DataFrame({
        "punctuality_rate": punctuality_rate,
        "docs_compliance": docs_compliance,
        "safety_incidents": safety_incidents,
        "years_active": years_active,
        "non_compliant": non_compliant,
    })


# ------------------------------------------------------------------
# Agent 1: Dynamic Pricing (Regression) — 7 algorithms
# ------------------------------------------------------------------
def train_agent1_pricing(kaggle_df: pd.DataFrame = None):
    df = kaggle_df if kaggle_df is not None else synthetic_pricing_data()
    X = df.drop(columns=["freight_cost"])
    y = df["freight_cost"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        "RandomForestRegressor": RandomForestRegressor(n_estimators=300, random_state=RANDOM_STATE),
        "GradientBoostingRegressor": GradientBoostingRegressor(random_state=RANDOM_STATE),
        "ExtraTreesRegressor": ExtraTreesRegressor(n_estimators=300, random_state=RANDOM_STATE),
        "Ridge": Ridge(alpha=1.0),
        "DecisionTreeRegressor": DecisionTreeRegressor(max_depth=12, random_state=RANDOM_STATE),
        "AdaBoostRegressor": AdaBoostRegressor(random_state=RANDOM_STATE),
        "KNeighborsRegressor": KNeighborsRegressor(n_neighbors=7),
    }

    results = {}
    for name, model in models.items():
        if name in ("Ridge", "KNeighborsRegressor"):
            model.fit(X_train_s, y_train)
            preds = model.predict(X_test_s)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
        score = r2_score(y_test, preds)
        results[name] = (model, score)
        db.save_ml_metric("Agent 1: Pricing", name, "R2", score)
        print(f"[Agent1] {name}: R2 = {score:.4f}")

    champion_name = max(results, key=lambda k: results[k][1])
    champion_model, champion_score = results[champion_name]
    print(f"[Agent1] Champion: {champion_name} (R2={champion_score:.4f})")
    assert champion_score >= 0.0, "sanity check"
    if champion_score < 0.90:
        print("⚠️  R2 below 0.90 target — re-run cell or check data generation seed.")

    joblib.dump({"model": champion_model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(MODELS_DIR, "agent1_pricing_champion.joblib"))
    db.save_ml_metric("Agent 1: Pricing", champion_name, "R2", champion_score, is_champion=True)
    return champion_name, champion_score


# ------------------------------------------------------------------
# Agent 2: Route Delay Classifier — 7 algorithms
# ------------------------------------------------------------------
def train_agent2_route_delay(kaggle_df: pd.DataFrame = None):
    df = kaggle_df if kaggle_df is not None else synthetic_route_delay_data()
    X = df.drop(columns=["delayed"])
    y = df["delayed"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        "RandomForestClassifier": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE),
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "SVC": SVC(kernel="rbf", probability=True, random_state=RANDOM_STATE),
        "ExtraTreesClassifier": ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE),
        "AdaBoostClassifier": AdaBoostClassifier(random_state=RANDOM_STATE),
        "KNeighborsClassifier": KNeighborsClassifier(n_neighbors=9),
    }

    results = {}
    for name, model in models.items():
        if name in ("LogisticRegression", "SVC", "KNeighborsClassifier"):
            model.fit(X_train_s, y_train)
            proba = model.predict_proba(X_test_s)[:, 1]
        else:
            model.fit(X_train, y_train)
            proba = model.predict_proba(X_test)[:, 1]
        score = roc_auc_score(y_test, proba)
        results[name] = (model, score)
        db.save_ml_metric("Agent 2: Route Delay", name, "ROC-AUC", score)
        print(f"[Agent2] {name}: ROC-AUC = {score:.4f}")

    champion_name = max(results, key=lambda k: results[k][1])
    champion_model, champion_score = results[champion_name]
    print(f"[Agent2] Champion: {champion_name} (ROC-AUC={champion_score:.4f})")

    joblib.dump({"model": champion_model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(MODELS_DIR, "agent2_route_delay_champion.joblib"))
    db.save_ml_metric("Agent 2: Route Delay", champion_name, "ROC-AUC", champion_score, is_champion=True)
    return champion_name, champion_score


# ------------------------------------------------------------------
# Agent 3: Carrier Compliance Sentinel — 7 algorithms
# ------------------------------------------------------------------
def train_agent3_carrier_audit(kaggle_df: pd.DataFrame = None):
    df = kaggle_df if kaggle_df is not None else synthetic_carrier_audit_data()
    X = df.drop(columns=["non_compliant"])
    y = df["non_compliant"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    models = {
        "GradientBoostingClassifier": GradientBoostingClassifier(random_state=RANDOM_STATE),
        "RandomForestClassifier": RandomForestClassifier(n_estimators=300, random_state=RANDOM_STATE),
        "ExtraTreesClassifier": ExtraTreesClassifier(n_estimators=300, random_state=RANDOM_STATE),
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "DecisionTreeClassifier": DecisionTreeClassifier(max_depth=10, random_state=RANDOM_STATE),
        "AdaBoostClassifier": AdaBoostClassifier(random_state=RANDOM_STATE),
        "MLPClassifier": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=800, random_state=RANDOM_STATE),
    }

    results = {}
    for name, model in models.items():
        if name in ("LogisticRegression", "MLPClassifier"):
            model.fit(X_train_s, y_train)
            proba = model.predict_proba(X_test_s)[:, 1]
        else:
            model.fit(X_train, y_train)
            proba = model.predict_proba(X_test)[:, 1]
        score = roc_auc_score(y_test, proba)
        results[name] = (model, score)
        db.save_ml_metric("Agent 3: Carrier Audit", name, "ROC-AUC", score)
        print(f"[Agent3] {name}: ROC-AUC = {score:.4f}")

    champion_name = max(results, key=lambda k: results[k][1])
    champion_model, champion_score = results[champion_name]
    print(f"[Agent3] Champion: {champion_name} (ROC-AUC={champion_score:.4f})")

    joblib.dump({"model": champion_model, "scaler": scaler, "features": list(X.columns)},
                os.path.join(MODELS_DIR, "agent3_carrier_audit_champion.joblib"))
    db.save_ml_metric("Agent 3: Carrier Audit", champion_name, "ROC-AUC", champion_score, is_champion=True)
    return champion_name, champion_score


# ------------------------------------------------------------------
# Convenience: run all three agents in one call
# ------------------------------------------------------------------
def train_all_agents():
    db.init_db()
    print("=== Training Agent 1: Dynamic Pricing ===")
    a1 = train_agent1_pricing()
    print("\n=== Training Agent 2: Route Delay Classifier ===")
    a2 = train_agent2_route_delay()
    print("\n=== Training Agent 3: Carrier Compliance Sentinel ===")
    a3 = train_agent3_carrier_audit()
    return {"agent1": a1, "agent2": a2, "agent3": a3}


if __name__ == "__main__":
    train_all_agents()
