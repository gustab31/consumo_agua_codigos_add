# ============================================================
# RECUPERANDO CD_SETOR POR SPATIAL JOIN FINAL
# ============================================================

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely import wkt
import time


inicio = time.time()


print("="*60)
print("RECUPERANDO CD_SETOR POR SPATIAL JOIN FINAL")
print("="*60)


# ------------------------------------------------------------
# Arquivos
# ------------------------------------------------------------

arquivo_residencial = (
    "resultados/base_residencial_p99.csv"
)

arquivo_espacial = (
    "resultados/base_final_espacial.csv"
)

saida = (
    "resultados/base_residencial_com_setor_completo.csv"
)


# ------------------------------------------------------------
# Ler residencial
# ------------------------------------------------------------

print("\nLendo residencial...")

df = pd.read_csv(
    arquivo_residencial,
    low_memory=False
)

print(
    "Residencial:",
    df.shape
)


# ------------------------------------------------------------
# Ler base espacial
# ------------------------------------------------------------

print("\nLendo base espacial...")

esp = pd.read_csv(
    arquivo_espacial,
    low_memory=False
)

print(
    "Espacial:",
    esp.shape
)


print(
    "\nColunas espacial:"
)

print(
    esp.columns.tolist()
)


# ------------------------------------------------------------
# Preparar espacial
# ------------------------------------------------------------

print("\nPreparando setores...")


esp = esp[
    [
        "matricula",
        "CD_SETOR",
        "geometry"
    ]
].copy()


esp = esp.dropna(
    subset=[
        "CD_SETOR",
        "geometry"
    ]
)


# transformar WKT em geometria
esp["geometry"] = esp["geometry"].apply(
    wkt.loads
)


setores = gpd.GeoDataFrame(
    esp,
    geometry="geometry",
    crs="EPSG:4326"
)


print(
    "Setores disponíveis:",
    setores["CD_SETOR"].nunique()
)


# ------------------------------------------------------------
# Criar pontos das matrículas
# ------------------------------------------------------------

print("\nCriando pontos...")


# pegar coordenadas se existirem na base espacial

coord = pd.read_csv(
    "resultados/base_geocodificada.csv",
    low_memory=False
)


coord["matricula"] = (
    coord["matricula"]
    .astype(str)
    .str.replace("-", "", regex=False)
)


coord = coord[
    [
        "matricula",
        "latitude",
        "longitude"
    ]
]


coord = coord.drop_duplicates(
    subset="matricula"
)


df["matricula_aux"] = (
    df["MATRICULA"]
    .astype(str)
    .str.replace("-", "", regex=False)
)


df = df.merge(
    coord,
    left_on="matricula_aux",
    right_on="matricula",
    how="left"
)


print(
    "Com coordenadas:",
    df["latitude"].notna().sum()
)


# ------------------------------------------------------------
# GeoDataFrame dos pontos
# ------------------------------------------------------------

pontos = df[
    df["latitude"].notna()
    &
    df["longitude"].notna()
].copy()


geometry = [
    Point(x,y)
    for x,y in zip(
        pontos["longitude"],
        pontos["latitude"]
    )
]


gdf = gpd.GeoDataFrame(
    pontos,
    geometry=geometry,
    crs="EPSG:4326"
)


# ------------------------------------------------------------
# Spatial Join
# ------------------------------------------------------------

print("\nExecutando spatial join...")


resultado = gpd.sjoin(
    gdf,
    setores[
        [
            "CD_SETOR",
            "geometry"
        ]
    ],
    how="left",
    predicate="within"
)


print(
    "Setores encontrados:",
    resultado["CD_SETOR"].notna().sum()
)


# ------------------------------------------------------------
# Voltar tabela
# ------------------------------------------------------------

resultado = pd.DataFrame(
    resultado.drop(
        columns="geometry"
    )
)


if "index_right" in resultado.columns:
    resultado = resultado.drop(
        columns="index_right"
    )


# ------------------------------------------------------------
# Juntar novamente com quem não tinha coordenada
# ------------------------------------------------------------

sem_ponto = df[
    df["latitude"].isna()
    |
    df["longitude"].isna()
].copy()


if len(sem_ponto) > 0:

    print(
        "\nSem coordenadas:",
        len(sem_ponto)
    )


    sem_ponto["CD_SETOR"] = None


    resultado_final = pd.concat(
        [
            resultado,
            sem_ponto
        ],
        ignore_index=True
    )

else:

    resultado_final = resultado



# ------------------------------------------------------------
# Limpeza
# ------------------------------------------------------------

resultado_final = resultado_final.drop(
    columns=[
        "matricula_aux",
        "matricula",
        "latitude",
        "longitude"
    ],
    errors="ignore"
)


# ------------------------------------------------------------
# Salvar
# ------------------------------------------------------------

resultado_final.to_csv(
    saida,
    index=False,
    encoding="utf-8-sig"
)


# ------------------------------------------------------------
# Resumo
# ------------------------------------------------------------

print("\n")
print("="*60)
print("RESULTADO FINAL")
print("="*60)


print(
    "Linhas:",
    len(resultado_final)
)


print(
    "Matrículas:",
    resultado_final["MATRICULA"].nunique()
)


print(
    "Setores encontrados:",
    resultado_final["CD_SETOR"].notna().sum()
)


print(
    "Percentual:",
    round(
        resultado_final["CD_SETOR"].notna().mean()*100,
        2
    ),
    "%"
)


print(
    "\nArquivo salvo:"
)

print(
    saida
)


print(
    "\nTempo:"
)

print(
    round(
        time.time()-inicio,
        2
    )
)


print("\nFim.")