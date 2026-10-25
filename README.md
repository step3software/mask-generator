# Mask Generator

Render one assembly of exactly three curved cardboard pieces from multiple viewpoints, then compare the projections against reference masks. The pipeline uses local Python rendering and measurements, with bounded previews for optional visual review.

Start with the [documentation index](docs/README.md). Agents enter through [AGENTS.md](AGENTS.md). Current progress and unresolved inputs have one owner: [project status](docs/status.md).

## Available now

See the [implementation map](docs/implementation.md) for the renderer, comparator, geometry search, and tests. The [scope contract](docs/contracts.md#scope-and-interpretation) distinguishes technical measurements from target acceptance.

## Run the synthetic demonstration

Follow [installation and demo instructions](docs/operations.md#install-and-run-the-demo). Included examples are synthetic fixtures, not target reconstructions.

## Inputs still needed

Use [the current input ledger](docs/status.md#outstanding-inputs). Missing target evidence does not prevent unrelated documentation or synthetic software work.

## Scene and camera schema

See [scene format](docs/contracts.md#scene-format) and [camera format](docs/contracts.md#camera-format). The [synthetic scene](examples/synthetic-scene.json) demonstrates the structure only.

## References and batch comparison

See [reference format](docs/contracts.md#reference-format) and [comparison operations](docs/operations.md#prepare-references-and-compare).

## Supported comparison measures

See [measurements and ranking](docs/contracts.md#measurements-and-ranking). A high score is not an acceptance verdict.

## Search within explicit bounds

See [search contract](docs/contracts.md#search-bounds) and [search command](docs/operations.md#search-and-render).

## Compact reports and low-token review

See [review bounds](docs/contracts.md#bounded-review) and [report interpretation](docs/operations.md#read-the-reports).

## Tests

Use [validation commands](docs/operations.md#validation). Existing evidence is recorded against its tested ref in [status](docs/status.md#evidence).

## Optional generic screening

The [generic screening tool](tools/generic_screening/README.md) performs technical triage separately from shape matching.
