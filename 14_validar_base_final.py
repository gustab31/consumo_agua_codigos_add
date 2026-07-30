import pandas as pd
import os
import time


inicio = time.time()

print("="*60)
print("VALIDAÇÃO BASE FINAL ESPACIAL")
print("="*60)


arquivo = "resultados/base_final.csv"


if not os.path.exists(arquivo):
    raise FileNotFoundError(arquivo)


df = pd.read_csv(
    arquivo,
    sep=",",
    encoding="utf-8",
    low_memory=False
)


print("\nShape:")
print(df.shape)


print("\nColunas:")
print(df.columns.tolist())


# -----------------------------
# Matrículas
# -----------------------------

print("\nMatrículas:")
print(df["matricula"].nunique())


# -----------------------------
# Setores
# -----------------------------

print("\nCD_SETOR:")

if "setor" in df.columns:

    print("Setores encontrados:")
    print(df["setor"].nunique())

    print("\nNulos:")
    print(df["setor"].isna().sum())

    percentual = (
        df["setor"].notna().mean()*100
    )

    print(
        f"\nPercentual com setor: {percentual:.2f}%"
    )


elif "CD_SETOR" in df.columns:

    print(df["CD_SETOR"].nunique())

else:

    print("Nenhuma coluna de setor encontrada")


# -----------------------------
# Consumo
# -----------------------------

print("\nConsumo L/hab.dia")

print(
    df["consumo_l_hab_dia"].describe(
        percentiles=[0.01,0.05,0.5,0.95,0.99]
    )
)


# -----------------------------
# Moradores
# -----------------------------

if "moradores_por_domicilio" in df.columns:

    print("\nMoradores:")
    print(
        df["moradores_por_domicilio"].describe()
    )


# -----------------------------
# Bairro
# -----------------------------

if "bairro" in df.columns:

    print("\nBairros:")
    print(
        df["bairro"].nunique()
    )


# -----------------------------
# Salvar cópia final
# -----------------------------

saida = "resultados/base_ANALISE_FINAL.csv"

df.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)


print("\nArquivo salvo:")
print(saida)


print("\nTempo:")
print(
    round(time.time()-inicio,2),
    "s"
)


print("\nFim.")