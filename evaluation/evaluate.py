"""
Anuvad evaluation script.

Runs the translator over evaluation/test_set.csv (columns: english, reference_marathi,
reference_hindi, ...) and reports BLEU and chrF scores per direction.

Usage:
    python -m evaluation.evaluate
    python -m evaluation.evaluate --target marathi
    python -m evaluation.evaluate --target hindi --limit 50

Writes a markdown summary to evaluation/results.md so it's easy to paste into your
README. Aim to keep your test set under version control: it IS your portfolio.
"""

from __future__ import annotations

import argparse
import csv
import logging
import statistics
import sys
import time
from pathlib import Path

import sacrebleu

from api.translator import SUPPORTED_LANGUAGES, get_translator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

EVAL_DIR = Path(__file__).parent
TEST_SET_PATH = EVAL_DIR / "test_set.csv"
RESULTS_PATH = EVAL_DIR / "results.md"


def load_test_set(path: Path, target_lang: str) -> tuple[list[str], list[str]]:
    """Load source English sentences and target-language references from CSV."""
    if not path.exists():
        sys.exit(
            f"Test set not found at {path}.\n"
            "Create a CSV with columns: english,reference_marathi,reference_hindi,..."
        )

    ref_col = f"reference_{target_lang}"
    sources, references = [], []
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "english" not in reader.fieldnames or ref_col not in reader.fieldnames:
            sys.exit(
                f"CSV must contain columns 'english' and '{ref_col}'. "
                f"Found: {reader.fieldnames}"
            )
        for row in reader:
            src = (row.get("english") or "").strip()
            ref = (row.get(ref_col) or "").strip()
            if src and ref:
                sources.append(src)
                references.append(ref)
    return sources, references


def evaluate(target_lang: str = "marathi", limit: int | None = None) -> dict:
    if target_lang not in SUPPORTED_LANGUAGES:
        sys.exit(f"Unsupported language '{target_lang}'.")

    sources, references = load_test_set(TEST_SET_PATH, target_lang)
    if limit:
        sources, references = sources[:limit], references[:limit]
    n = len(sources)
    if n == 0:
        sys.exit("Test set is empty.")
    logger.info("Evaluating %d sentences for English -> %s ...", n, target_lang)

    translator = get_translator()
    t0 = time.perf_counter()
    results = translator.translate_batch(sources, target_lang=target_lang)
    total_s = time.perf_counter() - t0
    hypotheses = [r.translated_text for r in results]
    per_item_latencies = [r.latency_ms for r in results]

    # sacreBLEU expects references as list-of-list (one ref set per system output).
    bleu = sacrebleu.corpus_bleu(hypotheses, [references])
    chrf = sacrebleu.corpus_chrf(hypotheses, [references])

    return {
        "target_lang": target_lang,
        "n": n,
        "bleu": round(bleu.score, 2),
        "chrf": round(chrf.score, 2),
        "avg_latency_ms": round(statistics.mean(per_item_latencies), 1),
        "p95_latency_ms": round(
            statistics.quantiles(per_item_latencies, n=20)[-1]
            if len(per_item_latencies) >= 20
            else max(per_item_latencies),
            1,
        ),
        "total_seconds": round(total_s, 2),
        "model": translator.model_name,
    }


def write_results_markdown(rows: list[dict]) -> None:
    lines: list[str] = [
        "# Evaluation results",
        "",
        f"_Last updated: {time.strftime('%Y-%m-%d')}_",
        "",
        f"Model: `{rows[0]['model']}`",
        "",
        "| Direction | n | BLEU | chrF | Avg latency | P95 latency |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| English → {r['target_lang'].title()} | {r['n']} | "
            f"{r['bleu']} | {r['chrf']} | {r['avg_latency_ms']} ms | "
            f"{r['p95_latency_ms']} ms |"
        )
    lines += [
        "",
        "## Notes",
        "- BLEU and chrF computed with `sacrebleu` on the hand-curated engineering test set.",
        "- Latency measured per-sentence on the active device (CPU unless GPU available).",
        "- Test set lives at `evaluation/test_set.csv` and is version-controlled.",
        "",
    ]
    RESULTS_PATH.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote %s", RESULTS_PATH)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Anuvad on engineering test set.")
    parser.add_argument(
        "--target",
        nargs="*",
        default=["marathi", "hindi"],
        help="One or more target languages.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit test set size.")
    args = parser.parse_args()

    rows = []
    for lang in args.target:
        result = evaluate(target_lang=lang, limit=args.limit)
        print(
            f"\nEnglish -> {lang}: BLEU {result['bleu']}  chrF {result['chrf']}  "
            f"avg latency {result['avg_latency_ms']} ms  (n={result['n']})"
        )
        rows.append(result)

    if rows:
        write_results_markdown(rows)


if __name__ == "__main__":
    main()
