"""Preprocesiranje UNSW-NB15 bez curenja podataka (Data Leakage).

Sve transformacije su sastavni deo ``sklearn.Pipeline`` objekta i uce se (``fit``)
ISKLJUCIVO na trening podacima; test podaci prolaze samo kroz ``transform``.
Tokom unakrsne validacije preprocesiranje se ponovo uci u svakom foldu.

Koraci:
  * numericke kolone: imputacija medijanom -> log1p na jako asimetricnim
    nenegativnim kolonama -> StandardScaler;
  * kategorijske kolone (proto, service, state): OneHotEncoder sa
    ``handle_unknown='ignore'`` (test sadrzi vrednosti ``state`` koje trening nema).
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from scipy.stats import skew
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.utils.validation import check_is_fitted

from . import config


def clean_infinite(X: pd.DataFrame) -> pd.DataFrame:
    """Zamenjuje +/-inf sa NaN (u UNSW-NB15 ih nema, ali je korak zastitni).

    NaN vrednosti se zatim popunjavaju medijanom unutar pipeline-a (fit samo na treningu).
    """
    return X.replace([np.inf, -np.inf], np.nan)


class SkewedLog1p(BaseEstimator, TransformerMixin):
    """Primenjuje log(1+x) na nenegativne kolone ciji je skewness na TRENINGU veci od praga.

    Skup kolona se odredjuje u ``fit`` (samo na trening podacima). Monotona
    transformacija ne menja stabla odlucivanja, ali je kljucna za SVM zbog
    ekstremnih vrednosti (npr. ``sload`` do ~6e9).
    Vrednosti ispod nule (ne postoje u podacima) se pre transformacije
    ogranicavaju na 0 radi numericke stabilnosti.
    """

    def __init__(self, skew_threshold: float = config.SKEW_THRESHOLD):
        self.skew_threshold = skew_threshold

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        mins = np.nanmin(X, axis=0)
        with np.errstate(all="ignore"):
            sk = skew(X, axis=0, nan_policy="omit")
        sk = np.nan_to_num(np.asarray(sk, dtype=float), nan=0.0)
        self.columns_ = np.where((mins >= 0) & (sk > self.skew_threshold))[0]
        self.n_features_in_ = X.shape[1]
        return self

    def transform(self, X):
        check_is_fitted(self, "columns_")
        X = np.array(X, dtype=float, copy=True)
        X[:, self.columns_] = np.log1p(np.clip(X[:, self.columns_], 0, None))
        return X

    def get_feature_names_out(self, input_features=None):
        return np.asarray(input_features, dtype=object)


def split_column_types(X: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """Vraca (numericke_kolone, kategorijske_kolone)."""
    numeric = X.select_dtypes(include="number").columns.tolist()
    categorical = [c for c in X.columns if c not in numeric]
    return numeric, categorical


def build_preprocessor(X_train: pd.DataFrame) -> ColumnTransformer:
    """Gradi (jos nefitovan) ColumnTransformer na osnovu tipova kolona iz X_train."""
    numeric, categorical = split_column_types(X_train)
    num_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("log", SkewedLog1p()),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipe = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    return ColumnTransformer(
        [("num", num_pipe, numeric), ("cat", cat_pipe, categorical)],
        remainder="drop",
        sparse_threshold=0.0,
        verbose_feature_names_out=False,
    )


def get_feature_names(preprocessor: ColumnTransformer) -> List[str]:
    """Imena izlaznih karakteristika fitovanog preprocesora."""
    check_is_fitted(preprocessor)
    return list(preprocessor.get_feature_names_out())


def get_feature_origins(preprocessor: ColumnTransformer) -> List[str]:
    """Za svaku izlaznu karakteristiku vraca naziv originalne kolone (za agregaciju znacaja)."""
    check_is_fitted(preprocessor)
    origins: List[str] = []
    for name, trans, cols in preprocessor.transformers_:
        if name == "num":
            origins.extend(list(cols))
        elif name == "cat":
            for col, cats in zip(cols, trans.categories_):
                origins.extend([col] * len(cats))
    return origins


def log_transformed_columns(preprocessor: ColumnTransformer) -> List[str]:
    """Nazivi numerickih kolona na koje je primenjena log1p (odredjeno na treningu)."""
    check_is_fitted(preprocessor)
    for name, trans, cols in preprocessor.transformers_:
        if name == "num":
            idx = trans.named_steps["log"].columns_
            return [list(cols)[i] for i in idx]
    return []


def make_pipeline(X_train: pd.DataFrame, estimator) -> Pipeline:
    """Pipeline = preprocesiranje (fit samo na treningu) + klasifikator."""
    return Pipeline([("prep", build_preprocessor(X_train)), ("clf", estimator)])
