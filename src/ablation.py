"""Ablaciona (analiza osetljivosti) studija sa fiksnim, vec izabranim hiperparametrima.

Varijante (primenjene na DT, RF i Linear SVM sa celim treningom):
  * Osnovni            - zvanicni skup karakteristika (rezultati iz glavnog eksperimenta);
  * Bez TCP seq.       - uklonjene kolone stcpb i dtcpb (TCP sekvencni brojevi);
  * Bez duplikata      - uklonjeni identicni zapisi (osim id) i iz treninga i iz testa.
Hiperparametri se NE podesavaju ponovo, pa je ovo analiza osetljivosti, a ne novi glavni eksperiment.
"""
from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.tree import DecisionTreeClassifier

from . import config
from .data_loader import drop_duplicate_records, get_xy, load_train_test
from .evaluation import load_json
from .experiment import fit_and_evaluate


def _estimators():
    M = config.RESULTS_METRICS
    dt = load_json(M / "decision_tree_binary.json")["params"]
    rf = load_json(M / "random_forest_binary.json")["params"]
    sv = load_json(M / "linear_svm_ceo_trening_binary.json")["params"]
    return {
        "Decision Tree": (DecisionTreeClassifier(random_state=config.RANDOM_STATE, **dt), dt),
        "Random Forest": (RandomForestClassifier(random_state=config.RANDOM_STATE, n_jobs=config.N_JOBS_FIT, **rf), rf),
        "Linear SVM (ceo trening)": (LinearSVC(dual=False, max_iter=10_000, random_state=config.RANDOM_STATE, **sv), sv),
    }


def run_ablation(train: pd.DataFrame = None, test: pd.DataFrame = None, verbose: bool = True) -> pd.DataFrame:
    config.ensure_directories()
    if train is None or test is None:
        train, test = load_train_test()
    variants = {
        "Osnovni": (train, test, ()),
        "Bez TCP seq. (stcpb, dtcpb)": (train, test, config.TCP_SEQ_COLUMNS),
        "Bez duplikata": (drop_duplicate_records(train), drop_duplicate_records(test), ()),
    }
    rows = []
    for vname, (tr, te, drop) in variants.items():
        X_tr, y_tr = get_xy(tr, "binary", drop_columns=drop)
        X_te, y_te = get_xy(te, "binary", drop_columns=drop)
        for mname, (est, params) in _estimators().items():
            r, _ = fit_and_evaluate(mname, est, X_tr, y_tr, X_te, y_te, params=params, save=False, with_ci=False)
            m = r["test_metrics"]
            rows.append({"Varijanta": vname, "Model": mname, "N_trening": r["n_train"], "N_test": r["n_test"],
                         "Accuracy": m["accuracy"], "Precision": m["precision"], "Recall": m["recall"],
                         "F1": m["f1"], "ROC_AUC": m["roc_auc"], "FPR": m["fpr"]})
            if verbose:
                print(f"[ABL] {vname:30s} {mname:26s} acc={m['accuracy']:.4f} rec={m['recall']:.4f} f1={m['f1']:.4f}")
    df = pd.DataFrame(rows)
    df.to_csv(config.RESULTS_METRICS / "ablation.csv", index=False)
    return df


if __name__ == "__main__":
    run_ablation()
