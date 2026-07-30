# ============================================================
# 23_propagar_setor_endereco_v2.py
#
# Propaga CD_SETOR por endereço
#
# ============================================================


import pandas as pd
import os
import time


inicio = time.time()


print("="*60)
print("PROPAGANDO CD_SETOR POR ENDEREÇO - V2")
print("="*60)



ARQ_BASE = (
    "resultados/"
    "base_residencial_setor_endereco_cep_v3.csv"
)


ARQ_SPATIAL = (
    "resultados/"
    "resultado_spatial_prioridade_alta_v9.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_propagado_v2.csv"
)


RESUMO = (
    "resultados/"
    "resumo_propagacao_setor_v2.csv"
)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base...")


base = pd.read_csv(
    ARQ_BASE,
    low_memory=False
)


print(
    base.shape
)



print("\nLendo espacial...")


spatial = pd.read_csv(
    ARQ_SPATIAL,
    low_memory=False
)



# ============================================================
# IDENTIFICAR COLUNAS
# ============================================================


def achar_coluna(df, nomes):

    for n in nomes:

        if n in df.columns:

            return n

    return None



end_base = achar_coluna(
    base,
    [
        "endereco",
        "Endereco"
    ]
)


bairro_base = achar_coluna(
    base,
    [
        "bairro",
        "Bairro"
    ]
)



end_spatial = achar_coluna(
    spatial,
    [
        "endereco",
        "Endereco"
    ]
)


bairro_spatial = achar_coluna(
    spatial,
    [
        "bairro",
        "Bairro"
    ]
)



print("\nColunas encontradas:")

print(
    "Base:",
    end_base,
    bairro_base
)


print(
    "Spatial:",
    end_spatial,
    bairro_spatial
)



if None in [
    end_base,
    bairro_base,
    end_spatial,
    bairro_spatial
]:

    raise Exception(
        "Não encontrou coluna de endereço ou bairro"
    )



# ============================================================
# CRIAR CHAVES TEMPORÁRIAS
# ============================================================


base["_END_CHAVE"] = (

    base[end_base]
    .astype(str)
    .str.upper()
    .str.strip()

)


base["_BAIRRO_CHAVE"] = (

    base[bairro_base]
    .astype(str)
    .str.upper()
    .str.strip()

)



spatial["_END_CHAVE"] = (

    spatial[end_spatial]
    .astype(str)
    .str.upper()
    .str.strip()

)


spatial["_BAIRRO_CHAVE"] = (

    spatial[bairro_spatial]
    .astype(str)
    .str.upper()
    .str.strip()

)



# ============================================================
# MAPA DE SETORES
# ============================================================


mapa = spatial[

    spatial["CD_SETOR"].notna()

][

    [

        "_END_CHAVE",

        "_BAIRRO_CHAVE",

        "CD_SETOR"

    ]

].copy()



print(
    "\nEndereços com setor:",
    len(mapa)
)



# remover conflitos

conf = (

    mapa

    .groupby(
        [
            "_END_CHAVE",
            "_BAIRRO_CHAVE"
        ]
    )

    ["CD_SETOR"]

    .nunique()

)



conflitos = conf[conf > 1]


print(
    "Conflitos:",
    len(conflitos)
)



mapa = (

    mapa

    .groupby(
        [
            "_END_CHAVE",
            "_BAIRRO_CHAVE"
        ]
    )

    .filter(
        lambda x:
        x["CD_SETOR"].nunique()==1
    )

)



mapa = mapa.drop_duplicates()



# ============================================================
# MERGE
# ============================================================


antes = base["CD_SETOR"].notna().sum()



print("\nTransferindo...")


base = base.merge(

    mapa,

    on=[

        "_END_CHAVE",

        "_BAIRRO_CHAVE"

    ],

    how="left"

)



# preencher

if "CD_SETOR_y" in base.columns:


    base["CD_SETOR"] = (

        base["CD_SETOR_x"]

        .fillna(

            base["CD_SETOR_y"]

        )

    )


    base.drop(

        columns=[

            "CD_SETOR_x",

            "CD_SETOR_y"

        ],

        inplace=True

    )



# ============================================================
# MÉTODO
# ============================================================


if "metodo_setor" not in base.columns:

    base["metodo_setor"] = ""


if "confianca" not in base.columns:

    base["confianca"] = ""



novo = (

    base["metodo_setor"]
    ==""

) & (

    base["CD_SETOR"]
    .notna()

)



base.loc[
    novo,
    "metodo_setor"
] = "endereco_geocodificado"



base.loc[
    novo,
    "confianca"
] = "media_alta"



# limpar

base.drop(

    columns=[

        "_END_CHAVE",

        "_BAIRRO_CHAVE"

    ],

    inplace=True

)



depois = base["CD_SETOR"].notna().sum()



# ============================================================
# SALVAR
# ============================================================


base.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



resumo = pd.DataFrame({

    "indicador":[

        "antes",

        "depois",

        "novos",

        "percentual"

    ],

    "valor":[

        antes,

        depois,

        depois-antes,

        round(
            depois/len(base)*100,
            2
        )

    ]

})


resumo.to_csv(

    RESUMO,

    index=False,

    encoding="utf-8-sig"

)



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(resumo)



print("\nSalvo:")

print(SAIDA)


print("\nTempo:")

print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")