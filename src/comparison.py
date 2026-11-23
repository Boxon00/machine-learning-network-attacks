"""Eksperimentalno poredjenje: zavrsna tabela, intervali poverenja, McNemar, grafikoni."""
from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from . import config
from . import visualization as viz
from .evaluation import build_comparison_table, load_json, mcnemar_test, save_json, environment_info

MAIN_FILES = [
    ("Decision Tree", "decision_tree_binary"),
    ("Random Forest", "random_forest_binary"),
    ("Linear SVM (ceo trening)", "linear_svm_ceo_trening_binary"),
    ("SVM RBF (uzorak)", "svm_rbf_uzorak_binary"),
]
SUPPLEMENT = ("Linear SVM (uzorak)", "linear_svm_uzorak_binary")


def _load(slug):
    M = config.RESULTS_METRICS
    return load_json(M / f"{slug}.json"), np.load(M / f"{slug}_predictions.npz")


def run_comparison(verbose: bool = True) -> pd.DataFrame:
    config.ensure_directories()
    M = config.RESULTS_METRICS
    results, preds = [], {}
    for name, slug in MAIN_FILES + [SUPPLEMENT]:
        r, p = _load(slug)
        results.append(r)
        preds[name] = {"y_true": p["y_true"], "y_pred": p["y_pred"], "y_score": p["y_score"]}

    table = build_comparison_table(results)
    table.to_csv(M / "final_comparison.csv", index=False)
    (M / "final_comparison.md").write_text(table.round(4).to_markdown(index=False)
                                           if _has_tabulate() else table.round(4).to_string(index=False),
                                           encoding="utf-8")
    main_table = table[table["Model"].isin([n for n, _ in MAIN_FILES])].reset_index(drop=True)

    # intervali poverenja i metrike na treningu (preprilagodjavanje)
    ci_rows, fit_rows = [], []
    for r in results:
        ci = r["test_ci95"]
        ci_rows.append({"Model": r["model"], **{f"{k}_lo": v[0] for k, v in ci.items()},
                        **{f"{k}_hi": v[1] for k, v in ci.items()}})
        fit_rows.append({"Model": r["model"], "Accuracy_trening": r["train_metrics"]["accuracy"],
                         "F1_trening": r["train_metrics"]["f1"], "Accuracy_test": r["test_metrics"]["accuracy"],
                         "F1_test": r["test_metrics"]["f1"],
                         "Razlika_accuracy": r["train_metrics"]["accuracy"] - r["test_metrics"]["accuracy"]})
    pd.DataFrame(ci_rows).to_csv(M / "bootstrap_ci95.csv", index=False)
    pd.DataFrame(fit_rows).to_csv(M / "train_vs_test.csv", index=False)

    # McNemar za svaki par glavnih modela
    mc_rows = []
    names = [n for n, _ in MAIN_FILES]
    for a, b in itertools.combinations(names, 2):
        t = mcnemar_test(preds[a]["y_true"], preds[a]["y_pred"], preds[b]["y_pred"])
        mc_rows.append({"Model_A": a, "Model_B": b, **t})
    pd.DataFrame(mc_rows).to_csv(M / "mcnemar.csv", index=False)

    # detekcija po kategorijama
    det = []
    for r in results:
        for row in r["detection_by_category"]:
            det.append({"Model": r["model"], **row})
    det_df = pd.DataFrame(det)
    det_df.to_csv(M / "detection_by_category.csv", index=False)

    # grafikoni
    main_preds = {n: preds[n] for n in names}
    viz.plot_experiment_design()
    viz.plot_roc_curves(main_preds)
    viz.plot_pr_curves(main_preds)
    viz.plot_metric_comparison(main_table)
    viz.plot_time_comparison(main_table)
    viz.plot_detection_by_category(det_df[det_df["Model"].isin(names)])
    for r in results:
        m = r["test_metrics"]
        cm = np.array([[m["tn"], m["fp"]], [m["fn"], m["tp"]]])
        slug = r["model"].lower().replace(" ", "_").replace("(", "").replace(")", "")
        viz.plot_confusion_matrix(cm, r["model"], f"cm_{slug}.png")
    if (M / "dt_feature_importance_aggregated.csv").exists() and (M / "rf_feature_importance_aggregated.csv").exists():
        viz.plot_importance_panel(pd.read_csv(M / "dt_feature_importance_aggregated.csv"),
                                  pd.read_csv(M / "rf_feature_importance_aggregated.csv"))
    if (M / "scaling.csv").exists():
        viz.plot_scaling(pd.read_csv(M / "scaling.csv"))
    abl = M / "ablation.csv"
    if abl.exists():
        viz.plot_ablation(pd.read_csv(abl))
    save_json(environment_info(), M / "environment.json")
    if verbose:
        print(main_table.round(4).to_string(index=False))
    return table


def _has_tabulate() -> bool:
    try:
        import tabulate  # noqa: F401
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    run_comparison()
