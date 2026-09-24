import numpy as np
from sklearn.ensemble import IsolationForest


def extract_features(record):
    """
    Extract normalized, behavioral features from an activity record.
    """
    active_sec = float(getattr(record, "active_seconds", 0) or 0)
    idle_sec = float(getattr(record, "idle_seconds", 0) or 0)
    kb_events = float(getattr(record, "keyboard_events", 0) or 0)
    mouse_events = float(getattr(record, "mouse_events", 0) or 0)

    total_sec = active_sec + idle_sec
    active_ratio = (active_sec / total_sec) if total_sec > 0 else 0.0
    idle_ratio = (idle_sec / total_sec) if total_sec > 0 else 0.0
    events_per_active = (kb_events + mouse_events) / (active_sec + 1.0)
    kb_mouse_ratio = kb_events / (mouse_events + 1.0)
    total_events = kb_events + mouse_events

    return [
        active_sec,
        idle_sec,
        kb_events,
        mouse_events,
        round(active_ratio, 3),
        round(idle_ratio, 3),
        round(events_per_active, 3),
        round(kb_mouse_ratio, 3),
        total_events,
    ]


def generate_anomaly_explanation(record, score):
    """
    Generate an explainable, human-readable reason for why an activity interval was flagged.
    """
    active_sec = getattr(record, "active_seconds", 0) or 0
    idle_sec = getattr(record, "idle_seconds", 0) or 0
    kb_events = getattr(record, "keyboard_events", 0) or 0
    mouse_events = getattr(record, "mouse_events", 0) or 0
    total_sec = active_sec + idle_sec
    total_events = kb_events + mouse_events

    if total_sec > 0 and (idle_sec / total_sec) >= 0.85 and total_events == 0:
        return "Extended idle duration with zero recorded input events."

    if active_sec > 15 and total_events == 0:
        return "Active window reported without corresponding keyboard or mouse inputs."

    if active_sec > 0 and (total_events / active_sec) > 18:
        return "Unusually high input frequency (>18 events/sec), potential macro or automated tool."

    if kb_events > 150 and mouse_events == 0:
        return "Single-mode interaction: unusually high keystroke volume with zero mouse engagement."

    if mouse_events > 200 and kb_events == 0:
        return "High click/scroll frequency with complete absence of keyboard interaction."

    return "Statistical outlier identified across multi-dimensional interaction patterns by Isolation Forest."


def evaluate_single_heuristic(record):
    """
    Heuristic baseline evaluator for cold-start or single-sample API requests.
    """
    active_sec = getattr(record, "active_seconds", 0) or 0
    idle_sec = getattr(record, "idle_seconds", 0) or 0
    kb_events = getattr(record, "keyboard_events", 0) or 0
    mouse_events = getattr(record, "mouse_events", 0) or 0
    total_sec = active_sec + idle_sec
    total_events = kb_events + mouse_events

    is_unusual = False
    reason = "Normal activity pattern."
    score = 0.15

    if total_sec > 0 and (idle_sec / total_sec) >= 0.90 and total_events == 0:
        is_unusual = True
        score = -0.25
        reason = "Extended idle duration with zero recorded input events."
    elif active_sec >= 20 and total_events == 0:
        is_unusual = True
        score = -0.30
        reason = "Active status reported with zero registered input events."
    elif active_sec > 0 and (total_events / active_sec) > 18:
        is_unusual = True
        score = -0.28
        reason = "High input frequency (>18 events/sec), possible automation pattern."

    return {
        "record": record,
        "status": "Unusual" if is_unusual else "Normal",
        "anomaly_score": score,
        "is_anomaly": is_unusual,
        "reason": reason if is_unusual else "Consistent with standard workforce activity ranges.",
    }


def analyze_activity(activity_records):
    """
    Detect unusual employee activity using Isolation Forest with feature engineering
    and explainable AI reasoning.
    """
    if not activity_records:
        return []

    # If small sample size, evaluate with established baseline heuristics
    if len(activity_records) < 5:
        return [evaluate_single_heuristic(rec) for rec in activity_records]

    features = [extract_features(r) for r in activity_records]
    X = np.array(features, dtype=float)

    # Train Isolation Forest
    contamination_rate = max(0.02, min(0.12, 5.0 / len(activity_records)))
    model = IsolationForest(
        contamination=contamination_rate,
        random_state=42,
        n_estimators=100,
    )

    predictions = model.fit_predict(X)
    scores = model.decision_function(X)

    results = []
    for record, pred, score in zip(activity_records, predictions, scores):
        is_unusual = bool(pred == -1)
        rounded_score = round(float(score), 4)

        if is_unusual:
            reason = generate_anomaly_explanation(record, rounded_score)
        else:
            reason = "Consistent with standard workforce interaction distributions."

        results.append({
            "record": record,
            "status": "Unusual" if is_unusual else "Normal",
            "is_anomaly": is_unusual,
            "anomaly_score": rounded_score,
            "reason": reason,
        })

    return results