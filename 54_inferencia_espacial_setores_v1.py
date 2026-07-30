# ============================================================
# 54_inferencia_espacial_setores_v1.py
#
# Inferência espacial de setores censitários
#
# Usa registros já identificados para inferir setores
# para registros sem CD_SETOR.
#
# Métodos:
# 1 - Mesmo CEP dominante
# 2 - Mesmo bairro + CEP dominante
#
# Saída:
# CD_SETOR_PROVAVEL
# metodo_atribuicao
# confianca
#
# ============================================================


import os
import time
import pandas as pd
import geopandas as gpd


inicio = time.time()


print("="*70)
print("INFERÊNCIA ESPACIAL DE SETORES CENSITÁRIOS")
print("="*70)


# ------------------------------------------------------------
# arquivos
# ------------------------------------------------------------

ENTRADA = (
    "resultados/"
    "base_residencial_setor_logradouro_normalizado_v3.csv"
)


SAIDA = (
    "resultados/"
    "base_inferencia_espacial_setor_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_inferencia_espacial_setor_v1.csv"
)


# procurar automaticamente o shapefile

SHAPE = None


possiveis = [

    "joinville_setores_mapa.shp",

    "Joinville_setores.shp",

    "resultados_02/joinville_setores_mapa.shp",

    "resultados_03/joinville_setores_mapa.shp"

]


for arq in possiveis:

    if os.path.exists(arq):

        SHAPE = arq
        break


if SHAPE is None:

    raise FileNotFoundError(
        "Nenhum shapefile de setores encontrado"
    )


print("\nShape encontrado:")
print(SHAPE)



# ------------------------------------------------------------
# leitura base
# ------------------------------------------------------------


print("\nLendo cadastro...")


df = pd.read_csv(
    ENTRADA,
    low_memory=False
)


print(
    "Registros:",
    len(df)
)



# ------------------------------------------------------------
# preparar campos
# ------------------------------------------------------------


df["CD_SETOR"] = (

    df["CD_SETOR"]

    .fillna("")

    .astype(str)

    .str.strip()

)



for c in [

    "CEP",
    "Bairro"

]:

    if c not in df.columns:

        df[c] = ""


    df[c] = (

        df[c]

        .fillna("")

        .astype(str)

        .str.upper()

        .str.strip()

    )



# novas colunas sempre texto

df["CD_SETOR_PROVAVEL"] = ""

df["metodo_atribuicao"] = ""

df["confianca"] = ""



# ------------------------------------------------------------
# separar
# ------------------------------------------------------------


com = df[
    df["CD_SETOR"] != ""
].copy()


sem = df[
    df["CD_SETOR"] == ""
].copy()



print("\nCom setor:")
print(len(com))


print("Sem setor:")
print(len(sem))



# ------------------------------------------------------------
# REGRA 1
# CEP dominante
# ------------------------------------------------------------


print("\nCalculando CEP dominante...")


cep_ref = (

    com

    .groupby(
        [
            "CEP",
            "CD_SETOR"
        ]
    )

    .size()

    .reset_index(
        name="n"
    )

)



cep_total = (

    cep_ref

    .groupby("CEP")
    ["n"]

    .sum()

)



cep_ref["total"] = cep_ref["CEP"].map(
    cep_total
)



cep_ref["percentual"] = (

    cep_ref["n"]

    /

    cep_ref["total"]

)



cep_dominante = cep_ref[

    cep_ref["percentual"] >= 0.90

]



mapa_cep = (

    cep_dominante

    .sort_values(
        "percentual",
        ascending=False
    )

    .drop_duplicates(
        "CEP"
    )

    .set_index(
        "CEP"
    )

    ["CD_SETOR"]

)



novos_cep = 0



for idx,row in sem.iterrows():


    cep = row["CEP"]


    if cep in mapa_cep.index:


        sem.at[
            idx,
            "CD_SETOR_PROVAVEL"
        ] = str(
            mapa_cep.loc[cep]
        )


        sem.at[
            idx,
            "metodo_atribuicao"
        ] = "CEP_dominante"


        sem.at[
            idx,
            "confianca"
        ] = "MEDIA"


        novos_cep += 1



print(
    "Novos por CEP:",
    novos_cep
)



# ------------------------------------------------------------
# REGRA 2
# Bairro + CEP
# ------------------------------------------------------------


print("\nCalculando bairro + CEP...")


faltantes = sem[

    sem["CD_SETOR_PROVAVEL"] == ""

]



ref2 = (

    com

    .groupby(
        [
            "Bairro",
            "CEP",
            "CD_SETOR"
        ]
    )

    .size()

    .reset_index(
        name="n"
    )

)



ref2_total = (

    ref2

    .groupby(
        [
            "Bairro",
            "CEP"
        ]
    )

    ["n"]

    .sum()

)



ref2["total"] = (

    ref2

    .set_index(
        [
            "Bairro",
            "CEP"
        ]
    )

    .index

    .map(ref2_total)

)



ref2["percentual"] = (

    ref2["n"]

    /

    ref2["total"]

)



ref2 = ref2[

    ref2["percentual"] >= 0.90

]



mapa2 = (

    ref2

    .sort_values(
        "percentual",
        ascending=False
    )

    .drop_duplicates(
        [
            "Bairro",
            "CEP"
        ]
    )

    .set_index(
        [
            "Bairro",
            "CEP"
        ]
    )

    ["CD_SETOR"]

)



novos_bairro = 0



for idx,row in faltantes.iterrows():


    chave = (

        row["Bairro"],

        row["CEP"]

    )


    if chave in mapa2.index:


        sem.at[
            idx,
            "CD_SETOR_PROVAVEL"
        ] = str(
            mapa2.loc[chave]
        )


        sem.at[
            idx,
            "metodo_atribuicao"
        ] = "bairro_CEP_dominante"


        sem.at[
            idx,
            "confianca"
        ] = "ALTA"


        novos_bairro += 1



print(
    "Novos bairro+CEP:",
    novos_bairro
)



# ------------------------------------------------------------
# juntar
# ------------------------------------------------------------


resultado = pd.concat(
    [
        com,
        sem
    ],
    ignore_index=True
)



# ------------------------------------------------------------
# resumo
# ------------------------------------------------------------


novos_total = (

    resultado["CD_SETOR_PROVAVEL"]

    != ""

).sum()



resumo = pd.DataFrame(

    {

        "indicador":[

            "total",

            "com_setor_original",

            "sem_setor_original",

            "novas_inferencias"

        ],


        "valor":[

            len(resultado),

            len(com),

            len(sem),

            novos_total

        ]

    }

)



print("\n")
print("="*70)
print("RESULTADO FINAL")
print("="*70)


print(resumo)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------


os.makedirs(
    "resultados",
    exist_ok=True
)



resultado.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



resumo.to_csv(

    RESUMO,

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivos:")

print(SAIDA)

print(RESUMO)



print(
    "\nTempo:",
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")