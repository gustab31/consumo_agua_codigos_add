# ============================================================
# AUDITORIA DE GRUPOS DE ENDEREÇO
# ============================================================

import pandas as pd
import os
import re
import unicodedata
import time


inicio = time.time()


print("="*60)
print("AUDITORIA DE GRUPOS DE ENDEREÇO")
print("="*60)



# ============================================================
# ARQUIVOS
# ============================================================

BASE = "resultados/base_residencial_setor_endereco_cep_v3.csv"

SAIDA_GRUPOS = "resultados/grupos_endereco_auditoria.csv"

SAIDA_RESUMO = "resultados/resumo_grupos_endereco.csv"



# ============================================================
# FUNÇÃO NORMALIZAÇÃO
# ============================================================

def normalizar(valor):

    if pd.isna(valor):
        return ""

    valor = str(valor).upper()

    valor = unicodedata.normalize(
        "NFKD",
        valor
    ).encode(
        "ASCII",
        "ignore"
    ).decode(
        "ASCII"
    )

    valor = re.sub(
        r"[^A-Z0-9]",
        "",
        valor
    )

    return valor



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base...")


df = pd.read_csv(
    BASE,
    low_memory=False
)


print("Shape:")
print(df.shape)



# ============================================================
# CRIAR CHAVES
# ============================================================


print("\nCriando chaves...")


df["CHAVE_END_NUM"] = (

    df["Endereco"]
    .fillna("")
    .apply(normalizar)

)



df["CHAVE_END_BAIRRO"] = (

    df["Endereco"]
    .fillna("")
    .apply(normalizar)

    +

    "_"

    +

    df["Bairro"]
    .fillna("")
    .apply(normalizar)

)



df["CHAVE_RUA_BAIRRO"] = (

    df["Endereco"]
    .fillna("")
    .apply(normalizar)

    +

    "_"

    +

    df["Bairro"]
    .fillna("")
    .apply(normalizar)

)



# ============================================================
# GRUPO ENDEREÇO COMPLETO
# ============================================================


print("\nAgrupando endereços...")


grupo = (

    df.groupby(
        "CHAVE_END_BAIRRO"
    )

    .agg(

        total_matriculas=(
            "MATRICULA",
            "nunique"
        ),

        total_registros=(
            "MATRICULA",
            "count"
        ),

        bairros=(
            "Bairro",
            "first"
        ),

        endereco_original=(
            "Endereco",
            "first"
        ),

        cep_exemplos=(
            "CEP",
            "first"
        ),

        setores_existentes=(
            "CD_SETOR",
            lambda x:
            ";".join(
                x.dropna()
                .astype(str)
                .unique()
            )

        ),

        quantidade_setores=(
            "CD_SETOR",
            lambda x:
            x.dropna()
            .nunique()
        )

    )

    .reset_index()

)



# ============================================================
# CLASSIFICAÇÃO
# ============================================================


grupo["possui_setor"] = (

    grupo["quantidade_setores"]
    >0

)



grupo["endereco_transferivel"] = (

    grupo["quantidade_setores"]
    ==1

)



# ============================================================
# RESUMO
# ============================================================


resumo = pd.DataFrame({

    "indicador":[

        "total_registros",

        "matriculas_unicas",

        "enderecos_grupo",

        "enderecos_com_mais_de_1_matricula",

        "maior_grupo_matriculas",

        "grupos_com_setor",

        "grupos_transferiveis"

    ],


    "valor":[

        len(df),

        df["MATRICULA"].nunique(),

        len(grupo),

        (grupo["total_matriculas"]>1)
        .sum(),

        grupo["total_matriculas"]
        .max(),

        grupo["possui_setor"]
        .sum(),

        grupo["endereco_transferivel"]
        .sum()

    ]

})



print("\n")
print("="*60)
print("RESUMO")
print("="*60)

print(resumo)



# ============================================================
# MAIORES GRUPOS
# ============================================================


print("\nMaiores grupos:")


print(

    grupo

    .sort_values(
        "total_matriculas",
        ascending=False
    )

    .head(20)

)



# ============================================================
# SALVAR
# ============================================================


grupo.to_csv(
    SAIDA_GRUPOS,
    index=False,
    encoding="utf-8-sig"
)


resumo.to_csv(
    SAIDA_RESUMO,
    index=False,
    encoding="utf-8-sig"
)



print("\nArquivos:")

print(SAIDA_GRUPOS)

print(SAIDA_RESUMO)



print("\nTempo:")

print(
    round(
        time.time()-inicio,
        2
    ),
    "segundos"
)


print("\nFim.")