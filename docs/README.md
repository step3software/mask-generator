# Documentation index

Read [agent entry](../AGENTS.md) and [current status](status.md) first. Then select the relevant owner below.

| Task | Canonical reading | Existing implementation |
| --- | --- | --- |
| Run a demonstration or interpret files | [Operations](operations.md) | [demo.py](../demo.py), [compare.py](../compare.py) |
| Prepare scene, cameras, references, or bounds | [Contracts](contracts.md) | [cardboard.py](../cardboard.py), [reference template](../references.template.json) |
| Change renderer, metrics, or search | Relevant [contract section](contracts.md), then [implementation map](implementation.md) | Source/test links in the map |
| Continue target fitting or update evidence | [Status ledger](status.md) | Existing contracts and operations; do not invent missing target inputs |
| Screen arbitrary image files | [Generic screening guide](../tools/generic_screening/README.md) | Its separate tool and test suite |
| Review this documentation reorganization | [Review evidence](evidence/documentation-review-2026-10-25.md) | Baseline and coverage recorded there |

Ownership: contracts describe scope and current behavior; operations describe procedures; implementation maps code to tests; status records progress and outstanding work; evidence records dated observations against exact refs. README and this index route readers rather than repeat those specifications.

No pre-existing documentation index, agent guide, status ledger, requirement identifiers, or decision register existed at the reviewed baseline. No separate milestone or acceptance policy is introduced by this layout. The review evidence is optional lookup, not mandatory startup reading.
