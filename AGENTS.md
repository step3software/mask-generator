# Agent entry point

Read [the documentation index](docs/README.md), then [current status](docs/status.md). Follow only the task-specific links from the index; the full documentation set is not required startup reading.

For forward development, choose the next eligible task from [M1](docs/status.md#m1--reproducible-baseline-fit), follow its linked procedure, and record completion evidence in that same ledger. Work from the user's designated development checkout rather than a generated output snapshot. Plans and proposed tests are not existing implementation.

- [Contracts](docs/contracts.md) owns existing scope, input formats, comparison semantics, and limitations.
- [Operations](docs/operations.md) owns commands and output interpretation.
- [Implementation map](docs/implementation.md) routes changes to existing code and tests.
- [Status](docs/status.md) owns current progress, missing inputs, and evidence links. Keep chronology out of startup navigation.

For a code task, inspect the relevant implementation and tests before changing behavior. If code and documentation disagree, report the discrepancy; an editorial update must not silently change acceptance, architecture, permissions, or authorization. Synthetic agreement is not a real-reference acceptance result.

Use [validation guidance](docs/operations.md#validation) appropriate to the change. Record the exact ref, commands actually run, and limitations when adding evidence. Documentation-only work does not by itself require the application test suites. This file is a routing guide, not a new project approval process.
