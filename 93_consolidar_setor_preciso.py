# ============================================================
# 94_associar_localizacao_completa_setor.py
#
# LOCALIZACAO COMPLETA x SETOR CENSITARIO IBGE
#
# Entrada:
#   2022.06.29. relatorio 75 1.xlsx
#   joinville_setores_mapa.shp
#
# Saída:
#   resultados\matricula_setor_preciso.csv
#
# ============================================================


import os
import time
import warnings

import pandas as pd
import geopandas as gpd


warnings.filterwarnings("ignore")


inicio = time.time()


print("="*70)
print("ASSOCIAÇÃO LOCALIZAÇÃO COMPLETA x SETOR CENSITÁRIO")
print("="*70)


RESULTADOS = "resultados"


arquivo_excel = "2022.06.29. relatorio 75 1.xlsx"

arquivo_shp = "joinville_setores_mapa.shp"



# ============================================================
# FUNÇÃO
# ============================================================


def texto(x):

    if pd.isna(x):
        return ""

    return str(x).strip()



# ============================================================
# LER RELATÓRIO
# ============================================================


print("\nLendo Relatório 75...")


bruto = pd.read_excel(
    arquivo_excel,
    header=None
)



cab = None


for i in range(15):

    linha = (

        bruto.iloc[i]
        .apply(texto)
        .tolist()

    )

    t = " ".join(linha).lower()


    if (
        "matricula" in t
        and "localizacao" in t
    ):

        cab = i
        break



if cab is None:

    raise Exception(
        "Cabeçalho não encontrado"
    )



print(
    "Cabeçalho:",
    cab
)



df = pd.read_excel(
    arquivo_excel,
    header=cab
)



print(
    "Registros:",
    len(df)
)



# ============================================================
# CAMPOS
# ============================================================


campos = [

    "Matricula",
    "Localizacao",
    "Bairro"

]


base = df[campos].copy()



base["LOCALIZACAO"] = (

    base["Localizacao"]
    .apply(texto)

)



# ============================================================
# EXTRAIR BLOCOS
# ============================================================


print("\nExtraindo blocos...")


partes = (

    base["LOCALIZACAO"]
    .str.split(".")

)



for i in range(6):

    base[f"BLOCO_{i+1}"] = partes.apply(

        lambda x:

        x[i]

        if len(x)>i

        else ""

    )



# usar do 3 ao 6

base["CHAVE_LOCAL"] = (

    base["BLOCO_3"]
    + "."
    + base["BLOCO_4"]
    + "."
    + base["BLOCO_5"]
    + "."
    + base["BLOCO_6"]

)



print(

    "Chaves únicas:",

    base["CHAVE_LOCAL"].nunique()

)



# ============================================================
# LER SETORES
# ============================================================


print("\nLendo setores IBGE...")


gdf = gpd.read_file(
    arquivo_shp
)



print(
    "Setores:",
    len(gdf)
)



gdf["NM_BAIRRO"] = (

    gdf["NM_BAIRRO"]
    .apply(texto)
    .str.upper()

)


gdf["CD_SETOR"] = (

    gdf["CD_SETOR"]
    .astype(str)
    .str.replace(".0","",regex=False)

)



# ============================================================
# RELAÇÃO BLOCO COMPLETO x SETOR
# ============================================================


print("\nCriando candidatos...")


# usa bairro como filtro territorial


tmp = base.merge(

    gdf[

        [
            "CD_SETOR",
            "NM_BAIRRO"

        ]

    ],

    left_on=

    base["Bairro"].str.upper(),

    right_on=

    gdf["NM_BAIRRO"],

    how="left"

)



# remover coluna auxiliar

tmp = tmp.drop(

    columns=["key_0"],

    errors="ignore"

)



print(

    "Candidatos gerados:",

    len(tmp)

)



# ============================================================
# ESCOLHER SETOR DOMINANTE
# ============================================================


print("\nCalculando confiança...")


ranking = (

    tmp

    .dropna(
        subset=["CD_SETOR"]
    )

    .groupby(

        [

            "CHAVE_LOCAL",

            "CD_SETOR"

        ]

    )

    .size()

    .reset_index(
        name="QTD"
    )

)



ranking["CONFIANCA"] = (

    ranking["QTD"]

    /

    ranking.groupby(
        "CHAVE_LOCAL"
    )["QTD"]

    .transform("sum")

    *

    100

)



melhor = (

    ranking

    .sort_values(

        "CONFIANCA",

        ascending=False

    )

    .groupby(
        "CHAVE_LOCAL"
    )

    .first()

    .reset_index()

)



melhor = melhor.rename(

    columns={

        "CD_SETOR":

        "CD_SETOR_FINAL"

    }

)



print(

    "Localizações resolvidas:",

    len(melhor)

)



# ============================================================
# ASSOCIAR MATRÍCULAS
# ============================================================


print("\nAssociando matrículas...")


final = base.merge(

    melhor[

        [

            "CHAVE_LOCAL",

            "CD_SETOR_FINAL",

            "CONFIANCA"

        ]

    ],

    on="CHAVE_LOCAL",

    how="left"

)



final["TEM_SETOR"] = (

    final["CD_SETOR_FINAL"]
    .notna()

)



# ============================================================
# SALVAR
# ============================================================


saida = os.path.join(

    RESULTADOS,

    "matricula_setor_preciso.csv"

)



final.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivo criado:")
print(saida)



print("\nResumo:")

print(
"Matrículas:",
len(final)
)


print(
"Com setor:",
final["TEM_SETOR"].sum()
)


print(
"Sem setor:",
(~final["TEM_SETOR"]).sum()
)


print(
"Setores:",
final["CD_SETOR_FINAL"].nunique()
)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim Código 94.")