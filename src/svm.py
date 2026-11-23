"""Support Vector Machine - binarna klasifikacija.

Samostalno pokretanje:  python -m src.svm
Tri varijante (sve evaluirane na CELOM test skupu):
  1. Linear SVM (LinearSVC) - trening na CELOM trening skupu;
  2. Linear SVM (uzorak)    - trening na istom stratifikovanom uzorku kao RBF (izolovanje efekta kernela);
  3. SVM RBF (uzorak)       - SVC(kernel='rbf') na stratifikovanom uzorku trening skupa
                              zbog racunske slozenosti (priblizno O(n^2)-O(n^3)).
Rezultati varijante 3 NISU rezultati na kompletnom trening skupu; u radu se tako i oznacavaju.
"""
from __future__ import annotations

import pandas as pd
from sklearn.svm import SVC, LinearSVC

from . import config
from .data_loader import get_xy, load_train_test, stratified_subsample
from .experiment import fit_and_evaluate, tune_hyperparameters
from . import visualization as viz

NAME_LINEAR = "Linear SVM (ceo trening)"
NAME_LINEAR_SAMPLE = "Linear SVM (uzorak)"
NAME_RBF = "SVM RBF (uzorak)"
LINEAR_GRID = {"clf__C": [0.01, 0.1, 1, 10]}
RBF_GRID = {"clf__C": [1, 10, 100], "clf__gamma": [0.001, 0.01, 0.1]}


def _linear(C: float = 1.0) -> LinearSVC:
    # dual=False: preporuceno kada je n_samples > n_features
    return LinearSVC(C=C, dual=False, max_iter=10_000, random_state=config.RANDOM_STATE)


def run_experiment(train: pd.DataFrame = None, test: pd.DataFrame = None, verbose: bool = True) -> dict:
    config.ensure_directories()
    if train is None or test is None:
        train, test = load_train_test()
    X_tr, y_tr = get_xy(train, "binary")
    X_te, y_te = get_xy(test, "binary")
    cats = test[config.TARGET_MULTICLASS]
    out = {}

    # ---- 1. Linear SVM: tuning na uzorku, finalni fit na celom treningu
    X_t, y_t = stratified_subsample(X_tr, y_tr, config.TUNING_SAMPLE_SIZE)
    tl = tune_hyperparameters(_linear(), LINEAR_GRID, X_t, y_t)
    tl["cv_results"].drop(columns=["params"]).to_csv(config.RESULTS_METRICS / "svm_linear_cv_results.csv", index=False)
    bl = tl["best_params"]
    if verbose:
        print(f"[SVM-lin] najbolji parametri: {bl} (CV F1={tl['best_cv_score']:.4f})")
    out["linear"], _ = fit_and_evaluate(
        NAME_LINEAR, _linear(**bl), X_tr, y_tr, X_te, y_te, attack_cat_test=cats, params=bl, tag="binary",
        extra={"tuning": {k: v for k, v in tl.items() if k != "cv_results"}, "sampled": False})

    # ---- uzorak za RBF (i za Linear SVM na uzorku)
    X_s, y_s = stratified_subsample(X_tr, y_tr, config.SVM_RBF_TRAIN_SAMPLE)
    out["linear_sample"], _ = fit_and_evaluate(
        NAME_LINEAR_SAMPLE, _linear(**bl), X_s, y_s, X_te, y_te, attack_cat_test=cats, params=bl, tag="binary",
        extra={"sampled": True, "sample_size": int(len(X_s))})

    # ---- 3. RBF: tuning C/gamma na podskupu uzorka, finalni fit na uzorku
    X_rt, y_rt = stratified_subsample(X_s, y_s, config.SVM_RBF_TUNING_SAMPLE)
    tr_ = tune_hyperparameters(SVC(kernel="rbf", cache_size=1000), RBF_GRID, X_rt, y_rt)
    cv = tr_["cv_results"]
    cv.drop(columns=["params"]).to_csv(config.RESULTS_METRICS / "svm_rbf_cv_results.csv", index=False)
    viz.plot_param_heatmap(cv.rename(columns={"param_clf__C": "C", "param_clf__gamma": "gamma"}),
                           "gamma", "C", "mean_test_score", "SVM RBF: CV F1 u funkciji C i gamma",
                           "svm_rbf_grid.png")
    br = tr_["best_params"]
    if verbose:
        print(f"[SVM-rbf] najbolji parametri: {br} (CV F1={tr_['best_cv_score']:.4f})")
    out["rbf"], _ = fit_and_evaluate(
        NAME_RBF, SVC(kernel="rbf", cache_size=1000, **br), X_s, y_s, X_te, y_te, attack_cat_test=cats,
        params=br, tag="binary",
        extra={"tuning": {k: v for k, v in tr_.items() if k != "cv_results"}, "sampled": True,
               "sample_size": int(len(X_s))})
    if verbose:
        for k, r in out.items():
            m = r["test_metrics"]
            print(f"[SVM:{k}] acc={m['accuracy']:.4f} prec={m['precision']:.4f} rec={m['recall']:.4f} "
                  f"f1={m['f1']:.4f} auc={m['roc_auc']:.4f} fit={r['fit_time_s']:.2f}s pred={r['predict_time_s']:.2f}s")
    return out


if __name__ == "__main__":
    run_experiment()
