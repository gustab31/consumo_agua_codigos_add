# ============================================================
# 103_estimativa_consumo_setores.py
#
# ESTIMATIVA CONSUMO L/hab/dia
# SOMENTE SETORES DO FILTRO CENSITARIO
#
# Entradas:
# resultados_04/base_final_consumo_setor.csv
# joinville_setores_mapa.shp
# filtrar_setores_cens.txt
#
# Saídas:
# resultados_05/
#
# 103_consumo_setores_completo.csv
# 103_consumo_setores_completo.shp
# 103_relatorio_estimativa.txt
# 103_tabela_comparacao.csv
# 103_mapa_consumo_completo.png
# 103_distribuicao_consumo.png
#
# ============================================================


import os
import time
import warnings

import pandas as pd
import geopandas as gpd
import numpy as np

import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error


warnings.filterwarnings("ignore")


inicio = time.time()


print("="*70)
print("ESTIMATIVA CONSUMO SETORES CENSITÁRIOS")
print("="*70)



# ============================================================
# PASTAS
# ============================================================


entrada = "resultados_04"
saida = "resultados_05"


os.makedirs(
    saida,
    exist_ok=True
)



arquivo_consumo = os.path.join(
    entrada,
    "base_final_consumo_setor.csv"
)


arquivo_shape = (
    "joinville_setores_mapa.shp"
)


arquivo_filtro = (
    "filtrar_setores_cens.txt"
)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo consumo...")


df = pd.read_csv(

    arquivo_consumo,

    encoding="utf-8-sig",

    low_memory=False

)


print(
    "Registros consumo:",
    len(df)
)



print("\nLendo setores IBGE...")


gdf = gpd.read_file(
    arquivo_shape
)


print(
    "Setores IBGE:",
    len(gdf)
)



# ============================================================
# PADRONIZAR CÓDIGOS
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



# ============================================================
# FILTRO TXT
# ============================================================


print("\nLendo filtro censitário...")


filtro = pd.read_csv(

    arquivo_filtro,

    sep="\t",

    encoding="utf-8-sig",

    low_memory=False

)


print(
    "Colunas filtro:"
)

print(
    filtro.columns.tolist()
)



filtro["CD_SETOR"] = (

    filtro["CD_SETOR"]

    .astype(str)

    .str.replace(
        ".0",
        "",
        regex=False
    )

    .str.strip()

)



gdf = gdf[
    gdf["CD_SETOR"].isin(
        filtro["CD_SETOR"]
    )
].copy()



print(
    "Setores após filtro:",
    len(gdf)
)



# ============================================================
# CRUZAMENTO CONSUMO
# ============================================================


print("\nCruzando consumo...")


base = gdf.merge(

    df,

    left_on="CD_SETOR",

    right_on="CD_SETOR_FINAL",

    how="left"

)



print(
    "Base analisada:",
    len(base)
)



# ============================================================
# VARIÁVEL OBSERVADA
# ============================================================


base["L_HAB_DIA_OBS"] = (

    base["L_HAB_DIA_FILTRADO"]

)



base["TIPO_DADO"] = np.where(

    base["L_HAB_DIA_OBS"].notna(),

    "OBSERVADO",

    "ESTIMADO"

)



print(
    "Observados:",
    (base["TIPO_DADO"]=="OBSERVADO").sum()
)


print(
    "Faltantes:",
    (base["TIPO_DADO"]=="ESTIMADO").sum()
)

# ============================================================
# PREPARAÇÃO DAS VARIÁVEIS
# ============================================================


print("\nPreparando variáveis...")


# população

base["POPULACAO"] = (

    base["POPULACAO"]

    .fillna(
        base["POPULACAO"].median()
    )

)


# matrículas

base["MATRICULAS"] = (

    base["MATRICULAS"]

    .fillna(0)

)



# densidade populacional

base["DENSIDADE"] = (

    base["POPULACAO"]

    /
    base["AREA_KM2"]

)



base["DENSIDADE"] = (

    base["DENSIDADE"]

    .replace(
        [np.inf,-np.inf],
        np.nan
    )

    .fillna(0)

)



# ============================================================
# MÉDIA DOS SETORES VIZINHOS
# ============================================================


print("\nCalculando vizinhança espacial...")


proj = base.to_crs(
    31982
)


proj["CENTRO"] = (

    proj.geometry.centroid

)



observados = proj[
    proj["L_HAB_DIA_OBS"].notna()
].copy()



media_vizinhos = []



for idx,linha in proj.iterrows():


    distancia = (

        observados["CENTRO"]

        .distance(
            linha["CENTRO"]
        )

    )


    proximos = (

        observados

        .loc[
            distancia.nsmallest(5).index,
            "L_HAB_DIA_OBS"
        ]

    )


    if len(proximos) > 0:

        media_vizinhos.append(

            proximos.mean()

        )

    else:

        media_vizinhos.append(

            observados["L_HAB_DIA_OBS"]
            .mean()

        )



base["MEDIA_VIZINHOS"] = media_vizinhos



# ============================================================
# TREINAMENTO DO MODELO
# ============================================================


print("\nTreinando modelo...")


treino = base[
    base["L_HAB_DIA_OBS"].notna()
].copy()



variaveis = [

    "POPULACAO",

    "MATRICULAS",

    "DENSIDADE",

    "MEDIA_VIZINHOS"

]



X = treino[variaveis]


y = treino["L_HAB_DIA_OBS"]



X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=0.20,

    random_state=42

)



modelo = RandomForestRegressor(

    n_estimators=300,

    max_depth=12,

    random_state=42

)



modelo.fit(

    X_train,

    y_train

)



# validação

previsto = modelo.predict(

    X_test

)



erro = mean_absolute_error(

    y_test,

    previsto

)



print(

    "Erro médio MAE:",

    round(erro,2),

    "L/hab/dia"

)



# ============================================================
# ESTIMATIVA DOS SETORES FALTANTES
# ============================================================


print("\nEstimando setores faltantes...")


faltantes = (

    base["L_HAB_DIA_OBS"]

    .isna()

)



base.loc[

    faltantes,

    "L_HAB_DIA_EST"

] = modelo.predict(

    base.loc[
        faltantes,
        variaveis
    ]

)



# valor final

base["L_HAB_DIA_FINAL"] = np.where(

    base["L_HAB_DIA_OBS"].notna(),

    base["L_HAB_DIA_OBS"],

    base["L_HAB_DIA_EST"]

)



# confiança

base["CONFIANCA_ESTIMATIVA"] = np.where(

    base["TIPO_DADO"]=="OBSERVADO",

    100,

    100 -

    (

        erro /

        base["L_HAB_DIA_FINAL"]

        *100

    )

)



base["CONFIANCA_ESTIMATIVA"] = (

    base["CONFIANCA_ESTIMATIVA"]

    .replace(
        [np.inf,-np.inf],
        np.nan
    )

    .fillna(0)

    .clip(0,100)

)



print("\nEstimativas concluídas")


print(

    "Observados:",

    (
        base["TIPO_DADO"]
        =="OBSERVADO"
    ).sum()

)


print(

    "Estimados:",

    (
        base["TIPO_DADO"]
        =="ESTIMADO"
    ).sum()

)

# ============================================================
# EXPORTAR CSV
# ============================================================


print("\nGerando arquivos...")


arquivo_csv_saida = os.path.join(

    saida,

    "103_consumo_setores_completo.csv"

)



base.drop(

    columns="geometry"

).to_csv(

    arquivo_csv_saida,

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# EXPORTAR SHP
# ============================================================


arquivo_shp_saida = os.path.join(

    saida,

    "103_consumo_setores_completo.shp"

)



# reduzir nomes para limite do shapefile

base_shp = base.copy()



renomear = {

    "L_HAB_DIA_OBS":
    "LHAB_OBS",

    "L_HAB_DIA_EST":
    "LHAB_EST",

    "L_HAB_DIA_FINAL":
    "LHAB_FINAL",

    "TIPO_DADO":
    "TIPO",

    "CONFIANCA_ESTIMATIVA":
    "CONFIANCA"

}


base_shp = base_shp.rename(

    columns=renomear

)



base_shp.to_file(

    arquivo_shp_saida,

    encoding="utf-8"

)



# ============================================================
# TABELA COMPARAÇÃO
# ============================================================


comparacao = pd.DataFrame({

    "TIPO_DADO":[

        "OBSERVADO",

        "ESTIMADO",

        "GERAL"

    ],

    "N_SETOR":[

        (
            base["TIPO_DADO"]
            =="OBSERVADO"
        ).sum(),

        (
            base["TIPO_DADO"]
            =="ESTIMADO"
        ).sum(),

        len(base)

    ],

    "MEDIA_L_HAB_DIA":[

        base.loc[

            base["TIPO_DADO"]
            =="OBSERVADO",

            "L_HAB_DIA_FINAL"

        ].mean(),


        base.loc[

            base["TIPO_DADO"]
            =="ESTIMADO",

            "L_HAB_DIA_FINAL"

        ].mean(),


        base["L_HAB_DIA_FINAL"].mean()

    ]

})



comparacao.to_csv(

    os.path.join(

        saida,

        "103_tabela_comparacao.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# PNG - DISTRIBUIÇÃO
# ============================================================


plt.figure(

    figsize=(9,6)

)


plt.hist(

    base["L_HAB_DIA_FINAL"].dropna(),

    bins=30,

    color="#1565C0",

    edgecolor="black"

)



plt.xlabel(

    "Consumo (L/hab/dia)"

)


plt.ylabel(

    "Número de setores"

)


plt.title(

    "Distribuição do consumo estimado"

)



plt.savefig(

    os.path.join(

        saida,

        "103_distribuicao_consumo.png"

    ),

    dpi=300,

    bbox_inches="tight"

)



plt.close()



# ============================================================
# PNG - MAPA
# ============================================================


print("\nGerando mapa...")


fig,ax = plt.subplots(

    figsize=(12,10)

)



cores = [

    "#08306B",

    "#2171B5",

    "#41AB5D",

    "#FE9929",

    "#990000"

]



base.plot(

    column="L_HAB_DIA_FINAL",

    cmap="RdYlBu_r",

    scheme="quantiles",

    k=5,

    legend=True,

    ax=ax,

    edgecolor="black",

    linewidth=0.15

)



# destacar estimados

base[

    base["TIPO_DADO"]=="ESTIMADO"

].boundary.plot(

    ax=ax,

    color="black",

    linewidth=0.3

)



ax.set_title(

    "Consumo específico de água\nL/hab/dia"

,

    fontsize=16

)


ax.axis("off")



# escala simples

ax.text(

    0.02,

    0.02,

    "Fonte: dados de consumo + estimativa espacial",

    transform=ax.transAxes,

    fontsize=9

)



plt.savefig(

    os.path.join(

        saida,

        "103_mapa_consumo_completo.png"

    ),

    dpi=300,

    bbox_inches="tight"

)



plt.close()



# ============================================================
# RELATÓRIO
# ============================================================


relatorio = os.path.join(

    saida,

    "103_relatorio_estimativa.txt"

)



with open(

    relatorio,

    "w",

    encoding="utf-8"

) as f:


    f.write(

        "ESTIMATIVA CONSUMO SETORES CENSITÁRIOS\n"

    )

    f.write(

        "="*60+"\n\n"

    )


    f.write(

        f"Setores analisados: {len(base)}\n"

    )


    f.write(

        f"Observados: {(base.TIPO_DADO=='OBSERVADO').sum()}\n"

    )


    f.write(

        f"Estimados: {(base.TIPO_DADO=='ESTIMADO').sum()}\n\n"

    )


    f.write(

        f"Erro MAE validação: {erro:.2f} L/hab/dia\n\n"

    )


    f.write(

        "Estatísticas L/hab/dia\n"

    )


    f.write(

        str(

            base["L_HAB_DIA_FINAL"]

            .describe()

        )

    )



# ============================================================
# FINAL
# ============================================================


print("\n==============================")

print("ARQUIVOS GERADOS")

print("==============================")


print(arquivo_csv_saida)

print(arquivo_shp_saida)

print(

    os.path.join(

        saida,

        "103_mapa_consumo_completo.png"

    )

)


print(

    os.path.join(

        saida,

        "103_relatorio_estimativa.txt"

    )

)



print("\nResumo:")


print(

    "Setores:",

    len(base)

)


print(

    "Observados:",

    (
        base["TIPO_DADO"]
        =="OBSERVADO"
    ).sum()

)


print(

    "Estimados:",

    (
        base["TIPO_DADO"]
        =="ESTIMADO"
    ).sum()

)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim Código 103.")