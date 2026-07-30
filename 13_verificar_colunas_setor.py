import pandas as pd

arquivo = "resultados/base_residencial_p99.csv"

df = pd.read_csv(
    arquivo,
    low_memory=False
)

print("="*60)
print("VERIFICAÇÃO BASE RESIDENCIAL")
print("="*60)

print("\nShape:")
print(df.shape)

print("\nColunas:")
for c in df.columns:
    print(c)


print("\nExiste CD_SETOR?")

print(
    "CD_SETOR" in df.columns
)


print("\nExemplo:")
print(
    df.head()
)