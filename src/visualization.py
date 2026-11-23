"""Grafikoni za EDA i eksperimentalne rezultate (cuvaju se u results/figures/)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Sequence

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import precision_recall_curve, roc_curve

from . import config

sns.set_theme(style="whitegrid", context="notebook")
PALETTE = {"Normalan saobraćaj": "#2a9d8f", "Napad": "#e76f51"}
MODEL_COLORS = ["#264653", "#2a9d8f", "#e9c46a", "#e76f51", "#8d99ae"]
DPI = 150


def _save(fig, name: str) -> Path:
    config.RESULTS_FIGURES.mkdir(parents=True, exist_ok=True)
    path = config.RESULTS_FIGURES / name
    fig.tight_layout()
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    return path


# ------------------------------------------------------------------------- EDA
def plot_label_distribution(train: pd.DataFrame, test: pd.DataFrame, name="eda_label_distribution.png"):
    rows = []
    for split, df in (("Trening", train), ("Test", test)):
        vc = df["label"].value_counts().sort_index()
        for lab, n in vc.items():
            rows.append({"Skup": split, "Klasa": "Normalan saobraćaj" if lab == 0 else "Napad", "Broj zapisa": n})
    d = pd.DataFrame(rows)
    fig, ax = plt.subplots(figsize=(6.5, 4))
    sns.barplot(data=d, x="Skup", y="Broj zapisa", hue="Klasa", palette=PALETTE, ax=ax)
    for c in ax.containers:
        ax.bar_label(c, fmt="{:,.0f}", padding=2, fontsize=9)
    ax.set_title("Raspodela klasa (label) u trening i test skupu")
    return _save(fig, name)


def plot_attack_distribution(train: pd.DataFrame, test: pd.DataFrame, name="eda_attack_cat_distribution.png"):
    d = pd.concat([train["attack_cat"].value_counts().rename("Trening"),
                   test["attack_cat"].value_counts().rename("Test")], axis=1).fillna(0)
    d = d.sort_values("Trening", ascending=True)
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    d.plot.barh(ax=ax, color=["#264653", "#e9c46a"], width=0.8)
    ax.set_xscale("log")
    ax.set_xlabel("Broj zapisa (logaritamska skala)")
    ax.set_ylabel("")
    ax.set_title("Zastupljenost kategorija saobraćaja (attack_cat)")
    return _save(fig, name)


def plot_categorical_vs_label(df: pd.DataFrame, col: str, top: int = 10, name=None):
    top_vals = df[col].value_counts().head(top).index
    d = df[df[col].isin(top_vals)].copy()
    d["Klasa"] = d["label"].map({0: "Normalan saobraćaj", 1: "Napad"})
    order = d[col].value_counts().index
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    sns.countplot(data=d, x=col, hue="Klasa", order=order, palette=PALETTE, ax=ax)
    ax.set_yscale("log"); ax.set_ylabel("Broj zapisa (log)")
    ax.set_title(f"Raspodela kolone '{col}' po klasama (trening, top {top})")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    return _save(fig, name or f"eda_{col}_vs_label.png")


def plot_correlation_heatmap(df: pd.DataFrame, top_n: int = 18, name="eda_correlation_heatmap.png"):
    num = df.select_dtypes(include="number").drop(columns=["id"], errors="ignore")
    corr_label = num.corr()["label"].drop("label").abs().sort_values(ascending=False)
    cols = corr_label.head(top_n).index.tolist()
    corr = num[cols + ["label"]].corr()
    fig, ax = plt.subplots(figsize=(9, 7.5))
    sns.heatmap(corr, cmap="vlag", center=0, annot=True, fmt=".2f", annot_kws={"size": 6.5},
                linewidths=0.3, cbar_kws={"shrink": 0.8}, ax=ax)
    ax.set_title(f"Pearsonova korelacija: {top_n} karakteristika najjače povezanih sa 'label'")
    return _save(fig, name)


def plot_feature_distributions(df: pd.DataFrame, cols: Sequence[str], name="eda_feature_distributions.png"):
    n = len(cols)
    ncols = 3
    nrows = int(np.ceil(n / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(11, 3.1 * nrows))
    for ax, c in zip(np.ravel(axes), cols):
        for lab, color in ((0, PALETTE["Normalan saobraćaj"]), (1, PALETTE["Napad"])):
            v = np.log1p(df.loc[df["label"] == lab, c].clip(lower=0))
            sns.histplot(v, bins=40, stat="density", element="step", fill=True, alpha=0.35,
                         color=color, ax=ax, label="Normalan" if lab == 0 else "Napad")
        ax.set_title(f"log(1+{c})"); ax.set_xlabel("")
    for ax in np.ravel(axes)[n:]:
        ax.axis("off")
    np.ravel(axes)[0].legend()
    fig.suptitle("Raspodele odabranih numeričkih karakteristika po klasama (trening)", y=1.0)
    return _save(fig, name)


def plot_missing_and_skew(skew_df: pd.DataFrame, name="eda_skewness.png"):
    d = skew_df.sort_values("skewness", ascending=False).head(15).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(d["feature"], d["skewness"], color="#264653")
    ax.set_xlabel("Skewness (trening)"); ax.set_title("Najasimetričnije numeričke karakteristike")
    return _save(fig, name)


# ------------------------------------------------------------------------- rezultati
def plot_confusion_matrix(cm: np.ndarray, title: str, name: str):
    cm = np.asarray(cm)
    pct = cm / cm.sum(axis=1, keepdims=True)
    annot = np.array([[f"{cm[i, j]:,}\n({pct[i, j]*100:.1f}%)" for j in range(2)] for i in range(2)])
    fig, ax = plt.subplots(figsize=(4.6, 4))
    sns.heatmap(pct, annot=annot, fmt="", cmap="Blues", cbar=False, vmin=0, vmax=1,
                xticklabels=["Normalan (0)", "Napad (1)"], yticklabels=["Normalan (0)", "Napad (1)"], ax=ax)
    ax.set_xlabel("Predikcija"); ax.set_ylabel("Stvarna klasa"); ax.set_title(title, fontsize=10)
    return _save(fig, name)


def plot_roc_curves(preds: Dict[str, dict], name="roc_curves.png"):
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    for (label, d), color in zip(preds.items(), MODEL_COLORS):
        fpr, tpr, _ = roc_curve(d["y_true"], d["y_score"])
        auc = np.trapezoid(tpr, fpr) if hasattr(np, "trapezoid") else np.trapz(tpr, fpr)
        ax.plot(fpr, tpr, color=color, lw=2, label=f"{label} (AUC={auc:.4f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Slučajan klasifikator")
    ax.set_xlabel("Stopa lažnih alarma (FPR)"); ax.set_ylabel("Stopa detekcije (TPR / Recall)")
    ax.set_title("ROC krive na test skupu"); ax.legend(loc="lower right", fontsize=8)
    return _save(fig, name)


def plot_pr_curves(preds: Dict[str, dict], name="pr_curves.png"):
    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    for (label, d), color in zip(preds.items(), MODEL_COLORS):
        p, r, _ = precision_recall_curve(d["y_true"], d["y_score"])
        ax.plot(r, p, color=color, lw=2, label=label)
    ax.set_xlabel("Recall"); ax.set_ylabel("Precision"); ax.set_title("Precision–Recall krive na test skupu")
    ax.legend(loc="lower left", fontsize=8)
    return _save(fig, name)


def plot_metric_comparison(table: pd.DataFrame, name="metrics_comparison.png"):
    metrics = ["Accuracy", "Precision", "Recall", "F1"]
    d = table.melt(id_vars="Model", value_vars=metrics, var_name="Metrika", value_name="Vrednost")
    fig, ax = plt.subplots(figsize=(9, 4.6))
    sns.barplot(data=d, x="Metrika", y="Vrednost", hue="Model", palette=MODEL_COLORS[:table.shape[0]], ax=ax)
    lo = max(0.0, d["Vrednost"].min() - 0.05)
    ax.set_ylim(lo, 1.07)
    for c in ax.containers:
        ax.bar_label(c, fmt="%.3f", padding=2, fontsize=7, rotation=90)
    ax.set_title("Poređenje metrika na test skupu")
    ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, frameon=False)
    return _save(fig, name)


def plot_time_comparison(table: pd.DataFrame, name="time_comparison.png"):
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    for ax, col, ttl in zip(axes, ["Vreme_treniranja_s", "Vreme_predikcije_s"],
                            ["Vreme treniranja (s)", "Vreme predikcije na test skupu (s)"]):
        sns.barplot(data=table, x="Model", y=col, hue="Model", palette=MODEL_COLORS[:len(table)],
                    legend=False, ax=ax)
        ax.set_yscale("log"); ax.set_title(ttl); ax.set_xlabel("")
        for c in ax.containers:
            ax.bar_label(c, fmt="%.2f", padding=2, fontsize=8)
        plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
    return _save(fig, name)


def plot_feature_importance(df: pd.DataFrame, title: str, name: str, top_n: int = 15, col="importance",
                            label_col="origin", color="#264653"):
    d = df.head(top_n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(d[label_col], d[col], color=color)
    ax.set_xlabel("Značaj karakteristike (Gini)"); ax.set_title(title)
    return _save(fig, name)


def plot_depth_curve(df: pd.DataFrame, name="dt_depth_curve.png"):
    fig, ax = plt.subplots(figsize=(7, 4.4))
    x = df["depth_label"]
    ax.plot(x, df["train_f1"], "o-", color="#264653", label="Trening (F1)")
    ax.plot(x, df["val_f1"], "s-", color="#e76f51", label="Validacija (F1)")
    ax.set_xlabel("max_depth"); ax.set_ylabel("F1-score"); ax.legend()
    ax.set_title("Decision Tree: uticaj dubine stabla (kontrola preprilagođavanja)")
    return _save(fig, name)


def plot_trees_curve(df: pd.DataFrame, name="rf_trees_curve.png"):
    fig, ax1 = plt.subplots(figsize=(7, 4.4))
    ax1.plot(df["n_estimators"], df["val_f1"], "o-", color="#2a9d8f", label="Validacija F1")
    ax1.set_xlabel("Broj stabala (n_estimators)"); ax1.set_ylabel("F1-score (validacija)")
    ax2 = ax1.twinx()
    ax2.plot(df["n_estimators"], df["fit_time_s"], "s--", color="#e76f51", label="Vreme treniranja (s)")
    ax2.set_ylabel("Vreme treniranja (s)"); ax2.grid(False)
    h1, l1 = ax1.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, loc="center right", fontsize=8)
    ax1.set_title("Random Forest: uticaj broja stabala")
    return _save(fig, name)


def plot_param_heatmap(df: pd.DataFrame, x: str, y: str, value: str, title: str, name: str):
    pv = df.pivot_table(index=y, columns=x, values=value)
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(pv, annot=True, fmt=".4f", cmap="viridis", ax=ax)
    ax.set_title(title)
    return _save(fig, name)


def plot_detection_by_category(df: pd.DataFrame, name="detection_by_category.png"):
    pv = df.pivot(index="attack_cat", columns="Model", values="detection_rate")
    order = df.drop_duplicates("attack_cat").sort_values("n", ascending=False)["attack_cat"]
    pv = pv.loc[order]
    fig, ax = plt.subplots(figsize=(8, 5.2))
    sns.heatmap(pv, annot=True, fmt=".3f", cmap="YlGnBu", vmin=0, vmax=1, ax=ax)
    ax.set_ylabel(""); ax.set_xlabel("")
    ax.set_title("Udeo ispravno klasifikovanih zapisa po kategoriji (test)\n(Normal = specifičnost; ostalo = Recall)")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right", fontsize=8)
    return _save(fig, name)


def plot_ablation(df: pd.DataFrame, name="ablation.png"):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), sharey=False)
    for ax, metric in zip(axes, ["F1", "Recall"]):
        sns.barplot(data=df, x="Model", y=metric, hue="Varijanta", ax=ax, palette="Set2")
        ax.set_ylim(max(0, df[metric].min() - 0.03), 1.0); ax.set_title(f"Ablaciona studija: {metric}")
        ax.set_xlabel(""); plt.setp(ax.get_xticklabels(), rotation=15, ha="right", fontsize=8)
        ax.legend(fontsize=7)
    return _save(fig, name)


def plot_experiment_design(name="experiment_design.png"):
    """Dijagram toka eksperimenta (koristi se u seminarskom radu)."""
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
    fig, ax = plt.subplots(figsize=(11, 4.6)); ax.axis("off"); ax.set_xlim(0, 11); ax.set_ylim(0, 4.6)

    def box(x, y, w, h, t, c="#dbe7f3", ec="#264653", fs=8.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.08", fc=c, ec=ec, lw=1.2))
        ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs)

    def arr(x1, y1, x2, y2):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, color="#264653", lw=1.2))
    box(0.1, 3.3, 2.2, 1.0, "UNSW_NB15_\ntraining-set.csv\n(175.341)", "#e9f5db")
    box(0.1, 0.4, 2.2, 1.0, "UNSW_NB15_\ntesting-set.csv\n(82.332)", "#fde2e4")
    box(3.0, 3.3, 2.4, 1.0, "get_xy: uklanja id,\nlabel, attack_cat\nfit preprocesora\n(samo trening)")
    box(3.0, 1.9, 2.4, 1.0, "Podešavanje\nhiperparametara\n(3-fold CV, uzorak 50k)")
    box(6.1, 2.6, 2.3, 1.5, "Finalno treniranje\nna celom treningu\nDT | RF | Linear SVM\nSVM RBF (uzorak 20k)", "#fff3b0")
    box(3.0, 0.4, 2.4, 1.0, "transform preprocesora\n(bez ponovnog fit-a)", "#fde2e4")
    box(8.9, 1.4, 2.0, 1.8, "Evaluacija na\ntest skupu:\nAcc, Prec, Rec, F1,\nAUC, vreme", "#cdeac0")
    arr(2.3, 3.8, 3.0, 3.8); arr(4.2, 3.3, 4.2, 2.9); arr(5.4, 2.4, 6.1, 3.0); arr(5.4, 3.8, 6.1, 3.5)
    arr(2.3, 0.9, 3.0, 0.9); arr(5.4, 0.9, 8.9, 1.8); arr(8.4, 3.3, 8.9, 2.8)
    ax.text(5.5, 4.45, "Test skup se koristi isključivo za završnu evaluaciju", ha="center", fontsize=9, style="italic")
    return _save(fig, name)


def plot_scaling(df: pd.DataFrame, name="scaling.png"):
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    for (m, g), c in zip(df.groupby("Model", sort=False), MODEL_COLORS):
        ax.plot(g["N_trening"], g["Vreme_treniranja_s"], "o-", color=c, label=m)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Broj trening uzoraka"); ax.set_ylabel("Vreme treniranja (s)")
    ax.set_title("Skaliranje vremena treniranja sa veličinom trening skupa"); ax.legend()
    return _save(fig, name)


def plot_importance_panel(dt_agg: pd.DataFrame, rf_agg: pd.DataFrame, top_n: int = 10, name="importances.png"):
    """Znacaj karakteristika (agregirano po originalnoj koloni): Decision Tree i Random Forest jedan pored drugog."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    for ax, df, ttl, col in ((axes[0], dt_agg, "(a) Decision Tree", "#264653"), (axes[1], rf_agg, "(b) Random Forest", "#2a9d8f")):
        d = df.head(top_n).iloc[::-1]
        ax.barh(d["origin"], d["importance"], color=col)
        ax.set_title(ttl, loc="left", fontsize=12, fontweight="bold"); ax.set_xlabel("Značaj karakteristike (Gini)")
        ax.tick_params(axis="y", labelsize=10)
    return _save(fig, name)
