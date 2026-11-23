"""Ucitavanje UNSW-NB15 trening/test skupa, provera seme i izdvajanje ulaza/cilja.

Koristi se ZVANICNA podela (UNSW_NB15_training-set.csv i UNSW_NB15_testing-set.csv).
Ova datoteka je jedino mesto na kojem se bira ciljna promenljiva, cime se
sprecava slucajno ukljucivanje ``label`` / ``attack_cat`` u ulazne karakteristike.
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from . import config


class DatasetNotFoundError(FileNotFoundError):
    """Podizemo kada ocekivani CSV fajl ne postoji u data/raw/."""


def _read_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise DatasetNotFoundError(
            f"Datoteka nije pronadjena: {path}\n"
            "Preuzmite UNSW-NB15 sa https://research.unsw.edu.au/projects/unsw-nb15-dataset "
            f"i postavite '{config.TRAIN_FILE}' i '{config.TEST_FILE}' u {config.DATA_RAW}."
        )
    try:
        return pd.read_csv(path)
    except Exception as exc:  # pragma: no cover - zaštita od oštecenog fajla
        raise RuntimeError(f"Neuspesno citanje {path}: {exc}") from exc


def load_train_test() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Ucitava zvanicni trening i test skup i proverava da su seme identicne.

    Returns:
        (train_df, test_df) - sirovi DataFrame-ovi, bez ikakve transformacije.
    """
    train = _read_csv(config.DATA_RAW / config.TRAIN_FILE)
    test = _read_csv(config.DATA_RAW / config.TEST_FILE)
    validate_schema(train, test)
    if config.QUICK:  # samo provera koda
        train = train.sample(n=min(len(train), 12_000), random_state=config.RANDOM_STATE)
        test = test.sample(n=min(len(test), 6_000), random_state=config.RANDOM_STATE)
        train, test = train.reset_index(drop=True), test.reset_index(drop=True)
    return train, test


def validate_schema(train: pd.DataFrame, test: pd.DataFrame) -> None:
    """Proverava da trening i test imaju iste kolone i da sadrze ciljne kolone."""
    if list(train.columns) != list(test.columns):
        raise ValueError("Trening i test skup nemaju identicne kolone.")
    for col in (config.TARGET_BINARY, config.TARGET_MULTICLASS, config.ID_COLUMN):
        if col not in train.columns:
            raise ValueError(f"Nedostaje ocekivana kolona '{col}'.")
    if set(train[config.TARGET_BINARY].unique()) - {0, 1}:
        raise ValueError("Kolona 'label' mora sadrzati samo vrednosti 0 i 1.")


def get_xy(
    df: pd.DataFrame,
    task: str = "binary",
    drop_columns: Iterable[str] = (),
) -> Tuple[pd.DataFrame, pd.Series]:
    """Razdvaja ulazne karakteristike X i ciljnu promenljivu y.

    ``id`` se uvek uklanja. Za ``task='binary'`` cilj je ``label`` a ``attack_cat``
    se odbacuje; za ``task='multiclass'`` cilj je ``attack_cat`` a ``label`` se
    odbacuje. Time ciljna promenljiva (niti njen derivat) nikada ne ulazi u X.

    Args:
        df: DataFrame sa svim kolonama.
        task: ``'binary'`` ili ``'multiclass'``.
        drop_columns: dodatne kolone za uklanjanje (npr. za ablacionu studiju).
    """
    if task == "binary":
        target = config.TARGET_BINARY
    elif task == "multiclass":
        target = config.TARGET_MULTICLASS
    else:
        raise ValueError("task mora biti 'binary' ili 'multiclass'.")
    to_drop = {config.ID_COLUMN, config.TARGET_BINARY, config.TARGET_MULTICLASS, *drop_columns}
    X = df.drop(columns=[c for c in to_drop if c in df.columns])
    y = df[target].copy()
    assert target not in X.columns
    return X, y


def stratified_subsample(
    X: pd.DataFrame, y: pd.Series, n: int, random_state: int = config.RANDOM_STATE
) -> Tuple[pd.DataFrame, pd.Series]:
    """Stratifikovani uzorak velicine ``n`` (cuva proporcije klasa)."""
    if n >= len(X):
        return X, y
    X_s, _, y_s, _ = train_test_split(
        X, y, train_size=n, stratify=y, random_state=random_state
    )
    return X_s, y_s


def drop_duplicate_records(df: pd.DataFrame) -> pd.DataFrame:
    """Uklanja zapise koji su identicni u svim kolonama osim ``id``."""
    cols = [c for c in df.columns if c != config.ID_COLUMN]
    return df.drop_duplicates(subset=cols).reset_index(drop=True)


def load_feature_descriptions() -> pd.DataFrame:
    """Ucitava zvanicni opis karakteristika (datoteka nije u UTF-8 kodiranju)."""
    for name in config.FEATURES_FILE_CANDIDATES:
        path = config.DATA_RAW / name
        if path.exists():
            df = pd.read_csv(path, encoding="latin-1")
            df.columns = [c.strip() for c in df.columns]
            return df
    raise DatasetNotFoundError("Datoteka sa opisom karakteristika nije pronadjena.")
