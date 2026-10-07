# Whispers in the Swarm

Open `index.html` in a browser. It is self-contained and needs no server, remote fonts, libraries, or API calls. Charts support pointer and keyboard inspection, with data tables and a light/dark toggle.

- `article.html`: editable article text and figure placeholders.
- `build.py`: preserves the original draft's styling and generates charts and the final page.
- `analyze.py`: recomputes metrics from all 95 saved swarm runs and 2,259 detector outputs.
- `analysis.json`: exact metrics, run-level results, and SHA-256 source manifest.
- `scheme_classifications.json`: preserved model-assisted classifications from the earlier Claude analysis (105 initiators: 95 Sol, 10 Opus).
- `original_draft.html`: unchanged copy of the unfinished Claude scratchpad draft.

To rebuild from the repository root:

```sh
python3 reports/blog/analyze.py
python3 reports/blog/build.py
```

All detector comparisons use the common 92-run cohort. Awareness is recomputed from saved `learned` and `plan_known` fields rather than potentially stale summary counts. Recruitment, explicit blocking, and filtered responses are distinguished in the article. The retry statistics use each blocked sender's next message, not an inferred same-payload retry.

Original draft: Claude conversation `231b36a3-4792-4212-86ae-b54281a56719`, titled “Model caching coverage.” Scheme classifications originated in conversation `6a3165e0-aa51-42f9-98c5-8c9c82445807`. The final conversation discussion and raw logs informed the completed article.

Validation: rendered in headless Chrome at desktop and phone widths; inspected figure screenshots; checked page overflow, JavaScript errors, tooltip focus/Escape, data-table expansion, and theme switching.
