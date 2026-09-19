import numpy as np
from sklearn.ensemble import IsolationForest


def analyze_activity(activity_records):
    """
    Detect unusual employee activity using Isolation Forest.

    Each activity record should contain:
    active_seconds, idle_seconds, keyboard_events and mouse_events.
    """

    if not activity_records:
        return []

    features = []

    for record in activity_records:
        features.append([
            record.active_seconds or 0,
            record.idle_seconds or 0,
            record.keyboard_events or 0,
            record.mouse_events or 0
        ])

    X = np.array(features, dtype=float)

    # Isolation Forest needs several observations to give
    # meaningful anomaly detection.
    if len(X) < 5:
        return [
            {
                "record": record,
                "status": "Normal",
                "anomaly_score": 0.0
            }
            for record in activity_records
        ]

    model = IsolationForest(
        contamination=0.1,
        random_state=42
    )

    predictions = model.fit_predict(X)
    scores = model.decision_function(X)

    results = []

    for record, prediction, score in zip(
        activity_records, predictions, scores
    ):
        results.append({
            "record": record,
            "status": "Unusual" if prediction == -1 else "Normal",
            "anomaly_score": round(float(score), 4)
        })

    return results