"""Centralna podesavanja projekta (putanje, seed, velicine uzoraka, broj jezgara).

Sve vrednosti koje uticu na reproduktivnost eksperimenta nalaze se na jednom mestu.
Promenljiva okruzenja ``SIR1_QUICK=1`` ukljucuje brzi rezim (mali uzorci) i sluzi
iskljucivo za proveru ispravnosti koda; rezultati iz brzog rezima NIKADA se ne koriste u radu.
"""
from __future__ import annotations

import os
from pathlib import Path

# ----------------------------------------------------------------------------- putanje
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
RESULTS_METRICS = PROJECT_ROOT / "results" / "metrics"
RESULTS_FIGURES = PROJECT_ROOT / "results" / "figures"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Brzi rezim koristi odvojene direktorijume da ne prepise prave rezultate.
QUICK = os.environ.get("SIR1_QUICK", "0") == "1"
if QUICK:
    RESULTS_METRICS = PROJECT_ROOT / "results_quick" / "metrics"
    RESULTS_FIGURES = PROJECT_ROOT / "results_quick" / "figures"

TRAIN_FILE = "UNSW_NB15_training-set.csv"
TEST_FILE = "UNSW_NB15_testing-set.csv"
FEATURES_FILE_CANDIDATES = ("UNSW-NB15_features.csv", "NUSW-NB15_features.csv")

# ----------------------------------------------------------------------------- kolone
ID_COLUMN = "id"                 # redni broj zapisa, nema informacionu vrednost
TARGET_BINARY = "label"          # 0 = normalan saobracaj, 1 = napad
TARGET_MULTICLASS = "attack_cat"  # kategorija napada (vise klasa)
# Kolone za ablacionu studiju (TCP sekvencni brojevi)
TCP_SEQ_COLUMNS = ("stcpb", "dtcpb")

# ----------------------------------------------------------------------------- reproduktivnost
RANDOM_STATE = 42
# Fitovanje modela koje se vremenski meri radi sa jednim jezgrom (poredivost vremena);
# pretraga hiperparametara moze koristiti sva jezgra.
N_JOBS_FIT = 1
N_JOBS_TUNING = -1
CV_FOLDS = 3
VALIDATION_FRACTION = 0.2

# ----------------------------------------------------------------------------- uzorci
TUNING_SAMPLE_SIZE = 50_000        # stratifikovani uzorak treninga za pretragu hiperparametara
SVM_RBF_TRAIN_SAMPLE = 20_000      # trening uzorak za RBF SVM (racunska zahtevnost)
SVM_RBF_TUNING_SAMPLE = 8_000      # uzorak (podskup prethodnog) za pretragu C/gamma
SKEW_THRESHOLD = 2.0               # prag asimetrije za log1p transformaciju

if QUICK:
    TUNING_SAMPLE_SIZE = 4_000
    SVM_RBF_TRAIN_SAMPLE = 3_000
    SVM_RBF_TUNING_SAMPLE = 1_500

BOOTSTRAP_ITERATIONS = 1000 if not QUICK else 100


def ensure_directories() -> None:
    """Kreira izlazne direktorijume ako ne postoje."""
    for d in (DATA_PROCESSED, RESULTS_METRICS, RESULTS_FIGURES, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)
