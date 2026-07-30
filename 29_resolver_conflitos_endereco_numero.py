# ============================================================
# 29_resolver_conflitos_endereco_numero.py
#
# Resolver conflitos CD_SETOR usando número do imóvel
#
# ============================================================


import pandas as pd
import re
import time
import os


inicio = time.time()


print("="*60)
print("RESOLVENDO CONFLITOS DE CD_SETOR POR NUMERO")
print("="*60)



ENTRADA = (
    "resultados/"
    "base_residencial_setor_similaridade_v1.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_conflitos_resolvidos_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_conflitos_resolvidos_v1.csv"
)



# ============================================================
# LEITURA
# ============================================================


df = pd.read_csv(

    ENTRADA,

    low_memory=False

)


print("\nBase:")

print(df.shape)



# ============================================================
# FUNÇÕES
# ============================================================


def extrair_numero(endereco):

    if pd.isna(endereco):

        return None


    texto = str(endereco)


    encontrados = re.findall(

        r"\d+",

        texto

    )


    if encontrados:

        return int(encontrados[-1])


    return None



def limpar_rua(endereco):

    if pd.isna(endereco):

        return ""


    texto = str(endereco).upper()


    texto = re.sub(

        r"\d+",

        "",

        texto

    )


    texto = re.sub(

        r"[^A-ZÁÉÍÓÚÃÕÇ ]",

        "",

        texto

    )


    texto = re.sub(

        r"\s+",

        " ",

        texto

    )


    return texto.strip()



# ============================================================
# CHAVES
# ============================================================


print("\nCriando chaves...")


df["RUA_BASE"] = (

    df["Endereco"]

    .apply(limpar_rua)

)


df["NUMERO"] = (

    df["Endereco"]

    .apply(extrair_numero)

)



# ============================================================
# REFERÊNCIA
# ============================================================


referencia = df[

    df["CD_SETOR"]

    .notna()

].copy()



print(

    "Com setor:",

    len(referencia)

)



# ============================================================
# IDENTIFICAR CONFLITOS
# ============================================================


grupos = (

    referencia

    .groupby(

        [

            "RUA_BASE",

            "Bairro"

        ]

    )["CD_SETOR"]

    .nunique()

)



conflitos = grupos[

    grupos > 1

].index



print(

    "Grupos conflitantes:",

    len(conflitos)

)



# ============================================================
# RESOLUÇÃO
# ============================================================


novos = 0


for idx,row in df.iterrows():


    if pd.notna(row["CD_SETOR"]):

        continue



    chave = (

        row["RUA_BASE"],

        row["Bairro"]

    )


    if chave not in conflitos:

        continue



    numero = row["NUMERO"]


    if pd.isna(numero):

        continue



    candidatos = referencia[

        (referencia["RUA_BASE"] == chave[0])

        &

        (referencia["Bairro"] == chave[1])

        &

        (referencia["NUMERO"].notna())

    ].copy()



    if len(candidatos) == 0:

        continue



    candidatos["DIST_NUM"] = (

        candidatos["NUMERO"]

        -

        numero

    ).abs()



    melhor = candidatos.sort_values(

        "DIST_NUM"

    ).iloc[0]



    # verifica se é realmente próximo

    if melhor["DIST_NUM"] <= 20:


        df.at[

            idx,

            "CD_SETOR"

        ] = melhor["CD_SETOR"]



        df.at[

            idx,

            "metodo_setor"

        ] = "conflito_numero"



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

        "com_setor",

        "sem_setor",

        "novos_resolvidos",

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