# ============================================================
# 19_priorizar_geocodificacao_endereco_v2.py
# ============================================================

import pandas as pd
import time
import re


inicio = time.time()


print("="*60)
print("PRIORIZANDO GEOCODIFICACAO POR ENDERECO - V2")
print("="*60)


# ============================================================
# ARQUIVOS
# ============================================================

BASE = "resultados/base_residencial_setor_endereco_cep_v3.csv"

SAIDA = "resultados/fila_geocodificacao_endereco.csv"



# ============================================================
# FUNÇÃO NORMALIZAÇÃO
# ============================================================

def normalizar(texto):

    if pd.isna(texto):
        return ""

    texto = str(texto).upper()

    texto = re.sub(
        r"[^A-Z0-9]",
        "",
        texto
    )

    return texto



# ============================================================
# LEITURA
# ============================================================

print("\nLendo base...")


df = pd.read_csv(
    BASE,
    low_memory=False
)


print(
    "Shape:",
    df.shape
)


print(
    "\nColunas:"
)

print(
    df.columns.tolist()
)



# ============================================================
# CRIAR CHAVES
# ============================================================

print("\nCriando chave de endereço...")


df["END_CHAVE"] = (
    df["Endereco"]
    .apply(normalizar)
)


df["BAIRRO_CHAVE"] = (
    df["Bairro"]
    .apply(normalizar)
)



df["CHAVE_END_BAIRRO"] = (

    df["END_CHAVE"]
    +
    "_"
    +
    df["BAIRRO_CHAVE"]

)



# ============================================================
# REMOVER QUEM JÁ TEM SETOR
# ============================================================


print("\nRegistros com setor:")


if "CD_SETOR" in df.columns:

    print(
        df["CD_SETOR"]
        .notna()
        .sum()
    )

else:

    print("Não existe CD_SETOR")

    df["CD_SETOR"] = None



# ============================================================
# AGRUPAR ENDEREÇOS
# ============================================================


print("\nAgrupando endereços...")


grupo = (

    df.groupby(
        "CHAVE_END_BAIRRO"
    )

    .agg(

        endereco=(
            "Endereco",
            "first"
        ),

        bairro=(
            "Bairro",
            "first"
        ),

        cep=(
            "CEP",
            "first"
        ),

        total_matriculas=(
            "MATRICULA",
            "nunique"
        ),

        matriculas=(
            "MATRICULA",
            lambda x:
            ";".join(
                x.astype(str)
            )
        ),

        possui_setor=(
            "CD_SETOR",
            lambda x:
            x.notna()
            .any()
        )

    )

    .reset_index()

)



# ============================================================
# SOMENTE SEM SETOR
# ============================================================


grupo = grupo[
    grupo["possui_setor"] == False
]



# ============================================================
# PRIORIDADE
# ============================================================


def definir_prioridade(n):

    if n >= 50:
        return "MUITO_ALTA"

    elif n >= 10:
        return "ALTA"

    elif n >= 3:
        return "MEDIA"

    else:
        return "BAIXA"



grupo["prioridade"] = (

    grupo["total_matriculas"]
    .apply(definir_prioridade)

)



ordem = {

    "MUITO_ALTA":1,
    "ALTA":2,
    "MEDIA":3,
    "BAIXA":4

}


grupo["ordem"] = (

    grupo["prioridade"]
    .map(ordem)

)



grupo = grupo.sort_values(
    [
        "ordem",
        "total_matriculas"
    ],
    ascending=[
        True,
        False
    ]
)


grupo.drop(
    columns=["ordem"],
    inplace=True
)



# ============================================================
# RESULTADO
# ============================================================


print("\n")
print("="*60)
print("RESULTADO")
print("="*60)


print(
    "Endereços para geocodificar:",
    len(grupo)
)


print("\nPrioridade:")

print(
    grupo["prioridade"]
    .value_counts()
)



print(
    "\nMatrículas potenciais:"
)

print(
    grupo["total_matriculas"]
    .sum()
)



print("\nTop 20:")


print(

    grupo.head(20)
    [
        [
            "endereco",
            "bairro",
            "total_matriculas",
            "prioridade"
        ]
    ]

)



# ============================================================
# SALVAR
# ============================================================


grupo.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)



print("\nArquivo salvo:")
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