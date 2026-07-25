# transformer_layer

Transformer sizing and load allocation analysis for ResStock/OCHRE building data.

Extracted from [gld-opedss-ochre-helics](https://github.com/MidrarAdham/gld-opedss-ochre-helics) with full commit history preserved.

## Structure

- `config/` — run configuration (`config.toml`)
- `scripts/` — analysis scripts (load allocation, panel ratings, transformer sizing)
- `results/` — output CSVs/figures, grouped by method (`method1`–`method4`)
- `sources/` — reference documents (utility filings, test reports)

## Setup

```sh
poetry install
```

Dataset paths in `config/config.toml` point to a network-mounted dataset directory (`/mnt/datasets/...`) rather than anything bundled in this repo.
