# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**snii-historico** is a data analysis project for studying historical data about active researchers in Mexico's National Researchers System (SNII - Sistema Nacional de Investigadores). It processes annual XLSX snapshots of researcher rosters spanning 2000–2025.

## Tech Stack

- **Python 3.13** with **uv** as the package manager
- **pandas** for data loading/manipulation (especially Excel files)
- **numpy** for numerical operations
- **matplotlib** for visualization

## Common Commands

```bash
# Install dependencies
uv sync

# Run a script
uv run python scripts/<script_name>.py

# Add a dependency
uv add <package>
```

## Data Pipeline

### `data/001_raw/`
26 yearly Excel files (`Investigadores_vigentes_YYYY.xlsx`, 2000–2025). Column names vary across four eras (2000–2014, 2015–2021, 2022–2023, 2024–2025) — see `scripts/001_concatenating.py` for the full harmonization logic.

### `data/002_intermediate/`
`snii_all.csv` — unified dataset produced by `001_concatenating.py`. Indexed by `AÑO` (datetime). Columns: `CVU`, `NOMBRE`, `NOBILIS`, `NIVEL`, `ÁREA DEL CONOCIMIENTO`, `DISCIPLINA`, `INSTITUCIÓN DE ADSCRIPCIÓN`, `DEPENDENCIA`, `ENTIDAD FEDERATIVA`, `PAIS`. `NOBILIS` is NaN for 2022, 2024–2025. `PAIS` is NaN for 2024–2025.

### `data/003_final/`
`snii.csv` — cleaned dataset produced by `002_datacleaning.py`. Columns: `NIVEL` (C/1/2/3), `AREA`, `DISCIPLINA`, `INSTITUCION`, `DEPENDENCIA`, `ESTADO`, `PAIS`, `SEXO` (H/M), `EMERITO` (bool).

### SEXO assignment strategy (`002_datacleaning.py`)
1. **NOBILIS**: `DR.`→H, `DRA.`→M (2000–2021, 2023)
2. **CVU lookup**: for remaining NaN, use the most frequent SEXO from other years with the same CVU
3. **First name prediction** (2024–2025 only): map first name to SEXO using historical name→sex frequencies (>90% consistency threshold, ~98% accuracy)
4. Rows still without SEXO are dropped (~0.7% of total)

### Scripts
Scripts live in `scripts/` with numbered prefixes matching the pipeline stage they produce. Use `# %%` virtual cells to divide code into logical sections. Do not use `df` as part of any DataFrame variable name.

## Language

Dataset fields, file names, and domain terminology are in Spanish. Code and comments should follow existing conventions in the repository.
