# ============================================================
# AUDITORIA DA GEOCODIFICACAO
# CAJ + CENSO
# ============================================================

import pandas as pd
import numpy as np
import os
import re
import time
import unicodedata


inicio = time.time()

print("="*60)
print("AUDITORIA DA GEOCODIFICACAO")
print("="*60)


# ------------------------------------------------------------
# Caminhos
# ------------------------------------------------------------

arquivo_base = r"resultados/base_residencial_p99.csv"

arquivo_saida = r"resultados/auditoria_geocodificacao.csv"

arquivo_endereco = r"resultados/endereco_agrupado.csv"


# ------------------------------------------------------------
# Função normalização texto
# ------------------------------------------------------------

def normalizar_texto(valor):

    if pd.isna(valor):
        return ""

    valor = str(valor).upper()

    valor = unicodedata.normalize(
        "NFKD",
        valor
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    valor = re.sub(
        r"[^A-Z0-9 ]",
        "",
        valor
    )

    valor = re.sub(
        r"\s+",
        " ",
        valor
    )

    return valor.strip()



# ------------------------------------------------------------
# Ler base
# ------------------------------------------------------------

print("\nLendo base residencial...")

df = pd.read_csv(
    arquivo_base,
    low_memory=False
)


print("Shape:")
print(df.shape)



# ------------------------------------------------------------
# Colunas existentes
# ------------------------------------------------------------

print("\nColunas encontradas:")

print(list(df.columns))



# ------------------------------------------------------------
# Auditoria geral
# ------------------------------------------------------------

resultado = []


def adicionar(indicador, valor):

    resultado.append(
        {
            "indicador": indicador,
            "valor": valor
        }
    )


adicionar(
    "total_registros",
    len(df)
)


adicionar(
    "matriculas_unicas",
    df["MATRICULA"].nunique()
)


adicionar(
    "matriculas_duplicadas",
    df["MATRICULA"].duplicated().sum()
)



# ------------------------------------------------------------
# Endereços
# ------------------------------------------------------------

print("\nCriando chave de endereço...")


df["ENDERECO_CHAVE"] = (
    df["Endereco"]
    .apply(normalizar_texto)
)


df["BAIRRO_CHAVE"] = (
    df["Bairro"]
    .apply(normalizar_texto)
)


df["ENDERECO_COMPLETO_CHAVE"] = (
    df["ENDERECO_CHAVE"]
    + "_"
    + df["BAIRRO_CHAVE"]
)



adicionar(
    "enderecos_unicos",
    df["ENDERECO_COMPLETO_CHAVE"].nunique()
)


repetidos = (
    df["ENDERECO_COMPLETO_CHAVE"]
    .value_counts()
)


adicionar(
    "enderecos_repetidos",
    (repetidos > 1).sum()
)


adicionar(
    "maior_numero_matriculas_mesmo_endereco",
    repetidos.max()
)



# ------------------------------------------------------------
# CEP
# ------------------------------------------------------------

if "CEP" in df.columns:

    cep_validos = (
        df["CEP"]
        .notna()
        .sum()
    )

    adicionar(
        "cep_preenchido",
        cep_validos
    )

    adicionar(
        "cep_nulo",
        len(df)-cep_validos
    )


# ------------------------------------------------------------
# Bairro
# ------------------------------------------------------------

adicionar(
    "bairros_unicos",
    df["Bairro"].nunique()
)



# ------------------------------------------------------------
# CD_SETOR existente
# ------------------------------------------------------------

if "CD_SETOR" in df.columns:

    setores = df["CD_SETOR"].notna().sum()

else:

    setores = 0


adicionar(
    "registros_com_cd_setor",
    setores
)



# ------------------------------------------------------------
# Salvar auditoria
# ------------------------------------------------------------

auditoria = pd.DataFrame(resultado)


auditoria.to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)



# ------------------------------------------------------------
# Agrupamento de endereço
# ------------------------------------------------------------

print("\nGerando agrupamento de endereços...")


grupo = (
    df.groupby(
        [
            "ENDERECO_COMPLETO_CHAVE",
            "Endereco",
            "Bairro"
        ],
        dropna=False
    )
    .agg(
        quantidade_matriculas=(
            "MATRICULA",
            "count"
        ),
        matriculas=(
            "MATRICULA",
            lambda x: ";".join(
                x.astype(str)
            )
        )
    )
    .reset_index()
)



grupo = grupo.sort_values(
    "quantidade_matriculas",
    ascending=False
)


grupo.to_csv(
    arquivo_endereco,
    index=False,
    encoding="utf-8-sig"
)



# ------------------------------------------------------------
# Resumo
# ------------------------------------------------------------

print("\n")
print("="*60)
print("RESUMO AUDITORIA")
print("="*60)


print(auditoria)


print("\nMaiores agrupamentos de endereço:")

print(
    grupo.head(20)
)



print("\nArquivos gerados:")

print(arquivo_saida)

print(arquivo_endereco)



print("\nTempo:")

print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")