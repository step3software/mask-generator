# Optional generic image screening

Technical triage only: readability, dimensions, transparency, exposure/detail indicators, exact duplicates and perceptual similarity candidates. These checks do not evaluate three-piece geometry or reference-shape agreement. The active renderer/comparator is at the repository root.

From the repository root, run:

```powershell
python tools/generic_screening/evaluate.py path/to/images --config tools/generic_screening/config.example.json --output runs/screening-001
```

No model calls. Use a new report directory. Thresholds are screening heuristics; only the first frame is examined. The legacy desk_criteria field is optional reviewer text and is not evaluated by Python. Every domain_status remains not_evaluated.
