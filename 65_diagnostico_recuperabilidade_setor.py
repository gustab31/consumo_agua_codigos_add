# ============================================================
# 65_diagnostico_recuperabilidade_setor.py
#
# Diagnóstico dos registros sem setor
#
# Não faz inferência.
# Mede possibilidade de recuperação.
#
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO DE RECUPERABILIDADE DE SETOR")
print("="*70)


ARQUIVO = (
    "resultados/"
    "base_setor_final_CEP.csv"
)


SAIDA = (
    "resultados/"
    "diagnostico_recuperabilidade_setor.csv"
)



# ------------------------------------------------------------
# normalização
# ------------------------------------------------------------

def normalizar(valor):

    if pd.isna(valor):

        return ""

    valor = str(valor).upper()


    valor = (
        unicodedata
        .normalize(
            "NFKD",
            valor
        )
        .encode(
            "ASCII",
            "ignore"
        )
        .decode(
            "ASCII"
        )
    )


    valor = re.sub(
        r"[^A-Z0-9]",
        " ",
        valor
    )


    valor = re.sub(
        r"\s+",
        " ",
        valor
    )


    return valor.strip()



# ------------------------------------------------------------
# leitura
# ------------------------------------------------------------

print("\nLendo base...")


df = pd.read_csv(

    ARQUIVO,

    low_memory=False

)



print(
    "Registros:",
    len(df)
)



# ------------------------------------------------------------
# identificar setor
# ------------------------------------------------------------

if "CD_SETOR_FINAL" in df.columns:

    campo_setor = "CD_SETOR_FINAL"

elif "CD_SETOR" in df.columns:

    campo_setor = "CD_SETOR"

else:

    raise Exception(
        "Campo de setor não encontrado"
    )



print(
    "Campo setor:",
    campo_setor
)



# ------------------------------------------------------------
# separar
# ------------------------------------------------------------

sem_setor = df[

    df[campo_setor].isna()

].copy()



com_setor = df[

    df[campo_setor].notna()

].copy()



print(
    "Com setor:",
    len(com_setor)
)


print(
    "Sem setor:",
    len(sem_setor)
)



# ------------------------------------------------------------
# normalizar campos
# ------------------------------------------------------------

print("\nNormalizando...")


for tabela in [

    com_setor,

    sem_setor

]:

    for campo in [

        "Endereco",

        "Bairro",

        "CEP"

    ]:

        if campo in tabela.columns:

            tabela[campo+"_NORM"] = (

                tabela[campo]

                .apply(normalizar)

            )



# ------------------------------------------------------------
# criar referências
# ------------------------------------------------------------

print("\nCriando referências...")


# endereço + bairro

regra_end_bairro = (

    com_setor

    .groupby(

        [

            "Endereco_NORM",

            "Bairro_NORM"

        ]

    )[campo_setor]

    .nunique()

    .reset_index(name="N_SETOR")

)



# CEP

regra_cep = (

    com_setor

    .groupby(

        "CEP_NORM"

    )[campo_setor]

    .nunique()

    .reset_index(name="N_SETOR")

)



# Bairro

regra_bairro = (

    com_setor

    .groupby(

        "Bairro_NORM"

    )[campo_setor]

    .nunique()

    .reset_index(name="N_SETOR")

)



# ------------------------------------------------------------
# análise
# ------------------------------------------------------------

print("\nAnalisando...")


resultados = []



resultados.append({

    "indicador":

    "sem_setor_total",

    "quantidade":

    len(sem_setor)

})



for campo in [

    "CEP",

    "Bairro",

    "Endereco"

]:

    if campo in sem_setor.columns:

        resultados.append({

            "indicador":

            campo+"_preenchido",

            "quantidade":

            int(

                sem_setor[campo]

                .notna()

                .sum()

            )

        })



# ------------------------------------------------------------
# endereço bairro
# ------------------------------------------------------------

teste_end = sem_setor.merge(

    regra_end_bairro,

    on=[

        "Endereco_NORM",

        "Bairro_NORM"

    ],

    how="left"

)



resultados.append({

    "indicador":

    "endereco_bairro_com_referencia",

    "quantidade":

    int(

        teste_end["N_SETOR"]

        .notna()

        .sum()

    )

})


resultados.append({

    "indicador":

    "endereco_bairro_unico",

    "quantidade":

    int(

        (

            teste_end["N_SETOR"]

            == 1

        )

        .sum()

    )

})



# ------------------------------------------------------------
# CEP
# ------------------------------------------------------------

teste_cep = sem_setor.merge(

    regra_cep,

    on="CEP_NORM",

    how="left"

)



resultados.append({

    "indicador":

    "cep_com_referencia",

    "quantidade":

    int(

        teste_cep["N_SETOR"]

        .notna()

        .sum()

    )

})


resultados.append({

    "indicador":

    "cep_unico",

    "quantidade":

    int(

        (

            teste_cep["N_SETOR"]

            == 1

        )

        .sum()

    )

})



# ------------------------------------------------------------
# bairro
# ------------------------------------------------------------

teste_bairro = sem_setor.merge(

    regra_bairro,

    on="Bairro_NORM",

    how="left"

)



resultados.append({

    "indicador":

    "bairro_com_referencia",

    "quantidade":

    int(

        teste_bairro["N_SETOR"]

        .notna()

        .sum()

    )

})


# ------------------------------------------------------------
# salvar
# ------------------------------------------------------------

resultado = pd.DataFrame(

    resultados

)



print("\n")
print("="*70)
print("RESULTADO")
print("="*70)


print(resultado)



os.makedirs(

    "resultados",

    exist_ok=True

)



resultado.to_csv(

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