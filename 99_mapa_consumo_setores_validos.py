# ============================================================
# 99_mapa_consumo_setores_validos.py
#
# MAPA FINAL CONSUMO x SETOR CENSITARIO
# SOMENTE SETORES COM DADOS
# ============================================================

import os
import time
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt


inicio = time.time()


print("="*70)
print("MAPA FINAL CONSUMO SETORES VALIDOS")
print("="*70)



PASTA = "resultados_04"



arquivo_csv = os.path.join(
    PASTA,
    "consumo_lhabdia_filtrado.csv"
)


arquivo_shp = (
    "joinville_setores_mapa.shp"
)



saida_csv = os.path.join(
    PASTA,
    "99_mapa_consumo_setores_validos.csv"
)


saida_shp = os.path.join(
    PASTA,
    "99_mapa_consumo_setores_validos.shp"
)


saida_png = os.path.join(
    PASTA,
    "99_mapa_consumo_setores_validos.png"
)


saida_txt = os.path.join(
    PASTA,
    "99_relatorio_mapa_final.txt"
)



# ============================================================
# LEITURA CONSUMO
# ============================================================


print("\nLendo consumo...")


df = pd.read_csv(
    arquivo_csv,
    encoding="utf-8-sig",
    low_memory=False
)



df["CD_SETOR_FINAL"] = (
    df["CD_SETOR_FINAL"]
    .astype(str)
    .str.replace(".0","",regex=False)
    .str.strip()
)



print(
    "Setores consumo:",
    len(df)
)



# ============================================================
# LEITURA MALHA
# ============================================================


print("\nLendo setores IBGE...")


gdf = gpd.read_file(
    arquivo_shp
)



gdf["CD_SETOR"] = (
    gdf["CD_SETOR"]
    .astype(str)
    .str.replace(".0","",regex=False)
    .str.strip()
)



print(
    "Setores IBGE:",
    len(gdf)
)



# ============================================================
# JUNCAO SOMENTE COM DADOS
# ============================================================


print("\nSelecionando setores com consumo...")


final = gdf.merge(
    df,
    left_on="CD_SETOR",
    right_on="CD_SETOR_FINAL",
    how="inner"
)



print(
    "Setores finais:",
    len(final)
)



# ============================================================
# EXPORTA CSV
# ============================================================


final.drop(
    columns="geometry"
).to_csv(
    saida_csv,
    index=False,
    encoding="utf-8-sig"
)



# ============================================================
# EXPORTA SHP
# ============================================================


final.to_file(
    saida_shp,
    encoding="utf-8"
)



# ============================================================
# PNG
# ============================================================


print("\nGerando PNG...")


fig, ax = plt.subplots(
    figsize=(10,10)
)



final.plot(
    column="L_HAB_DIA_FILTRADO",
    cmap="RdYlBu_r",
    legend=True,
    linewidth=0.25,
    edgecolor="black",
    ax=ax,
    missing_kwds={
        "color":"lightgrey"
    },
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
# RELATORIO
# ============================================================


with open(
    saida_txt,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "MAPA FINAL CONSUMO SETORES VALIDOS\n"
    )

    f.write("="*50+"\n")

    f.write(
        f"\nSetores IBGE: {len(gdf)}"
    )

    f.write(
        f"\nSetores consumo: {len(df)}"
    )

    f.write(
        f"\nSetores mapa final: {len(final)}"
    )



# ============================================================
# FINAL
# ============================================================


print("\n==============================")
print("ARQUIVOS GERADOS")
print("==============================")


print(saida_shp)
print(saida_csv)
print(saida_png)
print(saida_txt)


print("\nResumo:")
print(
    "Setores no mapa:",
    len(final)
)


print(
    "\nTempo:",
    round(time.time()-inicio,2),
    "segundos"
)


print("\nFim Codigo 99.")