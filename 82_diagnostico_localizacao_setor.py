# ============================================================
# 82_diagnostico_localizacao_setor.py
#
# DIAGNÓSTICO LOCALIZACAO x SETOR CENSITÁRIO
#
# Entrada:
#   resultados/consumo_com_endereco.csv
#   joinville_setores_mapa.shp
#   2022.06.29. relatorio 75 1.xlsx
#
# Saídas:
#   diagnostico_localizacao.xlsx
#   amostra_localizacao.xlsx
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
print("DIAGNÓSTICO LOCALIZACAO x SETOR CENSITÁRIO")
print("="*70)



RESULTADOS = "resultados"


os.makedirs(
    RESULTADOS,
    exist_ok=True
)



arquivo_relatorio = (
    "2022.06.29. relatorio 75 1.xlsx"
)



# ============================================================
# FUNÇÃO TEXTO SEGURA
# ============================================================


def texto_seguro(valor):

    if pd.isna(valor):

        return ""

    return str(valor)



# ============================================================
# LER RELATÓRIO
# ============================================================


print("\nLendo Relatório 75...")



bruto = pd.read_excel(

    arquivo_relatorio,

    header=None

)



print(

    "Dimensão bruto:",

    bruto.shape

)



print("\nProcurando cabeçalho real...")



linha_cab = None



for i in range(min(15, len(bruto))):


    valores = (

        bruto.iloc[i]

        .apply(texto_seguro)

        .tolist()

    )


    texto = " ".join(valores).lower()



    if (

        "matricula" in texto

        and "localizacao" in texto

    ):

        linha_cab = i

        break



if linha_cab is None:

    raise Exception(

        "Não foi encontrado cabeçalho do Relatório 75."

    )



print(

    "Cabeçalho encontrado:",

    linha_cab

)



df = pd.read_excel(

    arquivo_relatorio,

    header=linha_cab

)



print(

    "Linhas:",

    len(df)

)



print("\nColunas:")

for c in df.columns:

    print("-", c)



# ============================================================
# CAMPOS
# ============================================================


campos_desejados = [

    "Matricula",

    "Localizacao",

    "Endereco",

    "Bairro",

    "Inscricao_imobiliaria",

    "Setor Operacional",

    "DMC"

]



campos = [

    c for c in campos_desejados

    if c in df.columns

]



base = df[campos].copy()



print(

    "\nCampos utilizados:",

    campos

)



# ============================================================
# LOCALIZACAO
# ============================================================


print("\nAnalisando Localizacao...")



base["LOCALIZACAO_STR"] = (

    base["Localizacao"]

    .apply(texto_seguro)

)



base["TAMANHO_LOCALIZACAO"] = (

    base["LOCALIZACAO_STR"]

    .str.len()

)



base["QTD_PONTOS"] = (

    base["LOCALIZACAO_STR"]

    .str.count(r"\.")

)



base["PREFIXO"] = (

    base["LOCALIZACAO_STR"]

    .str[:5]

)



print("\nResumo Localizacao:")



print(

    base[

        [

            "TAMANHO_LOCALIZACAO",

            "QTD_PONTOS"

        ]

    ]

    .describe()

)



# ============================================================
# PADRÕES
# ============================================================


base["TEM_PADRAO_LOCALIZACAO"] = (

    base["LOCALIZACAO_STR"]

    .str.match(

        r"^\d+\.\d+\.\d+\."

    )

)



print("\nPadrão Localizacao:")


print(

    base["TEM_PADRAO_LOCALIZACAO"]

    .value_counts()

)



# ============================================================
# SETOR OPERACIONAL
# ============================================================


print("\nAnalisando Setor Operacional...")


if "Setor Operacional" in base.columns:


    print(

        "Setores operacionais:",

        base["Setor Operacional"]

        .nunique()

    )


    setor_operacional = (

        base.groupby(

            "Setor Operacional"

        )

        .size()

        .reset_index()

    )


    setor_operacional.columns = [

        "SETOR_OPERACIONAL",

        "QUANTIDADE"

    ]



else:


    setor_operacional = pd.DataFrame()



# ============================================================
# BAIRRO
# ============================================================


bairro = (

    base.groupby(

        "Bairro"

    )

    .size()

    .reset_index()

)



bairro.columns = [

    "BAIRRO",

    "QUANTIDADE"

]



# ============================================================
# AMOSTRA
# ============================================================


amostra = base.sample(

    min(

        1000,

        len(base)

    ),

    random_state=1

)



arquivo_amostra = os.path.join(

    RESULTADOS,

    "amostra_localizacao.xlsx"

)



amostra.to_excel(

    arquivo_amostra,

    index=False

)



# ============================================================
# SALVAR
# ============================================================


arquivo_saida = os.path.join(

    RESULTADOS,

    "diagnostico_localizacao.xlsx"

)



with pd.ExcelWriter(

    arquivo_saida

) as writer:


    base.head(5000).to_excel(

        writer,

        sheet_name="amostra",

        index=False

    )


    setor_operacional.to_excel(

        writer,

        sheet_name="setor_operacional",

        index=False

    )


    bairro.to_excel(

        writer,

        sheet_name="bairro",

        index=False

    )



print("\nArquivos gerados:")

print(

    "-",

    arquivo_saida

)

print(

    "-",

    arquivo_amostra

)



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)



print("\nFim Código 82.")