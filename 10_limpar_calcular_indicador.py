import pandas as pd
import numpy as np
import time
import unicodedata


# =====================================================
# FUNÇÃO NORMALIZAR NOMES
# =====================================================

def normalizar(texto):

    texto = str(texto)

    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = texto.encode(
        "ascii",
        "ignore"
    ).decode(
        "utf-8"
    )

    texto = texto.lower()

    texto = (
        texto
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
    )

    return texto



# =====================================================
# INÍCIO
# =====================================================

inicio = time.time()

print("="*60)
print("LIMPEZA CADASTRO CAJ + INDICADOR L/HAB.DIA")
print("="*60)



# =====================================================
# ARQUIVOS
# =====================================================

entrada = (
    "resultados/consumo_caj_completo.csv"
)

saida = (
    "resultados/base_consumo_limpa.csv"
)



# =====================================================
# LEITURA
# =====================================================

print("\nLendo base...")

df = pd.read_csv(
    entrada,
    low_memory=False
)


print("\nShape inicial:")
print(df.shape)



print("\nColunas:")
print(df.columns.tolist())



# =====================================================
# IDENTIFICAR COLUNAS
# =====================================================


def encontrar_coluna(palavra):

    for c in df.columns:

        nome = normalizar(c)

        if palavra in nome:

            return c

    return None



col_matricula = encontrar_coluna(
    "matric"
)

col_moradores = encontrar_coluna(
    "numeromoradores"
)

col_ligacao = encontrar_coluna(
    "ligacaoagua"
)

col_consumo = encontrar_coluna(
    "consumomedio"
)



print("\nColunas identificadas:")

print(
    "Matrícula:",
    col_matricula
)

print(
    "Moradores:",
    col_moradores
)

print(
    "Ligação:",
    col_ligacao
)

print(
    "Consumo:",
    col_consumo
)



if col_matricula is None:
    raise ValueError(
        "Matrícula não encontrada"
    )


if col_moradores is None:
    raise ValueError(
        "Número moradores não encontrado"
    )


if col_ligacao is None:
    raise ValueError(
        "Ligacao_agua não encontrada"
    )


if col_consumo is None:
    raise ValueError(
        "Consumo não encontrado"
    )



# =====================================================
# MATRÍCULA
# =====================================================

df[col_matricula] = (
    df[col_matricula]
    .astype(str)
    .str.strip()
)



# =====================================================
# SOMENTE LIGAÇÕES ATIVAS
# =====================================================

print("\nFiltrando ligações ativas...")

df = df[
    df[col_ligacao]
    =="Ativa"
].copy()


print(
    "Após ligação ativa:",
    df.shape
)



# =====================================================
# MORADORES
# =====================================================

print("\nTratando moradores...")


df[col_moradores] = pd.to_numeric(
    df[col_moradores],
    errors="coerce"
)


# remove:
# zero
# valores absurdos

df = df[
    (df[col_moradores] > 0)
    &
    (df[col_moradores] <= 20)
].copy()


print(
    "Após moradores válidos:",
    df.shape
)



# =====================================================
# CONSUMO
# =====================================================

print("\nTratando consumo...")


df[col_consumo] = pd.to_numeric(
    df[col_consumo],
    errors="coerce"
)


df = df[
    df[col_consumo].notna()
].copy()


df = df[
    df[col_consumo] >= 0
].copy()


print(
    "Após consumo válido:",
    df.shape
)



# =====================================================
# INDICADOR
# =====================================================

print("\nCalculando consumo L/hab.dia...")


df["consumo_l_hab_dia"] = (

    df[col_consumo] * 1000

) / (

    df[col_moradores] * 30

)



# remove inválidos

df.loc[
    df["consumo_l_hab_dia"] <= 0,
    "consumo_l_hab_dia"
] = np.nan



# =====================================================
# DIAGNÓSTICO
# =====================================================

print("\n==============================")
print("RESUMO FINAL")
print("==============================")


print("\nRegistros:")
print(len(df))


print("\nMatrículas:")
print(
    df[col_matricula]
    .nunique()
)


print("\nMoradores:")
print(
    df[col_moradores]
    .describe()
)


print("\nConsumo m3:")
print(
    df[col_consumo]
    .describe()
)


print("\nConsumo L/hab.dia:")
print(
    df["consumo_l_hab_dia"]
    .describe()
)



# =====================================================
# P99
# =====================================================

p99 = (
    df["consumo_l_hab_dia"]
    .quantile(0.99)
)


print("\nP99:")
print(
    round(p99,2)
)



print("\nMaiores valores:")

print(
    df[
        [
            col_matricula,
            "consumo_l_hab_dia"
        ]
    ]
    .sort_values(
        "consumo_l_hab_dia",
        ascending=False
    )
    .head(20)
)



# =====================================================
# SALVAR
# =====================================================

df.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivo salvo:")
print(saida)



# =====================================================
# FINAL
# =====================================================

fim = time.time()


print("\nTempo:")
print(
    round(
        fim-inicio,
        2
    ),
    "segundos"
)


print("\nProcesso concluído.")