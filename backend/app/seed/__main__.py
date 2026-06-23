import argparse
import logging
import sys

from .pregenerate import run_pregenerate, run_pregenerate_pilot
from .run import run, run_if_empty


def _configure_seed_logging() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Astra database")
    parser.add_argument(
        "--if-empty",
        action="store_true",
        help="Only seed when no subjects exist (used on Render release)",
    )
    parser.add_argument(
        "--pregenerate-backups",
        action="store_true",
        help="Generate AI backup questions for every chapter (run after seed; requires USE_AI)",
    )
    parser.add_argument(
        "--pregenerate-pilot",
        action="store_true",
        help="Generate AI bank for pilot chapters only (12 chapters × PILOT_AI_QUESTIONS_PER_CHAPTER)",
    )
    parser.add_argument(
        "--chapter",
        metavar="SLUG",
        help="With --pregenerate-backups, only process this chapter slug",
    )
    parser.add_argument(
        "--backup-multiplier",
        type=float,
        default=None,
        help="AI backups per chapter = multiplier × seed count (default: CHAPTER_BACKUP_MULTIPLIER / 2)",
    )
    parser.add_argument(
        "--pilot-questions",
        type=int,
        default=None,
        help="With --pregenerate-pilot, AI questions per pilot chapter (default: 35)",
    )
    args = parser.parse_args()
    if args.pregenerate_pilot:
        _configure_seed_logging()
        run_pregenerate_pilot(target_per_chapter=args.pilot_questions)
    elif args.pregenerate_backups:
        _configure_seed_logging()
        run_pregenerate(multiplier=args.backup_multiplier, chapter_slug=args.chapter)
    elif args.if_empty:
        run_if_empty()
    else:
        run()
