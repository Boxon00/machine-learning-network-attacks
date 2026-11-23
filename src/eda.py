"""Istrazivacka analiza podataka (EDA) UNSW-NB15: tabele (CSV/JSON) i grafikoni.

Sve statistike se racunaju iz ucitanih datoteka; nista nije prepisano iz literature.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import skew

from . import config
from . import visualization as viz
from .data_loader import drop_duplicate_records, get_xy, load_feature_descriptions, load_train_test
from .evaluation import save_json


def dimensions_and_types(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    """Tabela kolona: tip, broj jedinstvenih vrednosti i nedostajuce vrednosti u oba skupa."""
    rows = []
    for c in train.columns:
        rows.append({"kolona": c, "tip": str(train[c].dtype), "jedinstvenih_trening": int(train[c].nunique()),
                     "jedinstvenih_test": int(test[c].nunique()),
                     "nedostajuce_trening": int(train[c].isna().sum()), "nedostajuce_test": int(test[c].isna().sum())})
    return pd.DataFrame(rows)


def duplicates_summary(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    nd = [c for c in train.columns if c != config.ID_COLUMN]
    return {
        "duplikati_svi_atributi_trening": int(train.duplicated().sum()),
        "duplikati_svi_atributi_test": int(test.duplicated().sum()),
        "duplikati_bez_id_trening": int(train.duplicated(subset=nd).sum()),
        "duplikati_bez_id_test": int(test.duplicated(subset=nd).sum()),
        "jedinstveni_bez_id_trening": int(len(train.drop_duplicates(subset=nd))),
        "jedinstveni_bez_id_test": int(len(test.drop_duplicates(subset=nd))),
        # sastav uklonjenih duplikata (zadrzava se prvo pojavljivanje)
        "udeo_napada_medju_duplikatima_trening": float(train[train.duplicated(subset=nd)]["label"].mean()),
        "udeo_napada_medju_duplikatima_test": float(test[test.duplicated(subset=nd)]["label"].mean()),
        "udeo_napada_posle_dedup_trening": float(train.drop_duplicates(subset=nd)["label"].mean()),
        "udeo_napada_posle_dedup_test": float(test.drop_duplicates(subset=nd)["label"].mean()),
    }


def overlap_summary(train: pd.DataFrame, test: pd.DataFrame) -> dict:
    """Koliko test zapisa ima identican vektor karakteristika u treningu i koliko je kontradiktornih grupa."""
    feats = [c for c in train.columns if c not in (config.ID_COLUMN, "attack_cat", "label")]
    m = test[feats].merge(train[feats].drop_duplicates(), on=feats, how="left", indicator=True)
    n_overlap = int((m["_merge"] == "both").sum())
    contradictory = int((train.groupby(feats)["label"].nunique() > 1).sum())
    return {"test_zapisa_identicnih_treningu": n_overlap, "test_ukupno": int(len(test)),
            "udeo_preklapanja": n_overlap / len(test), "kontradiktornih_grupa_u_treningu": contradictory}


def categorical_summary(train: pd.DataFrame, test: pd.DataFrame) -> pd.DataFrame:
    X_tr, _ = get_xy(train)
    X_te, _ = get_xy(test)
    cats = [c for c in X_tr.columns if c not in X_tr.select_dtypes("number").columns]
    rows = []
    for c in cats:
        s_tr, s_te = set(train[c]), set(test[c])
        rows.append({"kolona": c, "vrednosti_trening": len(s_tr), "vrednosti_test": len(s_te),
                     "samo_u_testu": ", ".join(sorted(s_te - s_tr)) or "-",
                     "samo_u_treningu": ", ".join(sorted(s_tr - s_te)) or "-"})
    return pd.DataFrame(rows)


def skewness_table(train: pd.DataFrame) -> pd.DataFrame:
    X, _ = get_xy(train)
    num = X.select_dtypes("number")
    return pd.DataFrame({"feature": num.columns, "skewness": [float(skew(num[c])) for c in num.columns],
                         "min": num.min().values, "max": num.max().values}).sort_values("skewness", ascending=False)


def run_eda(train: pd.DataFrame = None, test: pd.DataFrame = None, verbose: bool = True) -> dict:
    """Generise sve EDA tabele i grafikone u results/."""
    config.ensure_directories()
    if train is None or test is None:
        train, test = load_train_test()
    M = config.RESULTS_METRICS

    summary = {
        "trening_oblik": list(train.shape), "test_oblik": list(test.shape),
        "label_trening": {int(k): int(v) for k, v in train["label"].value_counts().items()},
        "label_test": {int(k): int(v) for k, v in test["label"].value_counts().items()},
        "udeo_napada_trening": float(train["label"].mean()), "udeo_napada_test": float(test["label"].mean()),
        "beskonacne_vrednosti": int(np.isinf(train.select_dtypes("number")).sum().sum()
                                    + np.isinf(test.select_dtypes("number")).sum().sum()),
        "duplikati": duplicates_summary(train, test), "preklapanje": overlap_summary(train, test),
        "broj_numerickih_ulaznih": int(get_xy(train)[0].select_dtypes("number").shape[1]),
        "broj_kategorijskih_ulaznih": int(len([c for c in get_xy(train)[0].columns
                                               if c not in get_xy(train)[0].select_dtypes("number").columns])),
        "konstantne_kolone": [c for c in train.columns if train[c].nunique() == 1],
    }
    save_json(summary, M / "eda_summary.json")
    dimensions_and_types(train, test).to_csv(M / "eda_columns.csv", index=False)
    pd.concat([train["attack_cat"].value_counts().rename("trening"),
               test["attack_cat"].value_counts().rename("test")], axis=1).to_csv(M / "eda_attack_cat_counts.csv")
    categorical_summary(train, test).to_csv(M / "eda_categorical.csv", index=False)
    sk = skewness_table(train)
    sk.to_csv(M / "eda_skewness.csv", index=False)
    X_tr, _ = get_xy(train)
    X_tr.select_dtypes("number").describe().T.to_csv(M / "eda_numeric_describe.csv")
    load_feature_descriptions().to_csv(M / "eda_feature_descriptions.csv", index=False)
    # korelacija sa label (numericke kolone)
    num = train.select_dtypes("number").drop(columns=["id"])
    num.corr()["label"].drop("label").sort_values(key=abs, ascending=False).to_csv(M / "eda_corr_with_label.csv")

    viz.plot_label_distribution(train, test)
    viz.plot_attack_distribution(train, test)
    for c in ("proto", "service", "state"):
        viz.plot_categorical_vs_label(train, c)
    viz.plot_correlation_heatmap(train)
    viz.plot_feature_distributions(train, ["dur", "sbytes", "dbytes", "sload", "rate", "sttl"])
    viz.plot_missing_and_skew(sk)
    if verbose:
        print("[EDA] gotovo:", {k: summary[k] for k in ("trening_oblik", "test_oblik", "duplikati", "preklapanje")})
    return summary


if __name__ == "__main__":
    run_eda()
