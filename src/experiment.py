"""Zajednicka logika eksperimenta: treniranje, merenje vremena, evaluacija i cuvanje rezultata.

Svi algoritmi (Decision Tree, Random Forest, SVM) prolaze kroz iste funkcije
``fit_and_evaluate`` i ``tune_hyperparameters``, cime su uslovi poredivi:
isti test skup, isti pipeline za preprocesiranje, iste metrike i ista metodologija merenja vremena.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split

from . import config
from .evaluation import (bootstrap_ci, compute_binary_metrics, recall_by_attack_category,
                         save_json, timed)
from .preprocessing import (build_preprocessor, get_feature_names, get_feature_origins,
                            log_transformed_columns, make_pipeline)


def get_scores(pipeline, X) -> np.ndarray:
    """Kontinualni skor pozitivne klase (za ROC-AUC): verovatnoca ili rastojanje od hiperravni."""
    clf = pipeline.named_steps["clf"]
    if hasattr(clf, "predict_proba"):
        return pipeline.predict_proba(X)[:, 1]
    return pipeline.decision_function(X)


def tune_hyperparameters(estimator, param_grid: Dict, X_tune: pd.DataFrame, y_tune: pd.Series,
                         scoring: str = "f1") -> Dict:
    """GridSearchCV (stratifikovani k-fold) nad celim pipeline-om, samo na TRENING podacima.

    Preprocesiranje se ponovo uci u svakom foldu (nema curenja iz validacionog folda).
    Test skup se ovde NE koristi.
    """
    pipe = make_pipeline(X_tune, estimator)
    cv = StratifiedKFold(n_splits=config.CV_FOLDS, shuffle=True, random_state=config.RANDOM_STATE)
    gs = GridSearchCV(pipe, param_grid, scoring=scoring, cv=cv, n_jobs=config.N_JOBS_TUNING,
                      refit=False, return_train_score=True)
    gs.fit(X_tune, y_tune)
    res = pd.DataFrame(gs.cv_results_)
    best = res.loc[res["rank_test_score"].idxmin()]
    best_params = {k.replace("clf__", ""): _py(v) for k, v in best["params"].items()}
    return {"best_params": best_params, "best_cv_score": float(best["mean_test_score"]),
            "scoring": scoring, "n_tune": int(len(X_tune)), "cv_folds": config.CV_FOLDS,
            "cv_results": res}


def _py(v):
    return v.item() if isinstance(v, np.generic) else v


def fit_and_evaluate(model_name: str, estimator, X_train, y_train, X_test, y_test,
                     attack_cat_test=None, tag: str = "binary", params: Optional[dict] = None,
                     extra: Optional[dict] = None, save: bool = True, with_ci: bool = True):
    """Trenira pipeline na treningu i evaluira ga na test skupu.

    Meri: vreme treniranja (preprocesiranje + klasifikator), vreme predikcije labela
    na test skupu (preprocesiranje + predikcija). Racuna i metrike na trening skupu
    (za analizu preprilagodjavanja) i bootstrap intervale poverenja na test skupu.

    Returns:
        (result_dict, fitted_pipeline)
    """
    pipe = make_pipeline(X_train, clone(estimator))
    _, fit_t = timed(pipe.fit, X_train, y_train)
    y_pred, pred_t = timed(pipe.predict, X_test)
    y_score = get_scores(pipe, X_test)
    y_pred_train = pipe.predict(X_train)

    test_m = compute_binary_metrics(y_test, y_pred, y_score)
    train_m = compute_binary_metrics(y_train, y_pred_train)
    result = {
        "model": model_name, "task": tag,
        "params": {k: _py(v) for k, v in (params or {}).items()},
        "n_train": int(len(X_train)), "n_test": int(len(X_test)),
        "n_features_after_encoding": len(get_feature_names(pipe.named_steps["prep"])),
        "fit_time_s": fit_t, "predict_time_s": pred_t,
        "predict_time_per_1000_s": pred_t / len(X_test) * 1000,
        "test_metrics": test_m, "train_metrics": train_m,
        "log1p_columns": log_transformed_columns(pipe.named_steps["prep"]),
    }
    if with_ci:
        result["test_ci95"] = bootstrap_ci(y_test, y_pred)
    if attack_cat_test is not None:
        result["detection_by_category"] = recall_by_attack_category(
            attack_cat_test, y_pred).to_dict("records")
    if extra:
        result.update(extra)
    if save:
        slug = model_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        save_json(result, config.RESULTS_METRICS / f"{slug}_{tag}.json")
        np.savez_compressed(config.RESULTS_METRICS / f"{slug}_{tag}_predictions.npz",
                            y_true=np.asarray(y_test), y_pred=np.asarray(y_pred),
                            y_score=np.asarray(y_score))
    return result, pipe


def feature_importance_table(pipe) -> pd.DataFrame:
    """Znacaj karakteristika (po izlaznim kolonama) + agregacija po originalnoj koloni."""
    prep, clf = pipe.named_steps["prep"], pipe.named_steps["clf"]
    df = pd.DataFrame({"feature": get_feature_names(prep),
                       "origin": get_feature_origins(prep),
                       "importance": clf.feature_importances_})
    return df.sort_values("importance", ascending=False).reset_index(drop=True)


def aggregate_importance(df: pd.DataFrame) -> pd.DataFrame:
    """Zbir znacaja po originalnoj koloni (npr. sve ``proto_*`` kolone se sabiraju)."""
    return (df.groupby("origin", as_index=False)["importance"].sum()
              .sort_values("importance", ascending=False).reset_index(drop=True))


def make_validation_split(X, y):
    """Stratifikovana podela TRENINGA na (train_sub, val) za krive (dubina, broj stabala)."""
    return train_test_split(X, y, test_size=config.VALIDATION_FRACTION, stratify=y,
                            random_state=config.RANDOM_STATE)


def prepare_matrices(X_fit, *others):
    """Fituje preprocesor na X_fit i transformise X_fit i ostale skupove (bez curenja)."""
    prep = build_preprocessor(X_fit)
    A = prep.fit_transform(X_fit)
    return (prep, A, *[prep.transform(o) for o in others])
