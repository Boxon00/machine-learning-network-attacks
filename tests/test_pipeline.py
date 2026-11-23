"""Automatski testovi ispravnosti. Pokretanje iz korena projekta:  python -m unittest discover -s tests -v

Testovi proveravaju: sprecavanje curenja podataka, tacnost metrika, zvanicne dimenzije dataseta,
reproduktivnost i doslednost sacuvanih rezultata sa sacuvanim predikcijama.
"""
import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import config
from src.data_loader import get_xy, load_train_test, stratified_subsample
from src.evaluation import compute_binary_metrics
from src.preprocessing import SkewedLog1p, build_preprocessor, make_pipeline
from sklearn.tree import DecisionTreeClassifier

HAVE_DATA = (config.DATA_RAW / config.TRAIN_FILE).exists() and (config.DATA_RAW / config.TEST_FILE).exists()


@unittest.skipUnless(HAVE_DATA, "dataset nije u data/raw/")
class TestData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train, cls.test = load_train_test()

    def test_official_dimensions(self):
        self.assertEqual(self.train.shape, (175341, 45))
        self.assertEqual(self.test.shape, (82332, 45))

    def test_official_label_counts(self):
        self.assertEqual(self.train.label.value_counts().to_dict(), {1: 119341, 0: 56000})
        self.assertEqual(self.test.label.value_counts().to_dict(), {1: 45332, 0: 37000})

    def test_no_missing_or_inf(self):
        for df in (self.train, self.test):
            self.assertEqual(int(df.isna().sum().sum()), 0)
            self.assertEqual(int(np.isinf(df.select_dtypes("number")).sum().sum()), 0)

    def test_targets_never_in_features(self):
        for task in ("binary", "multiclass"):
            X, y = get_xy(self.train, task)
            for c in ("id", "label", "attack_cat"):
                self.assertNotIn(c, X.columns)
            self.assertEqual(X.shape[1], 42)
            self.assertEqual(len(X), len(y))

    def test_binary_target_is_label(self):
        _, y = get_xy(self.train, "binary")
        self.assertTrue((y.values == self.train["label"].values).all())

    def test_test_contains_unseen_state_values(self):
        unseen = set(self.test["state"]) - set(self.train["state"])
        self.assertTrue({"ACC", "CLO"} <= unseen)

    def test_unseen_category_handled_without_error(self):
        X_tr, y_tr = get_xy(self.train, "binary")
        X_te, _ = get_xy(self.test, "binary")
        Xs, ys = stratified_subsample(X_tr, y_tr, 3000)
        prep = build_preprocessor(Xs).fit(Xs)
        out = prep.transform(X_te.iloc[:2000])
        self.assertEqual(out.shape[1], prep.transform(Xs.iloc[:5]).shape[1])  # isti broj kolona
        names = list(prep.get_feature_names_out())
        state_cols = [i for i, n in enumerate(names) if n.startswith("state_")]
        mask = X_te.iloc[:2000]["state"].isin(["ACC", "CLO"]).values
        if mask.any():
            self.assertTrue((out[mask][:, state_cols] == 0).all())  # nepoznata stanja -> sve nule

    def test_preprocessor_fit_uses_only_train(self):
        X_tr, y_tr = get_xy(self.train, "binary")
        X_te, _ = get_xy(self.test, "binary")
        Xs, _ = stratified_subsample(X_tr, y_tr, 3000)
        prep = build_preprocessor(Xs).fit(Xs)
        mean_before = prep.named_transformers_["num"].named_steps["scaler"].mean_.copy()
        cols_before = prep.named_transformers_["num"].named_steps["log"].columns_.copy()
        prep.transform(X_te.iloc[:5000])  # transform ne sme menjati naucene parametre
        np.testing.assert_array_equal(mean_before, prep.named_transformers_["num"].named_steps["scaler"].mean_)
        np.testing.assert_array_equal(cols_before, prep.named_transformers_["num"].named_steps["log"].columns_)

    def test_reproducible_predictions(self):
        X_tr, y_tr = get_xy(self.train, "binary")
        X_te, _ = get_xy(self.test, "binary")
        Xs, ys = stratified_subsample(X_tr, y_tr, 4000)
        p1 = make_pipeline(Xs, DecisionTreeClassifier(max_depth=8, random_state=42)).fit(Xs, ys).predict(X_te.iloc[:3000])
        p2 = make_pipeline(Xs, DecisionTreeClassifier(max_depth=8, random_state=42)).fit(Xs, ys).predict(X_te.iloc[:3000])
        np.testing.assert_array_equal(p1, p2)

    def test_pipeline_does_not_depend_on_test_labels(self):
        """Predikcije zavise samo od trening podataka i test ULAZA, nikada od test oznaka."""
        X_tr, y_tr = get_xy(self.train, "binary")
        X_te, y_te = get_xy(self.test, "binary")
        Xs, ys = stratified_subsample(X_tr, y_tr, 4000)
        pipe = make_pipeline(Xs, DecisionTreeClassifier(max_depth=8, random_state=42)).fit(Xs, ys)
        a = pipe.predict(X_te.iloc[:3000])
        _ = y_te.sample(frac=1, random_state=1)  # "mesanje" test oznaka ne sme uticati na predikcije
        b = pipe.predict(X_te.iloc[:3000])
        np.testing.assert_array_equal(a, b)


class TestMetrics(unittest.TestCase):
    def test_known_values(self):
        y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])
        y_pred = np.array([1, 1, 1, 0, 1, 1, 0, 0, 0, 0])
        m = compute_binary_metrics(y_true, y_pred)
        self.assertEqual((m["tp"], m["fn"], m["fp"], m["tn"]), (3, 1, 2, 4))
        self.assertAlmostEqual(m["accuracy"], 0.7)
        self.assertAlmostEqual(m["precision"], 3 / 5)
        self.assertAlmostEqual(m["recall"], 3 / 4)
        self.assertAlmostEqual(m["f1"], 2 * 0.6 * 0.75 / (0.6 + 0.75))
        self.assertAlmostEqual(m["fpr"], 2 / 6)
        self.assertAlmostEqual(m["fnr"], 1 / 4)

    def test_skewed_log1p_learns_columns_on_fit_only(self):
        rng = np.random.default_rng(0)
        X = np.column_stack([rng.exponential(1, 500) ** 4, rng.normal(0, 1, 500)])  # 1. asimetricna nenegativna, 2. normalna
        t = SkewedLog1p().fit(X)
        self.assertEqual(list(t.columns_), [0])
        Z = t.transform(np.array([[1e9, -5.0]]))
        self.assertAlmostEqual(Z[0, 0], np.log1p(1e9))
        self.assertEqual(Z[0, 1], -5.0)


@unittest.skipUnless((config.RESULTS_METRICS / "final_comparison.csv").exists(), "nema rezultata (pokrenite main.py)")
class TestSavedResults(unittest.TestCase):
    def test_table_matches_saved_predictions(self):
        M = config.RESULTS_METRICS
        table = pd.read_csv(M / "final_comparison.csv").set_index("Model")
        for model, slug in (("Decision Tree", "decision_tree_binary"), ("Random Forest", "random_forest_binary"),
                            ("Linear SVM (ceo trening)", "linear_svm_ceo_trening_binary"), ("SVM RBF (uzorak)", "svm_rbf_uzorak_binary")):
            p = np.load(M / f"{slug}_predictions.npz")
            m = compute_binary_metrics(p["y_true"], p["y_pred"], p["y_score"])
            for k, col in (("accuracy", "Accuracy"), ("precision", "Precision"), ("recall", "Recall"), ("f1", "F1"), ("roc_auc", "ROC_AUC")):
                self.assertAlmostEqual(m[k], table.loc[model, col], places=9, msg=f"{model} {k}")
            self.assertEqual(len(p["y_true"]), 82332)

    def test_all_models_evaluated_on_same_test_labels(self):
        M = config.RESULTS_METRICS
        ys = [np.load(M / f"{s}_predictions.npz")["y_true"] for s in
              ("decision_tree_binary", "random_forest_binary", "linear_svm_ceo_trening_binary", "svm_rbf_uzorak_binary")]
        for y in ys[1:]:
            np.testing.assert_array_equal(ys[0], y)

    def test_test_labels_match_official_file(self):
        if not HAVE_DATA:
            self.skipTest("dataset nije u data/raw/")
        _, test = load_train_test()
        y = np.load(config.RESULTS_METRICS / "decision_tree_binary_predictions.npz")["y_true"]
        np.testing.assert_array_equal(y, test["label"].values)


if __name__ == "__main__":
    unittest.main(verbosity=2)
