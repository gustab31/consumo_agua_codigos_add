import pandas as pd
import time


inicio = time.time()


print("="*60)
print("RECUPERANDO CD_SETOR PARA MATRÍCULAS")
print("="*60)



# =====================================================
# ARQUIVOS
# =====================================================

arquivo_base = "resultados/base_residencial_p99.csv"

arquivo_espacial = "resultados/base_final_espacial.csv"



# =====================================================
# LEITURA
# =====================================================

print("\nLendo base residencial...")

df = pd.read_csv(
    arquivo_base,
    low_memory=False
)


print("Base residencial:")
print(df.shape)



print("\nLendo base espacial...")

esp = pd.read_csv(
    arquivo_espacial,
    low_memory=False
)


print("Base espacial:")
print(esp.shape)



# =====================================================
# IDENTIFICAR MATRÍCULA
# =====================================================

col_matricula = None


for c in esp.columns:

    if c.lower().strip() == "matricula":

        col_matricula = c
        break



if col_matricula is None:

    raise Exception(
        "Não encontrou coluna matrícula"
    )


print(
    "\nColuna matrícula espacial:",
    col_matricula
)



# =====================================================
# PREPARAR SETOR
# =====================================================

esp_setor = esp[
    [
        col_matricula,
        "CD_SETOR"
    ]
].copy()


esp_setor = esp_setor.rename(
    columns={
        col_matricula:"MATRICULA"
    }
)



# =====================================================
# PADRONIZAR MATRÍCULA
# =====================================================

print("\nPadronizando matrículas...")


df["MAT_SEM_HIFEN"] = (
    df["MATRICULA"]
    .astype(str)
    .str.strip()
    .str.replace("-", "", regex=False)
)



esp_setor["MAT_SEM_HIFEN"] = (
    esp_setor["MATRICULA"]
    .astype(str)
    .str.strip()
    .str.replace("-", "", regex=False)
)



# retirar duplicados

esp_setor = (
    esp_setor
    .drop_duplicates(
        subset="MAT_SEM_HIFEN"
    )
)



print(
    "Matrículas espaciais disponíveis:"
)

print(
    esp_setor.shape
)



# =====================================================
# MERGE
# =====================================================

print("\nExecutando merge...")


final = df.merge(
    esp_setor[
        [
            "MAT_SEM_HIFEN",
            "CD_SETOR"
        ]
    ],
    on="MAT_SEM_HIFEN",
    how="left",
    indicator=True
)



print("\nResultado:")
print(final.shape)



print("\nCorrespondência:")

print(
    final["_merge"]
    .value_counts()
)



print("\nSetores encontrados:")

print(
    final["CD_SETOR"]
    .notna()
    .sum()
)



print("\nPercentual com setor:")

print(
    round(
        final["CD_SETOR"]
        .notna()
        .mean()*100,
        2
    ),
    "%"
)



# =====================================================
# SALVAR
# =====================================================

final = final.drop(
    columns=[
        "_merge",
        "MAT_SEM_HIFEN"
    ]
)



saida = (
    "resultados/base_residencial_com_setor.csv"
)



final.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)



print("\nArquivo salvo:")
print(saida)



print("\nTempo:")

print(
    round(time.time()-inicio,2),
    "segundos"
)


print("\nFim.")