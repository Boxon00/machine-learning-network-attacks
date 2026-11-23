"""Skaliranje vremena treniranja sa brojem trening uzoraka (provera hipoteze H4).

Za fiksne, vec izabrane hiperparametre meri se SAMO vreme treniranja na stratifikovanim
podskupovima trening skupa rastuce velicine. Test skup se ne koristi.
"""
from __future__ import annotations

import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.tree import DecisionTreeClassifier

from . import config
from .data_loader import get_xy, load_train_test, stratified_subsample
from .evaluation import load_json, timed
from .experiment import make_pipeline

SIZES = [2_500, 5_000, 10_000, 20_000, 40_000] if not config.QUICK else [500, 1_000, 2_000]


def run_scaling(train=None, test=None, verbose=True) -> pd.DataFrame:
    config.ensure_directories()
    if train is None:
        train, _ = load_train_test()
    X, y = get_xy(train, "binary")
    M = config.RESULTS_METRICS
    p = {k: load_json(M / f"{f}_binary.json")["params"] for k, f in
         (("dt", "decision_tree"), ("rf", "random_forest"), ("lin", "linear_svm_ceo_trening"), ("rbf", "svm_rbf_uzorak"))}
    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=config.RANDOM_STATE, **p["dt"]),
        "Random Forest": RandomForestClassifier(random_state=config.RANDOM_STATE, n_jobs=1, **p["rf"]),
        "Linear SVM": LinearSVC(dual=False, max_iter=10_000, random_state=config.RANDOM_STATE, **p["lin"]),
        "SVM RBF": SVC(kernel="rbf", cache_size=1000, **p["rbf"]),
    }
    rows = []
    for n in SIZES:
        Xs, ys = stratified_subsample(X, y, n)
        for name, est in models.items():
            pipe = make_pipeline(Xs, clone(est))
            _, t = timed(pipe.fit, Xs, ys)
            rows.append({"Model": name, "N_trening": len(Xs), "Vreme_treniranja_s": t})
            if verbose:
                print(f"[SCALING] n={len(Xs):6d} {name:14s} {t:8.2f}s")
    df = pd.DataFrame(rows)
    df.to_csv(M / "scaling.csv", index=False)
    return df


if __name__ == "__main__":
    run_scaling()
