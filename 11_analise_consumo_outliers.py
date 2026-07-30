import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time


inicio = time.time()


print("="*60)
print("ANÁLISE DE OUTLIERS - CONSUMO L/HAB.DIA")
print("="*60)


# =====================================================
# LEITURA
# =====================================================

arquivo = (
    "resultados/base_consumo_limpa.csv"
)


df = pd.read_csv(
    arquivo,
    low_memory=False
)


print("\nBase:")
print(df.shape)



# =====================================================
# RESUMO
# =====================================================

col = "consumo_l_hab_dia"


print("\nResumo geral:")

print(
    df[col]
    .describe(
        percentiles=[
            .01,
            .05,
            .25,
            .50,
            .75,
            .95,
            .99
        ]
    )
)



# =====================================================
# CATEGORIAS
# =====================================================

if "Categoria_principal" in df.columns:

    print("\nConsumo por categoria:")

    print(
        df.groupby(
            "Categoria_principal"
        )[col]
        .describe()
    )



# =====================================================
# TOP OUTLIERS
# =====================================================

print("\nMaiores consumos:")


top = (
    df[
        [
            "MATRICULA",
            "Bairro",
            "Categoria_principal",
            "Número moradores",
            "consumo_medio_m3",
            col
        ]
    ]
    .sort_values(
        col,
        ascending=False
    )
    .head(100)
)


print(top.head(20))


top.to_csv(
    "resultados/diagnostico_outliers_consumo.csv",
    index=False,
    encoding="utf-8-sig"
)



# =====================================================
# LIMITES
# =====================================================

p95 = df[col].quantile(.95)
p99 = df[col].quantile(.99)


print("\nLimites:")

print(
    "P95:",
    round(p95,2)
)

print(
    "P99:",
    round(p99,2)
)



print("\nQuantidade acima P99:")

print(
    (
        df[col] > p99
    )
    .sum()
)



# =====================================================
# HISTOGRAMA
# =====================================================

plt.figure(figsize=(10,6))


plt.hist(
    df[col].dropna(),
    bins=100
)


plt.axvline(
    p99,
    color="red",
    linestyle="--",
    label=f"P99={p99:.1f}"
)


plt.xlabel(
    "Consumo (L/hab.dia)"
)


plt.ylabel(
    "Número de ligações"
)


plt.title(
    "Distribuição do consumo per capita"
)


plt.legend()


plt.tight_layout()


plt.savefig(
    "resultados/histograma_consumo.png",
    dpi=300
)


plt.close()



# =====================================================
# FINAL
# =====================================================


fim = time.time()


print("\nArquivos gerados:")

print(
    "- resultados/diagnostico_outliers_consumo.csv"
)

print(
    "- resultados/histograma_consumo.png"
)


print("\nTempo:")
print(
    round(fim-inicio,2),
    "s"
)


print("\nFim.")