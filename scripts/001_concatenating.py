# %% Imports and paths
import re
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/001_raw")
OUTPUT_PATH = Path("data/002_intermediate/snii_all.csv")

FINAL_COLUMNS = [
    "AÑO",
    "CVU",
    "NOMBRE",
    "NOBILIS",
    "NIVEL",
    "ÁREA DEL CONOCIMIENTO",
    "DISCIPLINA",
    "INSTITUCIÓN DE ADSCRIPCIÓN",
    "DEPENDENCIA",
    "ENTIDAD FEDERATIVA",
    "PAIS",
]

# %% Column normalization helpers

# After stripping whitespace/newlines and removing "(a partir de ...)" suffixes,
# these are the remaining name variants that need mapping to canonical names.
RENAME_MAP = {
    # CVU
    "CVU padrón corregido": "CVU",  # 2025
    # NOMBRE
    "NOMBRE DE LA INVESTIGADORA O INVESTIGADOR": "NOMBRE",  # 2000-2014
    "NOMBRE DE LA INVESTIGADORA O DEL INVESTIGADOR": "NOMBRE",  # 2015-2020
    "NOMBRE DEL INVESTIGADOR(A)": "NOMBRE",  # 2021
    "NOMBRE DEL INVESTIGADOR": "NOMBRE",  # 2023-2025
    # NOBILIS
    "GRADO ACADÉMICO": "NOBILIS",  # 2023
    # NIVEL
    "CATEGORÍA": "NIVEL",  # 2022-2024
    "CATEGORIA": "NIVEL",  # 2025 (no accent)
    # ÁREA DEL CONOCIMIENTO
    "ÁREA DE CONOCIMIENTO": "ÁREA DEL CONOCIMIENTO",  # 2024-2025
    # INSTITUCIÓN DE ADSCRIPCIÓN
    "INSTITUCION DE ADSCRIPCIÓN": "INSTITUCIÓN DE ADSCRIPCIÓN",  # 2022 missing accent
    "INSTITUCIÓN DE ACREDITACIÓN": "INSTITUCIÓN DE ADSCRIPCIÓN",  # 2024-2025
    # DEPENDENCIA
    "DEPENDENCIA DE ADSCRIPCIÓN": "DEPENDENCIA",  # 2023
    "DEPENDENCIA DE ACREDITACIÓN": "DEPENDENCIA",  # 2024-2025
    # ENTIDAD FEDERATIVA
    "ENTIDAD FEDERATIVA ADSCRIPCIÓN": "ENTIDAD FEDERATIVA",  # 2000-2014
    "ENTIDAD FEDERATIVA DE ADSCRIPCIÓN": "ENTIDAD FEDERATIVA",  # 2022-2023
    "ENTIDAD DE ACREDITACIÓN": "ENTIDAD FEDERATIVA",  # 2024-2025
    # PAIS
    "PAIS ADSCRIPCIÓN": "PAIS",  # 2000-2014
    "PAÍS": "PAIS",  # 2021
    "PAÍS DE ADSCRIPCIÓN": "PAIS",  # 2022-2023
}


def normalize_columns(columns: list[str]) -> list[str]:
    """Strip whitespace/newlines and remove '(a partir de YYYY)' suffixes."""
    cleaned = []
    for col in columns:
        col = " ".join(col.split())  # collapse whitespace and newlines
        col = re.sub(r"\s*\(a partir de \d{4}\)", "", col)
        col = col.strip()
        cleaned.append(col)
    return cleaned


# %% Read and harmonize all files

xlsx_files = sorted(RAW_DIR.glob("*.xlsx"))
yearly_frames = []

for filepath in xlsx_files:
    year = int(re.search(r"(\d{4})", filepath.name).group(1))

    raw = pd.read_excel(filepath)
    raw.columns = normalize_columns(raw.columns.tolist())

    # Skip CATEGORÍA→NIVEL rename when NIVEL already exists (2024-2025)
    rename = RENAME_MAP.copy()
    if "NIVEL" in raw.columns:
        rename.pop("CATEGORÍA", None)
        rename.pop("CATEGORIA", None)

    raw = raw.rename(columns=rename)

    # 2015+ files don't have an AÑO column — fill from filename
    if "AÑO" not in raw.columns:
        raw["AÑO"] = year

    # Keep only target columns (NOBILIS missing in 2022-2023 → fills with NaN)
    for col in FINAL_COLUMNS:
        if col not in raw.columns:
            raw[col] = pd.NA

    yearly_frames.append(raw[FINAL_COLUMNS])

    print(f"{year}: {len(raw):>6,} rows  ✓")

# %% Concatenate and set datetime index

investigadores = pd.concat(yearly_frames, ignore_index=True)

investigadores["CVU"] = pd.to_numeric(investigadores["CVU"], errors="coerce").astype("Int64")

investigadores["AÑO"] = pd.to_datetime(investigadores["AÑO"], format="%Y")
investigadores = investigadores.set_index("AÑO").sort_index()

print(f"\nTotal: {len(investigadores):,} rows, {investigadores.shape[1]} columns")
print(f"Date range: {investigadores.index.min()} → {investigadores.index.max()}")

# %% Save to CSV

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
investigadores.to_csv(OUTPUT_PATH)
print(f"\nSaved to {OUTPUT_PATH}")
