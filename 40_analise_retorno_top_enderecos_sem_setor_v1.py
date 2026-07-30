# ============================================================
# 40_analise_retorno_top_enderecos_sem_setor_v1.py
#
# ANALISE DE RETORNO POTENCIAL DOS ENDERECOS SEM CD_SETOR
#
# ============================================================


import pandas as pd
import time


inicio = time.time()


print("="*60)
print("ANALISE RETORNO TOP ENDERECOS SEM CD_SETOR - V1")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================


ENTRADA = (
    "resultados/"
    "diagnostico_prioridade_sem_setor_v2.csv"
)


SAIDA = (
    "resultados/"
    "retorno_top_enderecos_sem_setor_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_retorno_top_enderecos_v1.csv"
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

    "Endereços avaliados:",

    len(df)

)



# ============================================================
# FILTRAR ALTA PRIORIDADE
# ============================================================


top = df[

    df["prioridade"].isin(

        [

            "MUITO_ALTA",

            "ALTA"

        ]

    )

].copy()



top = top.sort_values(

    "total_matriculas",

    ascending=False

)



print("\nEndereços prioritários:")

print(

    len(top)

)



# ============================================================
# CÁLCULO DE POTENCIAL
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "enderecos_muito_alta_alta",

        "matriculas_potenciais",

        "muito_alta",

        "alta"

    ],

    "valor":[

        len(top),

        top["total_matriculas"].sum(),

        (

            top["prioridade"]

            =="MUITO_ALTA"

        ).sum(),

        (

            top["prioridade"]

            =="ALTA"

        ).sum()

    ]

})



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)


print(resumo)



print("\nTOP ENDEREÇOS:")


print(

    top[

        [

            "Endereco",

            "Bairro",

            "total_matriculas",

            "prioridade"

        ]

    ]

)



# ============================================================
# SALVAR
# ============================================================


top.to_csv(

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



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim.")