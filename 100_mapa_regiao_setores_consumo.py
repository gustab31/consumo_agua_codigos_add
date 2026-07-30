# ============================================================
# 100_mapa_regiao_setores_consumo.py
# ============================================================

import os
import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely import wkt


inicio = time.time()


print("="*70)
print("MAPA REGIAO SETORES CENSITARIOS CONSUMO")
print("="*70)


# ============================================================
# ARQUIVOS
# ============================================================

arquivo_ibge = "filtrar_setores_cens.txt"

arquivo_consumo = (
    "resultados_04/base_final_consumo_setor.csv"
)


saida_shp = (
    "resultados_04/"
    "100_mapa_regiao_setores_consumo.shp"
)

saida_csv = (
    "resultados_04/"
    "100_mapa_regiao_setores_consumo.csv"
)

saida_png = (
    "resultados_04/"
    "100_mapa_regiao_setores_consumo.png"
)



# ============================================================
# VERIFICA ARQUIVOS
# ============================================================

for arq in [
    arquivo_ibge,
    arquivo_consumo
]:

    if not os.path.exists(arq):

        raise Exception(
            f"Arquivo nao encontrado: {arq}"
        )



# ============================================================
# LER SETORES IBGE
# ============================================================

print("\nLendo setores censitarios...")


# tenta automaticamente separador

try:

    ibge = pd.read_csv(
        arquivo_ibge,
        sep=";",
        encoding="latin1",
        low_memory=False
    )


    if len(ibge.columns) < 5:
        raise Exception()

except:

    ibge = pd.read_csv(
        arquivo_ibge,
        sep="\t",
        encoding="latin1",
        low_memory=False
    )


# limpa nomes

ibge.columns = (
    ibge.columns
    .astype(str)
    .str.strip()
    .str.replace("\ufeff","",regex=False)
)


print("\nColunas IBGE:")

for c in ibge.columns:
    print("-", c)



# procura CD_SETOR

campo_setor = None

for c in ibge.columns:

    if c.upper() == "CD_SETOR":
        campo_setor = c
        break


if campo_setor is None:

    raise Exception(
        "Campo CD_SETOR nao encontrado no arquivo IBGE"
    )



# padroniza

ibge["CD_SETOR"] = (
    ibge[campo_setor]
    .astype(str)
    .str.strip()
)



print(
    "\nSetores IBGE:",
    len(ibge)
)



# ============================================================
# LER CONSUMO
# ============================================================

print("\nLendo consumo...")


consumo = pd.read_csv(
    arquivo_consumo,
    encoding="utf-8-sig",
    low_memory=False
)


consumo["CD_SETOR_FINAL"] = (
    consumo["CD_SETOR_FINAL"]
    .astype(str)
    .str.replace(".0","",regex=False)
    .str.strip()
)



lista_setores = (
    consumo["CD_SETOR_FINAL"]
    .dropna()
    .unique()
)


print(
    "Setores consumo:",
    len(lista_setores)
)



# ============================================================
# FILTRO
# ============================================================

print("\nFiltrando regiao...")


regiao = ibge[
    ibge["CD_SETOR"].isin(lista_setores)
].copy()



print(
    "Setores encontrados:",
    len(regiao)
)



# ============================================================
# GEOMETRIA
# ============================================================

print("\nCriando geometria...")


if "wkt_geom" not in regiao.columns:

    raise Exception(
        "Campo wkt_geom nao encontrado"
    )


regiao["geometry"] = (
    regiao["wkt_geom"]
    .apply(wkt.loads)
)



gdf = gpd.GeoDataFrame(
    regiao,
    geometry="geometry",
    crs="EPSG:4674"
)



# ============================================================
# JUNTA CONSUMO
# ============================================================

print("\nJuntando consumo...")


gdf = gdf.merge(
    consumo,
    left_on="CD_SETOR",
    right_on="CD_SETOR_FINAL",
    how="inner"
)



print(
    "Setores finais:",
    len(gdf)
)



# ============================================================
# SALVA CSV
# ============================================================

print("\nSalvando CSV...")


gdf.drop(
    columns="geometry"
).to_csv(
    saida_csv,
    index=False,
    encoding="utf-8-sig"
)



# ============================================================
# SALVA SHP
# ============================================================

print("Salvando SHP...")


gdf.to_file(
    saida_shp,
    encoding="utf-8"
)



# ============================================================
# PNG
# ============================================================

print("Gerando PNG...")


fig, ax = plt.subplots(
    figsize=(10,10)
)



gdf.plot(
    column="L_HAB_DIA_FILTRADO",
    cmap="RdYlBu_r",
    legend=True,
    linewidth=0.25,
    edgecolor="black",
    ax=ax,
    legend_kwds={
        "label":"Consumo L hab dia"
    }
)



ax.set_title(
    "Consumo de agua por setor censitario",
    fontsize=14
)


ax.axis("off")


plt.tight_layout()


plt.savefig(
    saida_png,
    dpi=300,
    bbox_inches="tight"
)


plt.close()



# ============================================================
# FINAL
# ============================================================

print("\n==============================")
print("ARQUIVOS GERADOS")
print("==============================")


print(saida_shp)
print(saida_csv)
print(saida_png)


print("\nResumo final:")
print(
    "Setores:",
    len(gdf)
)


print(
    "Tempo:",
    round(time.time()-inicio,2),
    "segundos"
)


print("\nFim Codigo 100.")