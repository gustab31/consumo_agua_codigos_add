# ============================================================
# 30_fuzzy_endereco_setor_v1.py
#
# Recuperação CD_SETOR por similaridade fuzzy de endereço
#
# ============================================================


import pandas as pd
import re
import unicodedata
import time
import os


from rapidfuzz import process, fuzz



inicio = time.time()


print("="*60)
print("FUZZY MATCHING ENDEREÇO + BAIRRO + CEP")
print("="*60)



ENTRADA = (
    "resultados/"
    "base_residencial_setor_conflitos_resolvidos_v1.csv"
)


SAIDA = (
    "resultados/"
    "base_residencial_setor_fuzzy_v1.csv"
)


RESUMO = (
    "resultados/"
    "resumo_fuzzy_setor_v1.csv"
)



# ============================================================
# LEITURA
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



if "CD_SETOR" not in df.columns:

    df["CD_SETOR"] = None



# ============================================================
# NORMALIZAÇÃO
# ============================================================


def normalizar(texto):

    if pd.isna(texto):

        return ""


    texto = str(texto).upper()


    texto = (

        unicodedata

        .normalize(

            "NFKD",

            texto

        )

        .encode(

            "ASCII",

            "ignore"

        )

        .decode()

    )


    texto = re.sub(

        r"\d+",

        "",

        texto

    )


    texto = re.sub(

        r"[^A-Z]",

        "",

        texto

    )


    return texto



def normalizar_cep(cep):

    if pd.isna(cep):

        return ""


    return re.sub(

        r"\D",

        "",

        str(cep)

    )



# ============================================================
# CHAVES
# ============================================================


print("\nCriando chaves...")


df["RUA_FUZZY"] = (

    df["Endereco"]

    .apply(normalizar)

)


df["BAIRRO_FUZZY"] = (

    df["Bairro"]

    .apply(normalizar)

)


df["CEP_FUZZY"] = (

    df["CEP"]

    .apply(normalizar_cep)

)



# ============================================================
# BASE REFERÊNCIA
# ============================================================


referencia = df[

    df["CD_SETOR"]

    .notna()

].copy()



print(

    "Referências:",

    len(referencia)

)



# chave composta

referencia["CHAVE"] = (

    referencia["RUA_FUZZY"]

    + "_"

    + referencia["BAIRRO_FUZZY"]

    + "_"

    + referencia["CEP_FUZZY"]

)



mapa_setor = (

    referencia

    .groupby("CHAVE")["CD_SETOR"]

    .unique()

)



chaves = list(

    mapa_setor.index

)



# ============================================================
# PROCESSAMENTO
# ============================================================


print("\nComparando endereços...")


novos = 0

processados = 0



for idx,row in df.iterrows():


    if pd.notna(row["CD_SETOR"]):

        continue



    chave_busca = (

        row["RUA_FUZZY"]

        + "_"

        + row["BAIRRO_FUZZY"]

        + "_"

        + row["CEP_FUZZY"]

    )



    # sem rua não compara

    if len(row["RUA_FUZZY"]) < 5:

        continue



    resultado = process.extractOne(

        chave_busca,

        chaves,

        scorer=fuzz.ratio

    )


    if resultado is None:

        continue



    melhor_chave, score, _ = resultado



    # somente alta confiança

    if score >= 90:


        setores = mapa_setor[melhor_chave]


        if len(setores) == 1:


            df.at[

                idx,

                "CD_SETOR"

            ] = setores[0]


            df.at[

                idx,

                "metodo_setor"

            ] = "fuzzy_endereco"


            novos += 1



    processados += 1



    if processados % 5000 == 0:

        print(

            "Processados:",

            processados

        )



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

        "novos_fuzzy",

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