# ============================================================
# 46_propagacao_setor_controlada_v1.py
#
# PROPAGACAO CONTROLADA CD_SETOR
# LOGRADOURO + BAIRRO
#
# ============================================================

import pandas as pd
import os
import time


inicio = time.time()


print("="*70)
print("PROPAGACAO SETOR CONTROLADA - V1")
print("="*70)



entrada = "resultados/base_residencial_setor_geocode_fila_v1.csv"


saida = "resultados/base_residencial_setor_propagacao_controlada_v1.csv"

resumo = "resultados/resumo_propagacao_controlada_v1.csv"



print("\nLendo base...")


df = pd.read_csv(

    entrada,

    low_memory=False

)



print("Shape:", df.shape)



# ------------------------------------------------------------
# localizar coluna setor
# ------------------------------------------------------------


if "CD_SETOR" not in df.columns:

    raise Exception(

        "CD_SETOR não encontrado"

    )



print(

    "Com setor antes:",

    df["CD_SETOR"].notna().sum()

)



# ------------------------------------------------------------
# criar chave logradouro
# ------------------------------------------------------------


print("\nCriando chave...")


def limpar(x):

    if pd.isna(x):

        return ""

    return (

        str(x)

        .upper()

        .strip()

    )



df["chave_logradouro_setor"] = (

    df["Endereco"]

    .apply(limpar)

    +

    "|"

    +

    df["Bairro"]

    .apply(limpar)

)



# ------------------------------------------------------------
# referências confiáveis
# ------------------------------------------------------------


referencia = df[

    df["CD_SETOR"].notna()

].copy()



print(

    "Registros referência:",

    len(referencia)

)



grupo = (

    referencia

    .groupby(

        "chave_logradouro_setor"

    )

    ["CD_SETOR"]

    .agg(

        [

            "count",

            lambda x: x.value_counts().index[0],

            lambda x: x.value_counts().iloc[0] / len(x)

        ]

    )

    .reset_index()

)



grupo.columns = [

    "chave_logradouro_setor",

    "total",

    "CD_SETOR_PROP",

    "percentual"

]



# ------------------------------------------------------------
# filtros de segurança
# ------------------------------------------------------------


dominante = grupo[

    (grupo["total"] >= 2)

    &

    (grupo["percentual"] >= 0.90)

]



print(

    "Logradouros dominantes:",

    len(dominante)

)



# ------------------------------------------------------------
# aplicar somente sem setor
# ------------------------------------------------------------


sem = df[

    df["CD_SETOR"].isna()

].copy()



print(

    "Sem setor:",

    len(sem)

)



sem = sem.merge(

    dominante[

        [

            "chave_logradouro_setor",

            "CD_SETOR_PROP",

            "percentual"

        ]

    ],

    on="chave_logradouro_setor",

    how="left"

)



transferidos = sem["CD_SETOR_PROP"].notna().sum()



print(

    "Novos potenciais:",

    transferidos

)



# aplicar


idx = sem[

    sem["CD_SETOR_PROP"].notna()

].index



sem.loc[

    idx,

    "CD_SETOR"

] = sem.loc[

    idx,

    "CD_SETOR_PROP"

]



sem["origem_CD_SETOR"] = "propagacao_controlada"



# ------------------------------------------------------------
# juntar novamente
# ------------------------------------------------------------


com = df[

    df["CD_SETOR"].notna()

].copy()


com["origem_CD_SETOR"] = "original"



resultado = pd.concat(

    [

        com,

        sem

    ],

    ignore_index=True

)



# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------


resultado.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



res = pd.DataFrame({

    "indicador":[

        "total",

        "com_setor_antes",

        "novos_propagacao",

        "com_setor_depois",

        "sem_setor",

        "percentual"

    ],

    "valor":[

        len(df),

        df["CD_SETOR"].notna().sum(),

        transferidos,

        resultado["CD_SETOR"].notna().sum(),

        resultado["CD_SETOR"].isna().sum(),

        round(

            resultado["CD_SETOR"].notna().mean()*100,

            2

        )

    ]

})


res.to_csv(

    resumo,

    index=False,

    encoding="utf-8-sig"

)



print("\n")

print("="*70)

print("RESULTADO FINAL")

print("="*70)


print(res)



print("\nArquivos:")

print(saida)

print(resumo)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim.")