# ============================================================
# 35_fila_geocode_prioridade_setor_v1.py
#
# Cria fila otimizada para geocodificação
# Objetivo:
# Recuperar CD_SETOR censitário
#
# ============================================================


import pandas as pd
import time
import os


inicio = time.time()


print("="*60)
print("FILA GEOCODIFICACAO PRIORIDADE SETOR CENSITARIO")
print("="*60)



ENTRADA = (
    "resultados/"
    "diagnostico_enderecos_sem_setor_v1.csv"
)


SAIDA = (
    "resultados/"
    "fila_geocode_setor_prioridade_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_fila_geocode_setor_v1.csv"
)



# ============================================================
# LER
# ============================================================


print("\nLendo diagnóstico...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)



print(

    "Endereços:",

    len(df)

)



# ============================================================
# LIMPEZA
# ============================================================


df["Endereco"] = (

    df["Endereco"]

    .astype(str)

)


df["Bairro"] = (

    df["Bairro"]

    .astype(str)

)



# ============================================================
# CRITÉRIOS
# ============================================================


df["prioridade_final"] = "BAIXA"



# prioridade pelo volume

df.loc[

    df["total_matriculas"] >= 10,

    "prioridade_final"

] = "MEDIA"



df.loc[

    df["total_matriculas"] >= 20,

    "prioridade_final"

] = "ALTA"



df.loc[

    df["total_matriculas"] >= 40,

    "prioridade_final"

] = "MUITO_ALTA"



# SN aumenta prioridade

mask_sn = (

    df["Endereco"]

    .str.upper()

    .str.contains(

        "SN",

        na=False

    )

)



df.loc[

    mask_sn &

    (df["prioridade_final"]=="BAIXA"),

    "prioridade_final"

] = "MEDIA"



# áreas rurais

mask_rural = (

    df["Bairro"]

    .str.upper()

    .str.contains(

        "RURAL|PIRABEIRABA|CUBATÃO|RIO BONITO",

        na=False

    )

)



df.loc[

    mask_rural &

    (df["prioridade_final"]=="MEDIA"),

    "prioridade_final"

] = "ALTA"



# ============================================================
# FILTRAR
# ============================================================


fila = df[

    df["prioridade_final"]

    .isin(

        [

            "MUITO_ALTA",

            "ALTA",

            "MEDIA"

        ]

    )

].copy()



fila = fila.sort_values(

    [

        "prioridade_final",

        "total_matriculas"

    ],

    ascending=[

        True,

        False

    ]

)



# ============================================================
# CONSULTA GEOCODE
# ============================================================


fila["consulta"] = (

    fila["Endereco"]

    + ", "

    +

    fila["Bairro"]

    + ", Joinville SC Brasil"

)



# ============================================================
# SALVAR
# ============================================================


fila.to_csv(

    SAIDA,

    index=False,

    encoding="utf-8-sig"

)



resumo = pd.DataFrame({

    "indicador":[

        "enderecos_fila",

        "matriculas_potenciais",

        "muito_alta",

        "alta",

        "media"

    ],

    "valor":[

        len(fila),

        fila["total_matriculas"].sum(),

        (

            fila.prioridade_final=="MUITO_ALTA"

        ).sum(),

        (

            fila.prioridade_final=="ALTA"

        ).sum(),

        (

            fila.prioridade_final=="MEDIA"

        ).sum()

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



print("\nTop 30:")

print(

    fila.head(30)

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