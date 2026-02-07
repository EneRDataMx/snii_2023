# %%
import pandas as pd
import missingno as msno
# %%
f = '../data/002_intermediate/snii_all.csv'
snii = pd.read_csv(f,index_col=0,parse_dates=True,low_memory=False)
snii.columns
# %%
snii["SEXO"] = snii["NOBILIS"].map({"DR.": "H", "DRA.": "M"})
# %%
msno.matrix(snii)
# %%
# Fill SEXO NaN using CVU lookup (most frequent SEXO per CVU)
cvu_sexo_map = (
    snii[snii["SEXO"].notna() & snii["CVU"].notna()]
    .groupby("CVU")["SEXO"]
    .agg(lambda x: x.mode().iloc[0])
)
mask = snii["SEXO"].isna() & snii["CVU"].notna()
snii.loc[mask, "SEXO"] = snii.loc[mask, "CVU"].map(cvu_sexo_map)
# %%
# Fill remaining SEXO NaN using first name prediction
snii["PRIMER_NOMBRE"] = (
    snii["NOMBRE"].str.split(",").str[1]
    .str.strip().str.split().str[0]
)
# Build name→sex map from rows where SEXO is known (>90% consistency)
known_names = snii[snii["SEXO"].notna() & snii["PRIMER_NOMBRE"].notna()]
name_counts = known_names.groupby("PRIMER_NOMBRE")["SEXO"].value_counts().unstack(fill_value=0)
name_counts["TOTAL"] = name_counts.sum(axis=1)
name_counts["DOMINANT"] = name_counts[["H", "M"]].idxmax(axis=1)
name_counts["PCT"] = name_counts[["H", "M"]].max(axis=1) / name_counts["TOTAL"] * 100
nombre_sexo_map = name_counts.loc[name_counts["PCT"] > 90, "DOMINANT"]

mask_nombre = snii["SEXO"].isna() & snii["PRIMER_NOMBRE"].notna() & snii.index.year.isin([2024, 2025])
snii.loc[mask_nombre, "SEXO"] = snii.loc[mask_nombre, "PRIMER_NOMBRE"].map(nombre_sexo_map)
snii = snii.drop(columns=["PRIMER_NOMBRE"])
# %%
msno.matrix(snii)

# %%
snii["EMERITO"] = snii["NIVEL"].isin(["Emérito", "E"])
snii["NIVEL"] = snii["NIVEL"].replace({
    "Emérito": "3",
    "E": "3",  # 2024-2025
    "Investigador(a) Nacional Nivel I": "1",
    "Investigador(a) Nacional Nivel II": "2",
    "Investigador(a) Nacional Nivel III": "3",
    "Candidato(a) a Investigador(a) Nacional": "C",
    "Candidato(a) a Investigador Nacional": "C",
    " Candidato(a) a Investigador(a) Nacional ": "C",
})
# %%
snii = snii.drop(columns=["NOMBRE","NOBILIS",'CVU'])
snii = snii.dropna(subset=["SEXO",'NIVEL'])
snii = snii.rename(columns={
    "ÁREA DEL CONOCIMIENTO": "AREA",
    "INSTITUCIÓN DE ADSCRIPCIÓN": "INSTITUCION",
    "ENTIDAD FEDERATIVA": "ESTADO",
})
# %%
snii.to_csv('../data/003_final/snii.csv')
# %%
msno.matrix(snii)
# %%
snii.groupby(snii.index.year).size()
# %%