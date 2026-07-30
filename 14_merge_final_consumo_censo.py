import pandas as pd
import os
import time


inicio=time.time()

print("="*60)
print("MERGE FINAL CONSUMO + CENSO")
print("="*60)


# arquivos

consumo = "resultados/base_residencial_p99.csv"

espacial = "resultados/base_final_espacial.csv"


print("\nLendo consumo...")
df1=pd.read_csv(
    consumo,
    low_memory=False
)

print(df1.shape)


print("\nLendo espacial...")
df2=pd.read_csv(
    espacial,
    low_memory=False
)

print(df2.shape)



# padronizar matricula

print("\nPadronizando matrículas...")


df1["matricula_merge"] = (
    df1["MATRICULA"]
    .astype(str)
    .str.replace("-","",regex=False)
)


df2["matricula_merge"] = (
    df2["matricula"]
    .astype(str)
    .str.replace("-","",regex=False)
)



# manter somente 1 registro espacial por matrícula

df2 = (
    df2
    .drop_duplicates(
        subset="matricula_merge"
    )
)


print(
    "Espacial único:",
    df2.shape
)



# selecionar campos censitários

cols = [
    "matricula_merge",
    "CD_SETOR",
    "V0001",
    "V0002",
    "V0003",
    "V0004",
    "V0005",
    "V0006",
    "V0007",
    "NM_BAIRRO",
    "AREA_KM2"
]


df2=df2[cols]


print("\nMerge...")


final = df1.merge(
    df2,
    on="matricula_merge",
    how="left",
    indicator=True
)



print("\nResultado:")
print(final.shape)


print("\nCorrespondência:")
print(
    final["_merge"].value_counts()
)


print(
    "\nSetores:",
    final["CD_SETOR"].notna().sum()
)


print(
    "Percentual setor:",
    round(
        final["CD_SETOR"].notna().mean()*100,
        2
    ),
    "%"
)



# remover auxiliar

final.drop(
    columns=["matricula_merge","_merge"],
    inplace=True
)



saida="resultados/base_ANALISE_FINAL.csv"


final.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)


print("\nSalvo:")
print(saida)


print("\nTempo:")
print(round(time.time()-inicio,2))


print("\nFim")