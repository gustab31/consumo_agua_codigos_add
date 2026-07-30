import pandas as pd
import time


inicio = time.time()

print("="*60)
print("GERAÇÃO DAS BASES FINAIS DE ANÁLISE")
print("="*60)


# =====================================================
# ARQUIVO
# =====================================================

entrada = (
    "resultados/base_consumo_limpa.csv"
)


df = pd.read_csv(
    entrada,
    low_memory=False
)


print("\nBase inicial:")
print(df.shape)



# =====================================================
# P99 GLOBAL
# =====================================================

col = "consumo_l_hab_dia"


p99 = df[col].quantile(0.99)


print("\nP99:")
print(round(p99,2))



# =====================================================
# BASE COMPLETA
# =====================================================

print("\nGerando base completa...")


base_completa = df[
    df[col] <= p99
].copy()


print(
    "Completa:",
    base_completa.shape
)


base_completa.to_csv(
    "resultados/base_completa_p99.csv",
    index=False,
    encoding="utf-8-sig"
)



# =====================================================
# BASE RESIDENCIAL
# =====================================================

print("\nGerando base residencial...")


base_res = df[
    df["Categoria_principal"]
    =="Residencial"
].copy()


base_res = base_res[
    base_res[col] <= p99
].copy()


print(
    "Residencial:",
    base_res.shape
)


base_res.to_csv(
    "resultados/base_residencial_p99.csv",
    index=False,
    encoding="utf-8-sig"
)



# =====================================================
# RESUMOS
# =====================================================

print("\nResumo residencial:")

print(
    base_res[col]
    .describe()
)



print("\nResumo completa:")

print(
    base_completa[col]
    .describe()
)



# =====================================================
# BAIRROS
# =====================================================

if "Bairro" in df.columns:

    resumo_bairro = (
        base_res
        .groupby("Bairro")
        [col]
        .agg(
            [
                "count",
                "mean",
                "median"
            ]
        )
        .sort_values(
            "median",
            ascending=False
        )
    )


    resumo_bairro.to_csv(
        "resultados/resumo_consumo_bairro.csv",
        encoding="utf-8-sig"
    )



# =====================================================
# FINAL
# =====================================================

fim = time.time()


print("\nArquivos gerados:")

print(
    "- resultados/base_completa_p99.csv"
)

print(
    "- resultados/base_residencial_p99.csv"
)

print(
    "- resultados/resumo_consumo_bairro.csv"
)


print("\nTempo:")
print(
    round(fim-inicio,2),
    "segundos"
)


print("\nFim.")