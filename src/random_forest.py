"""Random Forest (RandomForestClassifier) - binarna klasifikacija.

Samostalno pokretanje:  python -m src.random_forest
Koraci: (1) kriva broja stabala na podeli treninga 80/20 (izbor n_estimators),
(2) GridSearchCV (3-fold, F1) ostalih hiperparametara na stratifikovanom uzorku treninga,
(3) treniranje na CELOM treningu, (4) evaluacija na testu, (5) znacaj karakteristika.
"""
from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, accuracy_score

from . import config
from .data_loader import get_xy, load_train_test, stratified_subsample
from .evaluation import save_json, timed
from .experiment import (aggregate_importance, feature_importance_table, fit_and_evaluate,
                         make_validation_split, prepare_matrices, tune_hyperparameters)
from . import visualization as viz

MODEL_NAME = "Random Forest"
N_TREES = [10, 25, 50, 100, 200, 300] if not config.QUICK else [5, 10, 20]
PARAM_GRID = {
    "clf__max_depth": [None, 25],
    "clf__min_samples_leaf": [1, 3],
    "clf__max_features": ["sqrt", "log2"],
}
TUNING_TREES = 100 if not config.QUICK else 20


def trees_curve(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """F1/Accuracy na validacionom delu i vreme treniranja u funkciji broja stabala."""
    Xa, Xv, ya, yv = make_validation_split(X_train, y_train)
    _, A, V = prepare_matrices(Xa, Xv)
    rows = []
    for n in N_TREES:
        rf = RandomForestClassifier(n_estimators=n, random_state=config.RANDOM_STATE, n_jobs=config.N_JOBS_FIT)
        _, ft = timed(rf.fit, A, ya)
        pv = rf.predict(V)
        rows.append({"n_estimators": n, "val_f1": f1_score(yv, pv), "val_accuracy": accuracy_score(yv, pv),
                     "fit_time_s": ft})
    return pd.DataFrame(rows)


def choose_n_estimators(curve: pd.DataFrame, tol: float = 0.0005) -> int:
    """Najmanji broj stabala ciji je validacioni F1 u okviru ``tol`` od maksimuma (pravilo parsimonije)."""
    best = curve["val_f1"].max()
    return int(curve.loc[curve["val_f1"] >= best - tol, "n_estimators"].min())


def run_experiment(train: pd.DataFrame = None, test: pd.DataFrame = None, verbose: bool = True) -> dict:
    config.ensure_directories()
    if train is None or test is None:
        train, test = load_train_test()
    X_tr, y_tr = get_xy(train, "binary")
    X_te, y_te = get_xy(test, "binary")

    curve = trees_curve(X_tr, y_tr)
    curve.to_csv(config.RESULTS_METRICS / "rf_trees_curve.csv", index=False)
    viz.plot_trees_curve(curve)
    n_trees = choose_n_estimators(curve)
    if verbose:
        print(f"[RF] izabran broj stabala: {n_trees}")

    X_t, y_t = stratified_subsample(X_tr, y_tr, config.TUNING_SAMPLE_SIZE)
    base = RandomForestClassifier(n_estimators=TUNING_TREES, random_state=config.RANDOM_STATE, n_jobs=1)
    tuned = tune_hyperparameters(base, PARAM_GRID, X_t, y_t)
    tuned["cv_results"].drop(columns=["params"]).to_csv(config.RESULTS_METRICS / "rf_cv_results.csv", index=False)
    best = {**tuned["best_params"], "n_estimators": n_trees}
    if verbose:
        print(f"[RF] najbolji parametri: {best} (CV F1={tuned['best_cv_score']:.4f})")

    est = RandomForestClassifier(random_state=config.RANDOM_STATE, n_jobs=config.N_JOBS_FIT, **best)
    result, pipe = fit_and_evaluate(MODEL_NAME, est, X_tr, y_tr, X_te, y_te,
                                    attack_cat_test=test[config.TARGET_MULTICLASS], params=best,
                                    extra={"tuning": {k: v for k, v in tuned.items() if k != "cv_results"},
                                           "tuning_trees": TUNING_TREES})
    imp = feature_importance_table(pipe)
    imp.to_csv(config.RESULTS_METRICS / "rf_feature_importance.csv", index=False)
    agg = aggregate_importance(imp)
    agg.to_csv(config.RESULTS_METRICS / "rf_feature_importance_aggregated.csv", index=False)
    viz.plot_feature_importance(agg, "Random Forest: značaj karakteristika (agregirano po originalnoj koloni)",
                                "rf_feature_importance.png", color="#2a9d8f")
    if verbose:
        m = result["test_metrics"]
        print(f"[RF] test: acc={m['accuracy']:.4f} prec={m['precision']:.4f} rec={m['recall']:.4f} "
              f"f1={m['f1']:.4f} auc={m['roc_auc']:.4f} fit={result['fit_time_s']:.2f}s pred={result['predict_time_s']:.2f}s")
    return result


if __name__ == "__main__":
    run_experiment()
