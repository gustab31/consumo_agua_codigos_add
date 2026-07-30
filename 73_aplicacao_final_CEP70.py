# ============================================================
# DIAGNOSTICO_CEP_SEM_SETOR.py
# Verifica sobreposição de CEP entre registros com e sem setor
# ============================================================

import pandas as pd
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO CEP - COBERTURA DE RECUPERAÇÃO")
print("="*70)



ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)



SAIDA = (
    "resultados/"
    "diagnostico_CEP_sem_setor.csv"
)



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")


df = pd.read_csv(

    ARQUIVO,

    low_memory=False,

    dtype=str

)



print(

    "Registros:",

    len(df)

)



# ------------------------------------------------------------
# limpeza
# ------------------------------------------------------------

df["CD_SETOR_FINAL"] = (

    df["CD_SETOR_FINAL"]

    .replace(

        [

            "nan",

            "None",

            "",

            None

        ],

        pd.NA

    )

)



df["CEP_NORM"] = (

    df["CEP"]

    .astype(str)

    .str.replace(

        r"\D",

        "",

        regex=True

    )

)



# ------------------------------------------------------------
# separar
# ------------------------------------------------------------

com = df[

    df["CD_SETOR_FINAL"].notna()

]


sem = df[

    df["CD_SETOR_FINAL"].isna()

]



print("\nCom setor:", len(com))

print("Sem setor:", len(sem))



# ------------------------------------------------------------
# CEPs
# ------------------------------------------------------------

ceps_com = set(

    com["CEP_NORM"]

)



ceps_sem = set(

    sem["CEP_NORM"]

)



intersecao = (

    ceps_com

    &

    ceps_sem

)



print("\nCEPs com setor:", len(ceps_com))

print("CEPs sem setor:", len(ceps_sem))

print("CEPs em comum:", len(intersecao))



# ------------------------------------------------------------
# impacto
# ------------------------------------------------------------

registros_recuperaveis = sem[

    sem["CEP_NORM"].isin(

        intersecao

    )

]



print(

    "\nRegistros sem setor com CEP conhecido:",

    len(registros_recuperaveis)

)



# salvar

resumo = pd.DataFrame({

    "indicador":[

        "ceps_com_setor",

        "ceps_sem_setor",

        "ceps_em_comum",

        "registros_sem_setor_com_CEP_compartilhado"

    ],

    "valor":[

        len(ceps_com),

        len(ceps_sem),

        len(intersecao),

        len(registros_recuperaveis)

    ]

})



resumo.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



print("\nArquivo:")

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