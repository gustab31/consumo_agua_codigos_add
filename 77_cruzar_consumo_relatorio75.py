# ============================================================
# 77_cruzar_consumo_relatorio75.py
#
# CRUZAMENTO:
#
# CONSUMO CAJ
#      |
#      | MATRÍCULA
#      ↓
# RELATÓRIO 75
#
# Resultado:
# consumo com endereço/localização
#
# ============================================================


import os
import time
import warnings

import pandas as pd


warnings.filterwarnings("ignore")


inicio = time.time()


print("=" * 70)
print("CRUZAMENTO CONSUMO x RELATÓRIO 75")
print("=" * 70)



# ============================================================
# CONFIGURAÇÃO
# ============================================================


RESULTADOS = "resultados"

os.makedirs(
    RESULTADOS,
    exist_ok=True
)



arquivo_relatorio = (

    "2022.06.29. relatorio 75 1.xlsx"

)



arquivos_csv = [

    "fev20 a mar22.csv",

    "abr22 a maio24.csv"

]



# ============================================================
# LER RELATÓRIO 75
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



print(

    "\nProcurando linha de cabeçalho..."

)



linha_cabecalho = None



for i in range(len(bruto)):


    linha = (

        bruto.iloc[i]

        .fillna("")

        .astype(str)

        .str.lower()

        .tolist()

    )


    texto = " ".join(linha)



    if "matricula" in texto:


        linha_cabecalho = i

        break




if linha_cabecalho is None:


    raise Exception(

        "Não encontrou cabeçalho com Matricula."

    )



print(

    "Cabeçalho encontrado na linha:",

    linha_cabecalho

)



# ============================================================
# REABRIR COM CABEÇALHO CORRETO
# ============================================================


rel = pd.read_excel(

    arquivo_relatorio,

    header=linha_cabecalho

)



# ============================================================
# LIMPEZA DAS COLUNAS
# ============================================================


novas_colunas = []


for c in rel.columns:


    if pd.isna(c):

        novas_colunas.append(

            "COLUNA_VAZIA"

        )

    else:

        novas_colunas.append(

            str(c).strip()

        )



rel.columns = novas_colunas



print("\nColunas encontradas:")


for c in rel.columns:

    print("-", c)



# ============================================================
# IDENTIFICAR MATRÍCULA
# ============================================================


col_matricula = None



for c in rel.columns:


    if "matricula" in str(c).lower():

        col_matricula = c

        break




if col_matricula is None:


    raise Exception(

        "Coluna MATRICULA não encontrada."

    )



print(

    "\nColuna matrícula encontrada:",

    col_matricula

)



rel.rename(

    columns={

        col_matricula:

        "MATRICULA"

    },

    inplace=True

)



rel["MATRICULA"] = (

    rel["MATRICULA"]

    .astype(str)

    .str.strip()

)



print(

    "Matrículas Relatório 75:",

    rel["MATRICULA"].nunique()

)



# ============================================================
# CAMPOS DE INTERESSE
# ============================================================


campos = [

    "MATRICULA",

    "Localizacao",

    "Endereco",

    "Bairro",

    "CEP",

    "Inscricao_imobiliaria",

    "Setor Operacional",

    "DMC"

]



campos_existentes = [

    c for c in campos

    if c in rel.columns

]



print(

    "\nCampos utilizados:",

    campos_existentes

)



rel_reduzido = rel[

    campos_existentes

].copy()


# ============================================================
# LER CSV CONSUMO
# ============================================================


print("\nLendo arquivos de consumo...")


lista_consumo = []



for arquivo in arquivos_csv:


    print(

        "\nArquivo:",

        arquivo

    )


    consumo_temp = pd.read_csv(

        arquivo,

        sep=None,

        engine="python",

        encoding_errors="ignore"

    )


    print(

        "Registros:",

        len(consumo_temp)

    )



    if "MATRICULA" not in consumo_temp.columns:


        raise Exception(

            "Arquivo sem coluna MATRICULA: "

            + arquivo

        )



    consumo_temp["MATRICULA"] = (

        consumo_temp["MATRICULA"]

        .astype(str)

        .str.strip()

    )



    consumo_temp["arquivo_origem"] = (

        os.path.basename(arquivo)

    )



    lista_consumo.append(

        consumo_temp

    )




consumo = pd.concat(

    lista_consumo,

    ignore_index=True

)



print(

    "\nConsumo total:",

    len(consumo)

)



print(

    "Matrículas consumo:",

    consumo["MATRICULA"].nunique()

)



# ============================================================
# CRUZAMENTO
# ============================================================


print(

    "\nCruzando MATRÍCULA..."

)



base = consumo.merge(

    rel_reduzido,

    on="MATRICULA",

    how="left",

    indicator=True

)



# ============================================================
# DIAGNÓSTICO DO MATCH
# ============================================================


print(

    "\nResultado do cruzamento:"

)


print(

    base["_merge"]

    .value_counts()

)



base["tem_relatorio75"] = (

    base["_merge"]

    == "both"

)



base.drop(

    columns=["_merge"],

    inplace=True

)



print(

    "\nRegistros com Relatório 75:",

    base["tem_relatorio75"].sum()

)



print(

    "Registros sem Relatório 75:",

    (

        ~base["tem_relatorio75"]

    ).sum()

)



print(

    "\nMatrículas com Relatório 75:",

    base.loc[

        base["tem_relatorio75"],

        "MATRICULA"

    ]

    .nunique()

)



print(

    "Matrículas sem Relatório 75:",

    base.loc[

        ~base["tem_relatorio75"],

        "MATRICULA"

    ]

    .nunique()

)



# ============================================================
# VERIFICAR ENDEREÇO
# ============================================================


campos_endereco = [

    c for c in campos_existentes

    if c != "MATRICULA"

]



base["tem_endereco"] = (

    base[campos_endereco]

    .notna()

    .any(axis=1)

)



print(

    "\nCobertura endereço:"

)


print(

    base["tem_endereco"]

    .value_counts()

)



# ============================================================
# SALVAR RESULTADO
# ============================================================


saida = os.path.join(

    RESULTADOS,

    "consumo_com_endereco.csv"

)



base.to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)



print(

    "\nArquivo criado:",

    saida

)



# ============================================================
# RESUMO
# ============================================================


print("\nResumo final")

print(

    "Linhas:",

    len(base)

)

print(

    "Colunas:",

    len(base.columns)

)


print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim Código 77.")