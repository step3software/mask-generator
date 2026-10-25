# Documentation index

Read [agent entry](../AGENTS.md) and [current status](status.md) first. Then select the relevant owner below.

| Task | Canonical reading | Existing implementation |
| --- | --- | --- |
| Run a demonstration or interpret files | [Operations](operations.md) | [demo.py](../demo.py), [compare.py](../compare.py) |
| Prepare scene, cameras, references, or bounds | [Contracts](contracts.md) | [cardboard.py](../cardboard.py), [reference template](../references.template.json) |
| Change renderer, metrics, or search | Relevant [contract section](contracts.md), then [implementation map](implementation.md) | Source/test links in the map |
| Choose the next development task | [M1 task ledger](status.md#m1--reproducible-baseline-fit) | Dependencies and completion checks; planned tasks are not completed features |
| Prepare actual target views | [Preparation procedure](operations.md#reference-preparation-procedure) and [bundle contract](contracts.md#reference-preparation-bundle) | Existing loaders; manual preparation and recorded camera estimates |
| Decide whether to extend the geometry | [Geometry decision criteria](contracts.md#geometry-suitability-decision) | Existing renderer and comparison evidence |
| Validate fitting or update evidence | [Benchmark protocol](operations.md#benchmark-protocol), then [status ledger](status.md) | Existing tests plus explicitly planned independent validation |
| Screen arbitrary image files | [Generic screening guide](../tools/generic_screening/README.md) | Its separate tool and test suite |
| Review this documentation reorganization | [Review evidence](evidence/documentation-review-2026-10-25.md) | Baseline and coverage recorded there |

Ownership: contracts describe scope and current behavior; operations describe procedures; implementation maps code to tests; status records progress and outstanding work; evidence records dated observations against exact refs. README and this index route readers rather than repeat those specifications.

No pre-existing documentation index, agent guide, status ledger, requirement identifiers, or decision register existed at the reviewed baseline. M1 now defines planned development work in the existing status ledger; it does not claim target acceptance or introduce a separate approval process. The review evidence is optional lookup, not mandatory startup reading.
