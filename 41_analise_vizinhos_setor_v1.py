# ============================================================
# 41_analise_vizinhos_setor_v2.py
#
# ANALISE POTENCIAL POR LOGRADOURO COM SETOR CONHECIDO
#
# ============================================================


import pandas as pd
import unicodedata
import time


inicio = time.time()


print("="*60)
print("ANALISE LOGRADOURO COM CD_SETOR - V2")
print("="*60)


ENTRADA = (
    "resultados/"
    "base_residencial_setor_geocode_fila_v1.csv"
)


SAIDA = (
    "resultados/"
    "analise_potencial_logradouro_setor_v2.csv"
)


RESUMO = (
    "resultados/"
    "resumo_potencial_logradouro_setor_v2.csv"
)



def normalizar(x):

    if pd.isna(x):
        return ""

    x = str(x).upper().strip()

    x = unicodedata.normalize(
        "NFKD",
        x
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    return " ".join(x.split())



print("\nLendo base...")


df = pd.read_csv(
    ENTRADA,
    low_memory=False
)


print("Shape:", df.shape)



# identificar endereço

if "Endereco" in df.columns:
    col_end = "Endereco"

elif "endereco" in df.columns:
    col_end = "endereco"

else:
    raise Exception("Coluna endereco não encontrada")



if "Bairro" in df.columns:
    col_bairro = "Bairro"

elif "bairro" in df.columns:
    col_bairro = "bairro"

else:
    raise Exception("Coluna bairro não encontrada")



if "CD_SETOR" not in df.columns:
    raise Exception("CD_SETOR ausente")



print("\nCriando chave logradouro...")


df["logradouro_key"] = (

    df[col_end]

    .apply(normalizar)

)



com = df[

    df["CD_SETOR"].notna()

].copy()



sem = df[

    df["CD_SETOR"].isna()

].copy()



print(
    "Com setor:",
    len(com)
)


print(
    "Sem setor:",
    len(sem)
)



print("\nCalculando setores dominantes...")


dom = (

    com

    .groupby(

        [

            "logradouro_key",

            "CD_SETOR"

        ]

    )

    .size()

    .reset_index(

        name="qtd"

    )

)



tot = (

    dom

    .groupby(

        "logradouro_key"

    )

    ["qtd"]

    .sum()

    .reset_index(

        name="total"

    )

)



dom = dom.merge(

    tot,

    on="logradouro_key"

)



dom["percentual"] = (

    dom["qtd"]

    /

    dom["total"]

)



dominante = (

    dom

    .sort_values(

        "qtd",

        ascending=False

    )

    .drop_duplicates(

        "logradouro_key"

    )

)



dominante = dominante[

    dominante["percentual"] >= 0.80

]



print(

    "Logradouros dominantes:",

    len(dominante)

)



print("\nCalculando potencial...")


teste = sem.merge(

    dominante[

        [

            "logradouro_key",

            "CD_SETOR",

            "percentual"

        ]

    ],

    on="logradouro_key",

    how="inner",

    suffixes=(

        "",

        "_NOVO"

    )

)



# setor encontrado vem como CD_SETOR_NOVO

teste.rename(

    columns={

        "CD_SETOR_NOVO":

        "CD_SETOR_PROP"

    },

    inplace=True

)



resumo = pd.DataFrame({

    "indicador":[

        "total",

        "sem_setor",

        "logradouro_dominante",

        "potencial"

    ],

    "valor":[

        len(df),

        len(sem),

        len(dominante),

        len(teste)

    ]

})



print("\n")

print("="*60)

print("RESULTADO")

print("="*60)

print(resumo)



print("\nAmostra:")


print(

    teste[

        [

            col_end,

            col_bairro,

            "CD_SETOR_PROP",

            "percentual"

        ]

    ]

    .head(30)

)



teste.to_csv(

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