# ============================================================
# 32_logradouro_dominante_setor_v1.py
#
# Propagação CD_SETOR por logradouro dominante
#
# ============================================================


import pandas as pd
import re
import unicodedata
import time


inicio = time.time()


print("="*60)
print("PROPAGAÇÃO POR LOGRADOURO DOMINANTE")
print("="*60)



ENTRADA = (
    "resultados/"
    "base_residencial_setor_fuzzy_semcep_v1.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_logradouro_dominante_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_logradouro_dominante_v1.csv"
)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base...")


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)


print(df.shape)



if "CD_SETOR" not in df.columns:

    df["CD_SETOR"] = None



# ============================================================
# NORMALIZAÇÃO
# ============================================================


def normalizar(txt):

    if pd.isna(txt):

        return ""


    txt = str(txt).upper()


    txt = (

        unicodedata

        .normalize(

            "NFKD",

            txt

        )

        .encode(

            "ASCII",

            "ignore"

        )

        .decode()

    )


    txt = re.sub(

        r"\d+",

        "",

        txt

    )


    txt = re.sub(

        r"[^A-Z]",

        "",

        txt

    )


    return txt



print("\nCriando chave logradouro...")


df["RUA_DOM"] = (

    df["Endereco"]

    .apply(normalizar)

)


df["BAIRRO_DOM"] = (

    df["Bairro"]

    .apply(normalizar)

)



# ============================================================
# REFERÊNCIA
# ============================================================


ref = df[

    df["CD_SETOR"]

    .notna()

].copy()



print(

    "Registros com setor:",

    len(ref)

)



# ============================================================
# DISTRIBUIÇÃO POR RUA
# ============================================================


print("\nCalculando domínio...")


dist = (

    ref

    .groupby(

        [

            "RUA_DOM",

            "BAIRRO_DOM",

            "CD_SETOR"

        ]

    )

    .size()

    .reset_index(

        name="qtd"

    )

)



totais = (

    dist

    .groupby(

        [

            "RUA_DOM",

            "BAIRRO_DOM"

        ]

    )["qtd"]

    .sum()

    .reset_index(

        name="total"

    )

)



dist = dist.merge(

    totais,

    on=[

        "RUA_DOM",

        "BAIRRO_DOM"

    ]

)



dist["percentual"] = (

    dist["qtd"]

    /

    dist["total"]

)



# pega maior setor por rua

dominante = (

    dist

    .sort_values(

        "percentual",

        ascending=False

    )

    .drop_duplicates(

        [

            "RUA_DOM",

            "BAIRRO_DOM"

        ]

    )

)



# regras de segurança

dominante = dominante[

    (dominante["total"] >= 5)

    &

    (dominante["percentual"] >= 0.90)

]



print(

    "Logradouros dominantes:",

    len(dominante)

)



mapa = dominante.set_index(

    [

        "RUA_DOM",

        "BAIRRO_DOM"

    ]

)["CD_SETOR"]



# ============================================================
# APLICAR
# ============================================================


print("\nTransferindo...")


novos = 0



for idx,row in df.iterrows():


    if pd.notna(row["CD_SETOR"]):

        continue



    chave = (

        row["RUA_DOM"],

        row["BAIRRO_DOM"]

    )


    if chave in mapa.index:


        df.at[

            idx,

            "CD_SETOR"

        ] = mapa[chave]


        df.at[

            idx,

            "metodo_setor"

        ] = "logradouro_dominante"


        novos += 1



# ============================================================
# RESUMO
# ============================================================


total = len(df)


com_setor = (

    df["CD_SETOR"]

    .notna()

    .sum()

)



resumo = pd.DataFrame({

    "indicador":[

        "total",

        "com_CD_SETOR",

        "sem_CD_SETOR",

        "novos_logradouro",

        "percentual"

    ],

    "valor":[

        total,

        com_setor,

        total-com_setor,

        novos,

        round(

            com_setor /

            total *

            100,

            2

        )

    ]

})



# ============================================================
# SALVAR
# ============================================================


df.to_csv(

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