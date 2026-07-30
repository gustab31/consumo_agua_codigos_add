# ============================================================
# 99_base_final_consumo_setor.py
#
# CONSOLIDAÇÃO BASE FINAL CONSUMO x SETOR CENSITÁRIO
#
# Entrada:
# resultados_04/consumo_lhabdia_filtrado.csv
# joinville_setores_mapa.shp
#
# Saídas:
# resultados_04/
#   base_final_consumo_setor.csv
#   base_final_consumo_setor.shp
#   relatorio_base_final.txt
#
# ============================================================


import os
import time
import pandas as pd
import geopandas as gpd


inicio = time.time()


print("="*70)
print("BASE FINAL CONSUMO x SETOR CENSITÁRIO")
print("="*70)


PASTA = "resultados_04"


arquivo_csv = os.path.join(
    PASTA,
    "consumo_lhabdia_filtrado.csv"
)


arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base consumo...")


df = pd.read_csv(
    arquivo_csv,
    encoding="utf-8-sig",
    low_memory=False
)


print(
    "Registros:",
    len(df)
)


print("\nColunas:")

for c in df.columns:
    print("-", c)



# ============================================================
# PADRONIZAR SETOR
# ============================================================


df["CD_SETOR_FINAL"] = (

    df["CD_SETOR_FINAL"]

    .astype(str)

    .str.replace(
        ".0",
        "",
        regex=False
    )

    .str.strip()

)



# ============================================================
# EXPORTAR CSV FINAL
# ============================================================


saida_csv = os.path.join(
    PASTA,
    "base_final_consumo_setor.csv"
)


df.to_csv(
    saida_csv,
    index=False,
    encoding="utf-8-sig"
)



# ============================================================
# SHAPEFILE FINAL
# ============================================================


print("\nLendo setores IBGE...")


gdf = gpd.read_file(
    arquivo_shp
)



gdf["CD_SETOR"] = (

    gdf["CD_SETOR"]

    .astype(str)

    .str.replace(
        ".0",
        "",
        regex=False
    )

    .str.strip()

)



print(
    "Setores mapa:",
    len(gdf)
)



print("\nJuntando dados...")


final = gdf.merge(

    df,

    left_on="CD_SETOR",

    right_on="CD_SETOR_FINAL",

    how="left"

)



saida_shp = os.path.join(

    PASTA,

    "base_final_consumo_setor.shp"

)



final.to_file(

    saida_shp,

    encoding="utf-8"

)
# ============================================================
# FIGURA PNG FINAL
# ============================================================

import matplotlib.pyplot as plt


print("\nGerando figura PNG...")


saida_png = os.path.join(
    PASTA,
    "99_mapa_final_consumo_lhabdia.png"
)


fig, ax = plt.subplots(
    figsize=(10,10)
)


final.plot(
    column="L_HAB_DIA_FILTRADO",
    cmap="RdYlBu_r",
    legend=True,
    linewidth=0.25,
    edgecolor="gray",
    ax=ax,
    missing_kwds={
        "color":"lightgrey",
        "label":"Sem dados"
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


print(saida_png)


# ============================================================
# RELATÓRIO
# ============================================================


relatorio = os.path.join(

    PASTA,

    "relatorio_base_final.txt"

)



with open(

    relatorio,

    "w",

    encoding="utf-8"

) as f:


    f.write(
        "BASE FINAL CONSUMO x SETOR\n"
    )

    f.write(
        "="*50+"\n\n"
    )

    f.write(
        f"Setores consumo: {len(df)}\n"
    )

    f.write(
        f"Setores mapa: {len(gdf)}\n"
    )

    f.write(
        f"Setores shapefile final: {len(final)}\n\n"
    )


    if "L_HAB_DIA_FILTRADO" in df.columns:

        f.write(
            "Estatística L/hab/dia filtrado\n"
        )

        f.write(
            str(
                df["L_HAB_DIA_FILTRADO"]
                .describe()
            )
        )


# ============================================================
# RESULTADO
# ============================================================


print("\n==============================")
print("ARQUIVOS GERADOS")
print("==============================")


print(saida_csv)

print(saida_shp)

print(relatorio)



print("\nResumo:")

print(
    "Setores:",
    len(df)
)


print(
    "Com L/hab/dia filtrado:",
    df["L_HAB_DIA_FILTRADO"].notna().sum()
)


print(
    "Suspeitos:",
    df["SETOR_SUSPEITO"].sum()
)


print(
    "\nTempo:",
    round(time.time()-inicio,2),
    "segundos"
)


print("\nFim Código 99.")