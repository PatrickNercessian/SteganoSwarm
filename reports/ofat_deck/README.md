# Hidden contagion results deck

Current deck: `output/hidden_contagion_final.pptx`. It has five slides and approximately 80–90 seconds of speaker notes. The script is also in `output/speaker_script.md`. The fuller analysis is `output/detector_analysis.md`.

The deck retains the experiment introduction, including the nine-of-ten recruitment result and a small puzzle-accuracy note. A restored slide covers live blocking and spread without code hints. Two slides cover detector context and the effect of counting filtered empty replies as flags.

## Data snapshot

All 95 planned OFAT experiment runs are complete. The detector analysis froze 2,259 of 2,280 expected output files. To compare the same messages across all 24 setups, the slides use the common 92 fully scored runs. Missing setup results affect N=20 seeds 3, 4, and 5. Read `output/detector_analysis.md` for exact denominators, all 24 setup scores, coverage, prompt effects, and interpretation limits.

Only `logs/ofat/*.json` and `logs/ofat/detect/*.json` enter the analysis. The source manifests and numerical results are in `.build/data_snapshot.json` and `.build/detector/snapshot.json`. No detector API calls or new experiment runs were made.

## Refresh

1. Run `python3 reports/ofat_deck/.build/analyze_detectors.py` to freeze a new detector snapshot.
2. Run `python3 reports/ofat_deck/.build/write_detector_report.py` to rebuild the analysis.
3. Run the presentation builder below with a **new output filename**. The finalizer will not overwrite an existing deck or receipt.
4. Review all rendered slides and revise the prose if coverage or conclusions change. Some explanatory notes describe this snapshot's missing N=20 runs, so a refresh needs editorial review.

```sh
RUNTIME_NODE_MODULES=/Users/patrick_nercessian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules RUNTIME_NODE=/Users/patrick_nercessian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node /Users/patrick_nercessian/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node reports/ofat_deck/.build/build.mjs /Users/patrick_nercessian/Documents/ChatGPT/hidden_contagion/reports/ofat_deck/output/hidden_contagion_detectors_v3.pptx
```

The builder preserves editable charts and tables and writes renders to `.build/slide-1.png` through `.build/slide-5.png`. Original experiment deck revisions remain in `output/`. The pre-detector builder is preserved in `.build/build_before_detectors.mjs`.

The fifth slide summarizes the presenter-supplied code anecdotes. Speaker notes retain the longer examples and source attribution.
