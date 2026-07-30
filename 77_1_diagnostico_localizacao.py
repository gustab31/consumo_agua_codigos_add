# ============================================================
# 77_1_diagnostico_localizacao.py
#
# Diagnóstico do campo Localizacao
#
# Objetivo:
# descobrir se existe:
# - coordenada
# - endereço
# - código interno
# - outra chave espacial
#
# ============================================================


import os
import re
import time
import warnings

import pandas as pd


warnings.filterwarnings("ignore")


inicio = time.time()


print("="*70)
print("DIAGNÓSTICO CAMPO LOCALIZACAO - RELATÓRIO 75")
print("="*70)



ARQUIVO = "2022.06.29. relatorio 75 1.xlsx"


RESULTADOS = "resultados"


os.makedirs(

    RESULTADOS,

    exist_ok=True

)



# ============================================================
# LER RELATÓRIO
# ============================================================


print("\nLendo arquivo...")


bruto = pd.read_excel(

    ARQUIVO,

    header=None

)



linha_cabecalho = None



for i in range(len(bruto)):


    valores = (

        bruto.iloc[i]

        .fillna("")

        .astype(str)

        .str.lower()

        .tolist()

    )


    texto = " ".join(valores)


    if "matricula" in texto:


        linha_cabecalho = i

        break



if linha_cabecalho is None:

    raise Exception(

        "Cabeçalho não encontrado"

    )



print(

    "Cabeçalho:",

    linha_cabecalho

)



df = pd.read_excel(

    ARQUIVO,

    header=linha_cabecalho

)



df.columns = [

    str(c).strip()

    for c in df.columns

]



print("\nColunas:")


for c in df.columns:

    print("-", c)



# ============================================================
# VERIFICAR LOCALIZACAO
# ============================================================


col = None



for c in df.columns:


    if "local" in str(c).lower():

        col = c

        break



if col is None:

    raise Exception(

        "Campo Localizacao não encontrado"

    )



print(

    "\nCampo utilizado:",

    col

)



serie = (

    df[col]

    .dropna()

    .astype(str)

    .str.strip()

)



print(

    "\nValores únicos:",

    serie.nunique()

)



# ============================================================
# AMOSTRA
# ============================================================


amostra = pd.DataFrame({

    "Localizacao":

    serie.sample(

        min(200, len(serie)),

        random_state=1

    )

})



arquivo_amostra = os.path.join(

    RESULTADOS,

    "amostra_localizacao.xlsx"

)



amostra.to_excel(

    arquivo_amostra,

    index=False

)



print(

    "\nAmostra salva:",

    arquivo_amostra

)



# ============================================================
# TESTES DE PADRÃO
# ============================================================



texto_total = " ".join(

    serie.head(5000)

)



padroes = {


    "tem_latitude_longitude":

    r"-?\d+\.\d+[,; ]+-?\d+\.\d+",


    "tem_coordenada_grau":

    r"\d{1,3}°",


    "tem_CEP":

    r"\d{5}-?\d{3}",


    "tem_numero_endereco":

    r"\d+\s",

}



print("\nTestes de padrão:")



for nome, regex in padroes.items():


    resultado = bool(

        re.search(

            regex,

            texto_total

        )

    )


    print(

        nome,

        "->",

        resultado

    )



# ============================================================
# DISTRIBUIÇÃO DOS FORMATOS
# ============================================================


formatos = pd.DataFrame({

    "Localizacao":

    serie,

    "tamanho":

    serie.str.len(),

    "tem_numero":

    serie.str.contains(

        r"\d",

        regex=True

    ),

    "tem_virgula":

    serie.str.contains(",")

})



formatos.to_excel(

    os.path.join(

        RESULTADOS,

        "diagnostico_formatos_localizacao.xlsx"

    ),

    index=False

)



# ============================================================
# RESUMO
# ============================================================


print("\nResumo:")


print(

    formatos.describe(include="all")

)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 77.1")