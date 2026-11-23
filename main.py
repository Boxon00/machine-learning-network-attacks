"""Glavna ulazna tacka: python main.py [--stage all|eda|dt|rf|svm|ablation|scaling|compare] [--quick]

  all       EDA -> Decision Tree -> Random Forest -> SVM -> ablacija -> poredjenje
  --quick   brza provera koda sa malim uzorcima (rezultati se upisuju u results_quick/)
Rezultati se cuvaju u results/metrics/ i results/figures/.
"""
import argparse
import os
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description="SIR1: ML u detekciji mreznih napada (UNSW-NB15)")
    parser.add_argument("--stage", default="all",
                        choices=["all", "eda", "dt", "rf", "svm", "ablation", "scaling", "compare"])
    parser.add_argument("--quick", action="store_true", help="samo provera koda (mali uzorci)")
    args = parser.parse_args()
    if args.quick:
        os.environ["SIR1_QUICK"] = "1"  # mora pre uvoza src.config

    from src import ablation, comparison, decision_tree, eda, random_forest, scaling, svm
    from src.data_loader import DatasetNotFoundError, load_train_test

    try:
        train, test = load_train_test()
    except DatasetNotFoundError as exc:
        print(exc)
        return 1

    stages = {
        "eda": lambda: eda.run_eda(train, test),
        "dt": lambda: decision_tree.run_experiment(train, test),
        "rf": lambda: random_forest.run_experiment(train, test),
        "svm": lambda: svm.run_experiment(train, test),
        "ablation": lambda: ablation.run_ablation(train, test),
        "scaling": lambda: scaling.run_scaling(train),
        "compare": lambda: comparison.run_comparison(),
    }
    order = list(stages) if args.stage == "all" else [args.stage]
    for name in order:
        t0 = time.perf_counter()
        print(f"\n=== {name} ===")
        stages[name]()
        print(f"=== {name} gotovo za {time.perf_counter() - t0:.1f}s ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
