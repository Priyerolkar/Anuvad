# Evaluation results

_Last updated: 2026-05-08_

Model: `ai4bharat/indictrans2-en-indic-dist-200M`

| Direction | n | BLEU | chrF | Avg latency | P95 latency |
|---|---|---|---|---|---|
| English → Marathi | 20 | 30.39 | 66.18 | 588.0 ms | 700.9 ms |
| English → Hindi | 20 | 42.57 | 65.85 | 592.4 ms | 680.1 ms |

## Notes
- BLEU and chrF computed with `sacrebleu` on the hand-curated engineering test set.
- Latency measured per-sentence on the active device (CPU unless GPU available).
- Test set lives at `evaluation/test_set.csv` and is version-controlled.
