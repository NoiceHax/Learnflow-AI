import argparse

from .run import run, run_if_empty

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Astra database")
    parser.add_argument(
        "--if-empty",
        action="store_true",
        help="Only seed when no subjects exist (used on Render release)",
    )
    args = parser.parse_args()
    if args.if_empty:
        run_if_empty()
    else:
        run()
