"""Evaluacione metrike, merenje vremena, bootstrap intervali i uporedna tabela."""
from __future__ import annotations

import json
import platform
import time
from pathlib import Path
from typing import Callable, Dict, Iterable, Tuple

import numpy as np
import pandas as pd
import sklearn
from scipy.stats import chi2
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score, confusion_matrix,
    f1_score, matthews_corrcoef, precision_score, recall_score, roc_auc_score,
)

from . import config


def timed(fn: Callable, *args, **kwargs) -> Tuple[object, float]:
    """Izvrsava ``fn`` i vraca (rezultat, trajanje u sekundama)."""
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, time.perf_counter() - t0


def compute_binary_metrics(y_true, y_pred, y_score=None) -> Dict[str, float]:
    """Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC i elementi matrice konfuzije.

    Pozitivna klasa (1) = mrezni napad. ``fpr`` = FP/(FP+TN) (stopa laznih alarma).
    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    m = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1": f1_score(y_true, y_pred, zero_division=0),
        "balanced_accuracy": balanced_accuracy_score(y_true, y_pred),
        "mcc": matthews_corrcoef(y_true, y_pred),
        "specificity": tn / (tn + fp) if (tn + fp) else float("nan"),
        "fpr": fp / (fp + tn) if (fp + tn) else float("nan"),
        "fnr": fn / (fn + tp) if (fn + tp) else float("nan"),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
    }
    if y_score is not None:
        m["roc_auc"] = roc_auc_score(y_true, y_score)
        m["pr_auc"] = average_precision_score(y_true, y_score)
    return {k: (float(v) if not isinstance(v, int) else v) for k, v in m.items()}


def compute_multiclass_metrics(y_true, y_pred) -> Dict[str, float]:
    """Pripremljeno za buduci multi-class eksperiment (nije deo binarnog eksperimenta)."""
    return {
        "accuracy": accuracy_score(y_true, y_pred),
        "macro_precision": precision_score(y_true, y_pred, average="macro", zero_division=0),
        "macro_recall": recall_score(y_true, y_pred, average="macro", zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "weighted_f1": f1_score(y_true, y_pred, average="weighted", zero_division=0),
    }


def bootstrap_ci(y_true, y_pred, n_boot: int = config.BOOTSTRAP_ITERATIONS,
                 seed: int = config.RANDOM_STATE) -> Dict[str, Tuple[float, float]]:
    """95% percentilni bootstrap intervali za Accuracy, Precision, Recall i F1 na test skupu."""
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true); y_pred = np.asarray(y_pred)
    n = len(y_true)
    acc, pre, rec, f1 = [], [], [], []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        t, p = y_true[idx], y_pred[idx]
        tp = np.sum((t == 1) & (p == 1)); fp = np.sum((t == 0) & (p == 1))
        fn = np.sum((t == 1) & (p == 0)); tn = np.sum((t == 0) & (p == 0))
        acc.append((tp + tn) / n)
        pr = tp / (tp + fp) if tp + fp else 0.0
        rc = tp / (tp + fn) if tp + fn else 0.0
        pre.append(pr); rec.append(rc)
        f1.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    q = lambda a: (float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5)))
    return {"accuracy": q(acc), "precision": q(pre), "recall": q(rec), "f1": q(f1)}


def mcnemar_test(y_true, pred_a, pred_b) -> Dict[str, float]:
    """McNemar test (sa korekcijom kontinuiteta) za poredjenje dva klasifikatora na istom test skupu."""
    y_true = np.asarray(y_true)
    a_ok = np.asarray(pred_a) == y_true
    b_ok = np.asarray(pred_b) == y_true
    n01 = int(np.sum(a_ok & ~b_ok))   # A tacan, B pogresan
    n10 = int(np.sum(~a_ok & b_ok))   # A pogresan, B tacan
    if n01 + n10 == 0:
        return {"n_a_only": n01, "n_b_only": n10, "chi2": 0.0, "p_value": 1.0}
    stat = (abs(n01 - n10) - 1) ** 2 / (n01 + n10)
    return {"n_a_only": n01, "n_b_only": n10, "chi2": float(stat),
            "p_value": float(chi2.sf(stat, df=1))}


def recall_by_attack_category(attack_cat: Iterable[str], y_pred) -> pd.DataFrame:
    """Udeo ispravno detektovanih zapisa po kategoriji napada (Recall po kategoriji).

    Za kategoriju ``Normal`` vraca specificnost (udeo ispravno prepoznatog normalnog saobracaja).
    """
    df = pd.DataFrame({"attack_cat": list(attack_cat), "pred": np.asarray(y_pred)})
    rows = []
    for cat, g in df.groupby("attack_cat"):
        ok = (g["pred"] == 0).mean() if cat == "Normal" else (g["pred"] == 1).mean()
        rows.append({"attack_cat": cat, "n": len(g), "detection_rate": float(ok)})
    return pd.DataFrame(rows).sort_values("n", ascending=False).reset_index(drop=True)


def save_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False, default=_json_default)


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


def environment_info() -> Dict[str, str]:
    """Verzije softvera i hardver - zapis radi reproduktivnosti."""
    import os
    import scipy
    return {
        "python": platform.python_version(), "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "scikit-learn": sklearn.__version__, "scipy": scipy.__version__,
        "cpu_count": str(os.cpu_count()), "random_state": str(config.RANDOM_STATE),
        "quick_mode": str(config.QUICK),
    }


def build_comparison_table(results: Iterable[dict]) -> pd.DataFrame:
    """Zavrsna tabela: po jedan red za svaki model (test metrike + vremena)."""
    rows = []
    for r in results:
        m = r["test_metrics"]
        rows.append({
            "Model": r["model"], "N_trening": r["n_train"],
            "Accuracy": m["accuracy"], "Precision": m["precision"], "Recall": m["recall"],
            "F1": m["f1"], "ROC_AUC": m.get("roc_auc"), "PR_AUC": m.get("pr_auc"),
            "FPR": m["fpr"], "FNR": m["fnr"], "MCC": m["mcc"],
            "Vreme_treniranja_s": r["fit_time_s"], "Vreme_predikcije_s": r["predict_time_s"],
        })
    return pd.DataFrame(rows)
