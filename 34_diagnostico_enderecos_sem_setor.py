# ============================================================
# 34_diagnostico_enderecos_sem_setor.py
#
# Diagnóstico de endereços sem setor censitário
#
# Unidade:
# SETOR CENSITÁRIO IBGE
#
# ============================================================


import pandas as pd
import os
import time


inicio = time.time()


print("="*60)
print("DIAGNÓSTICO ENDEREÇOS SEM CD_SETOR")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ENTRADA = (
    "resultados/"
    "base_residencial_setor_espacial_v3.csv"
)


SAIDA = (
    "resultados/"
    "diagnostico_enderecos_sem_setor_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_diagnostico_sem_setor_v1.csv"
)



# ============================================================
# LER BASE
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Shape:",

    df.shape

)



# ============================================================
# IDENTIFICAR SEM SETOR
# ============================================================


if "CD_SETOR" not in df.columns:

    raise Exception(
        "Coluna CD_SETOR não encontrada"
    )



sem_setor = df[

    df["CD_SETOR"].isna()

].copy()



print(

    "Sem CD_SETOR:",

    len(sem_setor)

)



# ============================================================
# NORMALIZAR NOMES
# ============================================================


def achar_coluna(lista):

    for c in lista:

        if c in sem_setor.columns:

            return c

    return None



endereco = achar_coluna([

    "endereco",

    "Endereco",

    "ENDERECO"

])



bairro = achar_coluna([

    "bairro",

    "Bairro",

    "BAIRRO"

])



cep = achar_coluna([

    "cep",

    "CEP",

    "Cep"

])



if endereco is None:

    raise Exception(
        "Coluna endereço não encontrada"
    )



if bairro is None:

    raise Exception(
        "Coluna bairro não encontrada"
    )



# ============================================================
# AGRUPAMENTO
# ============================================================


print("\nAgrupando endereços...")


campos = [

    endereco,

    bairro

]


if cep:

    campos.append(cep)



grupo = (

    sem_setor

    .groupby(campos)

    .size()

    .reset_index(

        name="total_matriculas"

    )

)



grupo = grupo.sort_values(

    "total_matriculas",

    ascending=False

)



grupo["prioridade"] = "BAIXA"



grupo.loc[

    grupo["total_matriculas"] >= 20,

    "prioridade"

] = "ALTA"



grupo.loc[

    grupo["total_matriculas"] >= 50,

    "prioridade"

] = "MUITO_ALTA"



# ============================================================
# RESUMO
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "matriculas_sem_setor",

        "enderecos_unicos_sem_setor",

        "potencial_muito_alta",

        "potencial_alta"

    ],

    "valor":[

        len(sem_setor),

        len(grupo),

        grupo.loc[

            grupo.prioridade=="MUITO_ALTA",

            "total_matriculas"

        ].sum(),

        grupo.loc[

            grupo.prioridade=="ALTA",

            "total_matriculas"

        ].sum()

    ]

})



# ============================================================
# SALVAR
# ============================================================


grupo.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



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



print("\nTop 20:")

print(

    grupo.head(20)

)



print("\nArquivos:")

print(SAIDA)

print(RESUMO)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim.")