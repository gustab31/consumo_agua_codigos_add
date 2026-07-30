# ============================================================
# GEOCODIFICAÇÃO COMPLETA DE ENDEREÇOS
# ============================================================

import pandas as pd
import os
import time
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


inicio = time.time()


print("="*60)
print("GEOCODIFICAÇÃO COMPLETA DE ENDEREÇOS")
print("="*60)


# ------------------------------------------------------------
# Arquivos
# ------------------------------------------------------------

entrada = (
    "resultados/base_residencial_p99.csv"
)

saida = (
    "resultados/geocode_completo.csv"
)


# ------------------------------------------------------------
# Ler base
# ------------------------------------------------------------

print("\nLendo base...")

df = pd.read_csv(
    entrada,
    low_memory=False
)

print(
    "Base:",
    df.shape
)


# ------------------------------------------------------------
# Criar endereço de busca
# ------------------------------------------------------------

print("\nMontando endereços...")


df["endereco_busca"] = (
    df["Endereco"].astype(str)
    + ", "
    + df["Bairro"].astype(str)
    + ", Joinville - SC"
)


# ------------------------------------------------------------
# Carregar resultados anteriores
# ------------------------------------------------------------

if os.path.exists(saida):

    print("\nEncontrado arquivo anterior")

    geo_ant = pd.read_csv(
        saida,
        low_memory=False
    )

    processados = set(
        geo_ant["MATRICULA"]
        .astype(str)
    )

    print(
        "Já processados:",
        len(processados)
    )

else:

    geo_ant = pd.DataFrame()

    processados = set()



# ------------------------------------------------------------
# Selecionar faltantes
# ------------------------------------------------------------

df["MATRICULA"] = (
    df["MATRICULA"]
    .astype(str)
)


faltantes = df[
    ~df["MATRICULA"].isin(processados)
].copy()


print(
    "Pendentes:",
    len(faltantes)
)


# ------------------------------------------------------------
# Geocoder
# ------------------------------------------------------------

geolocator = Nominatim(
    user_agent="pesquisa_censitario_agua"
)


geocode = RateLimiter(
    geolocator.geocode,
    min_delay_seconds=1
)



# ------------------------------------------------------------
# Processamento
# ------------------------------------------------------------

resultados = []


for i, linha in faltantes.iterrows():

    matricula = linha["MATRICULA"]

    endereco = linha["endereco_busca"]

    print(
        f"{i}/{len(faltantes)} - {matricula}"
    )


    try:

        local = geocode(
            endereco
        )


        if local:

            lat = local.latitude
            lon = local.longitude

        else:

            lat = None
            lon = None


    except Exception as e:

        print(
            "Erro:",
            e
        )

        lat = None
        lon = None



    resultados.append(
        {
            "MATRICULA": matricula,
            "Endereco": linha["Endereco"],
            "Bairro": linha["Bairro"],
            "CEP": linha["CEP"],
            "latitude": lat,
            "longitude": lon
        }
    )


    # salvar a cada 100 registros

    if len(resultados) % 100 == 0:


        parcial = pd.DataFrame(
            resultados
        )


        if len(geo_ant):

            parcial = pd.concat(
                [
                    geo_ant,
                    parcial
                ],
                ignore_index=True
            )


        parcial.to_csv(
            saida,
            index=False,
            encoding="utf-8-sig"
        )


        print(
            "Salvo parcial:",
            len(parcial)
        )



# ------------------------------------------------------------
# Salvar final
# ------------------------------------------------------------

novo = pd.DataFrame(
    resultados
)


if len(geo_ant):

    novo = pd.concat(
        [
            geo_ant,
            novo
        ],
        ignore_index=True
    )


novo.to_csv(
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
    "Total geocodificado:",
    len(novo)
)


print(
    "Com coordenadas:",
    novo["latitude"].notna().sum()
)


print(
    "Percentual:",
    round(
        novo["latitude"].notna().mean()*100,
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
    "\nTempo:",
    round(time.time()-inicio,2)
)


print("\nFim.")