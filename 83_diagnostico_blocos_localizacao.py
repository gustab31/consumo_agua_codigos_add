# ============================================================
# 83_diagnostico_blocos_localizacao.py
#
# DIAGNÓSTICO DOS BLOCOS DA LOCALIZACAO CAJ
#
# Entrada:
#   2022.06.29. relatorio 75 1.xlsx
#
# Saídas:
#   diagnostico_blocos_localizacao.xlsx
#   frequencia_blocos_localizacao.xlsx
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
print("DIAGNÓSTICO BLOCOS LOCALIZACAO CAJ")
print("="*70)



RESULTADOS = "resultados"


arquivo_relatorio = (
    "2022.06.29. relatorio 75 1.xlsx"
)



# ============================================================
# FUNÇÃO SEGURA
# ============================================================


def texto_seguro(x):

    if pd.isna(x):

        return ""

    return str(x)



# ============================================================
# LOCALIZAR CABEÇALHO
# ============================================================


print("\nLendo Relatório 75...")


bruto = pd.read_excel(

    arquivo_relatorio,

    header=None

)



linha_cab = None



for i in range(15):


    linha = (

        bruto.iloc[i]

        .apply(texto_seguro)

        .tolist()

    )


    texto = " ".join(linha).lower()


    if (

        "matricula" in texto

        and "localizacao" in texto

    ):

        linha_cab = i

        break



if linha_cab is None:

    raise Exception(
        "Cabeçalho não encontrado"
    )



print(

    "Cabeçalho:",

    linha_cab

)



df = pd.read_excel(

    arquivo_relatorio,

    header=linha_cab

)



print(

    "Registros:",

    len(df)

)



# ============================================================
# CAMPOS
# ============================================================


campos = [

    "Matricula",

    "Localizacao",

    "Bairro",

    "Setor Operacional"

]



base = df[

    [

        c for c in campos

        if c in df.columns

    ]

].copy()



base["LOCALIZACAO"] = (

    base["Localizacao"]

    .apply(texto_seguro)

)



# ============================================================
# SEPARAR BLOCOS
# ============================================================


print("\nSeparando blocos...")


blocos = (

    base["LOCALIZACAO"]

    .str.split(".")

)



for i in range(6):


    base[

        f"BLOCO_{i+1}"

    ] = blocos.apply(

        lambda x:

        x[i]

        if len(x)>i

        else ""

    )



print("\nExemplo:")


print(

    base[

        [

            "LOCALIZACAO",

            "BLOCO_1",

            "BLOCO_2",

            "BLOCO_3",

            "BLOCO_4",

            "BLOCO_5",

            "BLOCO_6"

        ]

    ]

    .head()

)



# ============================================================
# FREQUÊNCIAS
# ============================================================


print("\nCalculando frequências...")


resultados = []



for coluna in [

    "BLOCO_1",

    "BLOCO_2",

    "BLOCO_3",

    "BLOCO_4",

    "BLOCO_5",

    "BLOCO_6"

]:


    temp = (

        base.groupby(

            coluna

        )

        .size()

        .reset_index()

    )


    temp.columns = [

        "VALOR",

        "QUANTIDADE"

    ]


    temp["CAMPO"] = coluna


    resultados.append(temp)



frequencias = pd.concat(

    resultados,

    ignore_index=True

)



# ============================================================
# RELAÇÃO COM SETOR OPERACIONAL
# ============================================================


print("\nRelacionando Setor Operacional...")


if "Setor Operacional" in base.columns:


    relacoes = (

        base.groupby(

            [

                "Setor Operacional",

                "BLOCO_3"

            ]

        )

        .size()

        .reset_index()

    )


    relacoes.columns = [

        "SETOR_OPERACIONAL",

        "BLOCO_3",

        "QUANTIDADE"

    ]


else:


    relacoes = pd.DataFrame()



# ============================================================
# SALVAR
# ============================================================


arquivo_saida = os.path.join(

    RESULTADOS,

    "diagnostico_blocos_localizacao.xlsx"

)



arquivo_freq = os.path.join(

    RESULTADOS,

    "frequencia_blocos_localizacao.xlsx"

)



with pd.ExcelWriter(

    arquivo_saida

) as writer:


    base.head(10000).to_excel(

        writer,

        sheet_name="amostra_blocos",

        index=False

    )


    relacoes.to_excel(

        writer,

        sheet_name="setor_operacional",

        index=False

    )



frequencias.to_excel(

    arquivo_freq,

    index=False

)



print("\nArquivos gerados:")

print("-", arquivo_saida)

print("-", arquivo_freq)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 83.")