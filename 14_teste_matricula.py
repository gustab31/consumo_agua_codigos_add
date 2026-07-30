import pandas as pd


res = pd.read_csv(
    "resultados/base_residencial_p99.csv",
    low_memory=False
)

esp = pd.read_csv(
    "resultados/base_final_espacial.csv",
    low_memory=False
)


print("="*60)
print("TESTE DE MATRÍCULAS")
print("="*60)


# padronização

res["MATRICULA_TESTE"] = (
    res["MATRICULA"]
    .astype(str)
    .str.strip()
)


esp["MATRICULA_TESTE"] = (
    esp["matricula"]
    .astype(str)
    .str.strip()
)


print("\nExemplos residencial:")
print(
    res["MATRICULA_TESTE"].head(10)
)


print("\nExemplos espacial:")
print(
    esp["MATRICULA_TESTE"].head(10)
)



# interseção

comuns = set(
    res["MATRICULA_TESTE"]
).intersection(
    set(
        esp["MATRICULA_TESTE"]
    )
)


print("\nMatrículas em comum:")
print(len(comuns))


if len(comuns)>0:
    print("\nExemplos:")
    print(
        list(comuns)[:10]
    )