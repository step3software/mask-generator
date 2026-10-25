# Optional generic image screening

Technical triage only: readability, dimensions, transparency, exposure/detail indicators, exact duplicates, and perceptual similarity candidates. These checks do not evaluate three-piece geometry or reference-shape agreement. The active pipeline is routed through the [documentation index](../../docs/README.md).

From the repository root:

```powershell
python tools/generic_screening/evaluate.py path/to/images --config tools/generic_screening/config.example.json --output runs/screening-001
```

Use a new report directory. Outputs include compact summaries, CSV/JSONL records, a bounded queue, and a contact sheet when selected images exist. No model calls occur. Threshold defaults in [config.example.json](config.example.json) and [evaluate.py](evaluate.py) are screening heuristics, not shape requirements. Only the first frame is examined. The legacy `desk_criteria` field is optional reviewer text; Python never evaluates it. Every `domain_status` remains `not_evaluated`.

Run the separate suite using [validation instructions](../../docs/operations.md#validation). [Project status](../../docs/status.md) owns current progress and evidence; this guide owns only generic-tool usage.
