"""Decision Tree (DecisionTreeClassifier) - binarna klasifikacija.

Samostalno pokretanje:  python -m src.decision_tree
Koraci: (1) kriva dubine stabla (kontrola preprilagodjavanja) na podeli treninga 80/20,
(2) GridSearchCV (3-fold, F1) na stratifikovanom uzorku treninga, (3) treniranje na CELOM treningu
sa najboljim hiperparametrima, (4) evaluacija na test skupu, (5) znacaj karakteristika.
"""
from __future__ import annotations

import pandas as pd
from sklearn.tree import DecisionTreeClassifier

from . import config
from .data_loader import get_xy, load_train_test, stratified_subsample
from .evaluation import save_json
from .experiment import (aggregate_importance, feature_importance_table, fit_and_evaluate,
                         make_validation_split, prepare_matrices, tune_hyperparameters)
from . import visualization as viz

MODEL_NAME = "Decision Tree"
DEPTHS = [2, 4, 6, 8, 10, 12, 15, 20, 25, 30, None]
PARAM_GRID = {
    "clf__criterion": ["gini", "entropy"],
    "clf__max_depth": [5, 10, 20, None],
    "clf__min_samples_leaf": [1, 5, 20],
}


def depth_curve(X_train: pd.DataFrame, y_train: pd.Series) -> pd.DataFrame:
    """F1 na trening/validacionom delu u funkciji max_depth (samo unutar trening skupa)."""
    from sklearn.metrics import f1_score
    Xa, Xv, ya, yv = make_validation_split(X_train, y_train)
    _, A, V = prepare_matrices(Xa, Xv)
    rows = []
    for d in DEPTHS:
        clf = DecisionTreeClassifier(max_depth=d, random_state=config.RANDOM_STATE).fit(A, ya)
        rows.append({"max_depth": d, "depth_label": "None" if d is None else str(d),
                     "train_f1": f1_score(ya, clf.predict(A)), "val_f1": f1_score(yv, clf.predict(V)),
                     "n_leaves": clf.get_n_leaves(), "actual_depth": clf.get_depth()})
    return pd.DataFrame(rows)


def run_experiment(train: pd.DataFrame = None, test: pd.DataFrame = None, verbose: bool = True) -> dict:
    """Pokrece kompletan eksperiment za Decision Tree i cuva rezultate."""
    config.ensure_directories()
    if train is None or test is None:
        train, test = load_train_test()
    X_tr, y_tr = get_xy(train, "binary")
    X_te, y_te = get_xy(test, "binary")

    # (1) kriva dubine
    curve = depth_curve(X_tr, y_tr)
    curve.to_csv(config.RESULTS_METRICS / "dt_depth_curve.csv", index=False)
    viz.plot_depth_curve(curve)

    # (2) podesavanje hiperparametara
    X_t, y_t = stratified_subsample(X_tr, y_tr, config.TUNING_SAMPLE_SIZE)
    tuned = tune_hyperparameters(DecisionTreeClassifier(random_state=config.RANDOM_STATE), PARAM_GRID, X_t, y_t)
    tuned["cv_results"].drop(columns=["params"]).to_csv(config.RESULTS_METRICS / "dt_cv_results.csv", index=False)
    best = tuned["best_params"]
    if verbose:
        print(f"[DT] najbolji parametri: {best} (CV F1={tuned['best_cv_score']:.4f})")

    # (3)+(4) finalni model na celom treningu, evaluacija na testu
    est = DecisionTreeClassifier(random_state=config.RANDOM_STATE, **best)
    result, pipe = fit_and_evaluate(MODEL_NAME, est, X_tr, y_tr, X_te, y_te,
                                    attack_cat_test=test[config.TARGET_MULTICLASS], params=best,
                                    extra={"tuning": {k: v for k, v in tuned.items() if k != "cv_results"}})
    result["tree_depth"] = int(pipe.named_steps["clf"].get_depth())
    result["n_leaves"] = int(pipe.named_steps["clf"].get_n_leaves())
    save_json(result, config.RESULTS_METRICS / "decision_tree_binary.json")

    # (5) znacaj karakteristika
    imp = feature_importance_table(pipe)
    imp.to_csv(config.RESULTS_METRICS / "dt_feature_importance.csv", index=False)
    agg = aggregate_importance(imp)
    agg.to_csv(config.RESULTS_METRICS / "dt_feature_importance_aggregated.csv", index=False)
    viz.plot_feature_importance(agg, "Decision Tree: značaj karakteristika (agregirano po originalnoj koloni)",
                                "dt_feature_importance.png")
    if verbose:
        m = result["test_metrics"]
        print(f"[DT] test: acc={m['accuracy']:.4f} prec={m['precision']:.4f} rec={m['recall']:.4f} "
              f"f1={m['f1']:.4f} auc={m['roc_auc']:.4f} fit={result['fit_time_s']:.2f}s pred={result['predict_time_s']:.2f}s")
    return result


if __name__ == "__main__":
    run_experiment()
