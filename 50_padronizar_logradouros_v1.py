# ============================================================
# 50_padronizar_logradouros_v1.py
#
# Padronização pesada dos logradouros
#
# ============================================================

import pandas as pd
import re
import unicodedata
import time
import os

inicio = time.time()

print("="*70)
print("PADRONIZAÇÃO DE LOGRADOUROS")
print("="*70)

ENTRADA = "resultados/enderecos_unicos_para_geocodificar.csv"

SAIDA = "resultados/enderecos_unicos_padronizados.csv"

df = pd.read_csv(
    ENTRADA,
    dtype=str
).fillna("")


# --------------------------------------------------------
# remove acentos
# --------------------------------------------------------

def remover_acentos(txt):

    txt = unicodedata.normalize("NFKD", txt)

    txt = txt.encode("ASCII","ignore").decode()

    return txt


# --------------------------------------------------------
# função principal
# --------------------------------------------------------

def limpar(txt):

    txt = txt.upper()

    txt = remover_acentos(txt)

    # remove conteúdo entre ()
    txt = re.sub(r"\(.*?\)", " ", txt)

    # remove SN
    txt = re.sub(r"\bS/?N\b", " ", txt)

    # remove número no final
    txt = re.sub(r",?\s*\d+[A-Z]?$", " ", txt)

    # remove LAT.
    txt = re.sub(r"\bLAT\.?\b", " ", txt)

    # remove LATERAL DA
    txt = re.sub(r"LATERAL DA", " ", txt)

    txt = re.sub(r"LATERAL DO", " ", txt)

    txt = re.sub(r"LATERAL", " ", txt)

    # remove ACESSO
    txt = re.sub(r"ACESSO A", " ", txt)

    # remove FUNDOS
    txt = re.sub(r"FUNDOS", " ", txt)

    # remove FRENTE
    txt = re.sub(r"FRENTE", " ", txt)

    # remove PROXIMO
    txt = re.sub(r"PROXIMO A", " ", txt)

    # remove SD #####
    txt = re.sub(r"\bSD\s*\d+\b", " ", txt)

    # remove RUA #### quando for código interno
    txt = re.sub(r"\bRUA\s+\d+\s*-", "", txt)

    # padroniza abreviações
    txt = txt.replace("ROD.", "RODOVIA")
    txt = txt.replace("EST.", "ESTRADA")
    txt = txt.replace("SERV.", "SERVIDAO")
    txt = txt.replace("AV.", "AVENIDA")

    # remove espaços
    txt = re.sub(r"\s+", " ", txt)

    return txt.strip()


print("\nPadronizando...")

df["Endereco_Padronizado"] = df["Endereco"].apply(limpar)


# --------------------------------------------------------
# estatísticas
# --------------------------------------------------------

antes = len(df)

depois = df["Endereco_Padronizado"].nunique()

print()

print("="*70)

print("RESULTADO")

print("="*70)

print("Endereços antes :", antes)

print("Após padronização :", depois)

print("Redução :", antes-depois)

print("Percentual : %.2f%%" % (
    (antes-depois)/antes*100
))

df.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo salvo:")

print(SAIDA)

print("\nTempo:", round(time.time()-inicio,2), "segundos")

print("\nFim.")