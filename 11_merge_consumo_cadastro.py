import pandas as pd
import os
import time

inicio = time.time()

print("="*60)
print("MERGE CONSUMO + CADASTRO CAJ")
print("="*60)

# =====================================================
# ARQUIVOS
# =====================================================

ARQ_CONSUMO = "resultados/consumo_matricula.csv"

ARQ_CADASTRO = "2022.06.29. relatorio 75 1.xlsx"

SAIDA = "resultados/consumo_caj_completo.csv"


# =====================================================
# VERIFICA
# =====================================================

for arq in [ARQ_CONSUMO, ARQ_CADASTRO]:

    if not os.path.exists(arq):
        raise FileNotFoundError(
            f"Arquivo não encontrado: {arq}"
        )


# =====================================================
# CONSUMO
# =====================================================

print("\nLendo consumo...")

consumo = pd.read_csv(
    ARQ_CONSUMO,
    dtype={"MATRICULA":str}
)

print(consumo.shape)

# padroniza matrícula

consumo["MATRICULA"] = (
    consumo["MATRICULA"]
    .astype(str)
    .str.strip()
)


# =====================================================
# CADASTRO CAJ
# =====================================================

print("\nLendo cadastro CAJ...")

cadastro = pd.read_excel(
    ARQ_CADASTRO,
    header=1
)

print("\nColunas encontradas:")
print(cadastro.columns.tolist())


# =====================================================
# PADRONIZA NOMES
# =====================================================

cadastro.columns = (
    cadastro.columns
    .astype(str)
    .str.strip()
)


# localizar matrícula

col_mat = None

for c in cadastro.columns:

    if "matric" in c.lower():

        col_mat = c
        break


if col_mat is None:

    raise ValueError(
        "Coluna matrícula não encontrada no cadastro"
    )


print("\nColuna matrícula:")
print(col_mat)


cadastro = cadastro.rename(
    columns={
        col_mat:"MATRICULA"
    }
)


cadastro["MATRICULA"] = (
    cadastro["MATRICULA"]
    .astype(str)
    .str.strip()
)


# =====================================================
# MERGE
# =====================================================

print("\nExecutando merge...")

base = consumo.merge(
    cadastro,
    on="MATRICULA",
    how="left",
    indicator=True
)


# =====================================================
# DIAGNÓSTICO
# =====================================================

print("\nResultado:")
print(base.shape)


print("\nCorrespondência:")
print(
    base["_merge"]
    .value_counts()
)


taxa = (
    (base["_merge"]=="both")
    .mean()
    *100
)

print("\nTaxa encontrada:")
print(round(taxa,2), "%")


# remove coluna auxiliar

base = base.drop(
    columns="_merge"
)


# =====================================================
# SALVAR
# =====================================================

base.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivo salvo:")
print(SAIDA)


print("\nTempo:")
print(
    round(time.time()-inicio,2),
    "segundos"
)

print("\nFim.")