import pandas as pd
import os

arquivo = "resultados/consumo_matricula.csv"

print("Arquivo existe?")
print(os.path.exists(arquivo))

df = pd.read_csv(
    arquivo
)

print("\nLinhas e colunas:")
print(df.shape)

print("\nPrimeiras linhas:")
print(df.head())

print("\nResumo:")
print(df["consumo_medio_m3"].describe())