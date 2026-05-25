"""
Entry point for running the SPSS Modeler stream builder.

Examples
--------
# Basic – CSV with C&RT (default):
    python run_stream.py --data data/customers.csv --target Churn

# Override algorithm:
    python run_stream.py --data data/customers.sav --target Churn --model randomforest

# Save the resulting stream:
    python run_stream.py --data data/customers.csv --target Churn --save output/churn_model.str
"""

import argparse
import sys
from stream_builder import build_and_run

SUPPORTED_MODELS = [
    "cartree",
    "chaid",
    "logistic",
    "randomforest",
    "neuralnet",
]


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Build, run, and evaluate an SPSS Modeler predictive stream."
    )
    parser.add_argument(
        "--data",
        required=True,
        help="Path to the input data file (.csv, .sav, .xlsx).",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Name of the target (outcome) field.",
    )
    parser.add_argument(
        "--model",
        default="cartree",
        choices=SUPPORTED_MODELS,
        help="Modeling algorithm to use (default: cartree).",
    )
    parser.add_argument(
        "--save",
        default=None,
        metavar="STREAM_PATH",
        help="Optional path to save the finished .str stream file.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    print("=" * 60)
    print("SPSS Modeler Stream Builder")
    print("=" * 60)
    print(f"  Data   : {args.data}")
    print(f"  Target : {args.target}")
    print(f"  Model  : {args.model}")
    print(f"  Save to: {args.save or '(not saved)'}")
    print("-" * 60)

    try:
        build_and_run(
            data_path=args.data,
            target_field=args.target,
            model_type=args.model,
            stream_save_path=args.save,
        )
        print("=" * 60)
        print("Done – stream built and evaluated successfully.")
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
