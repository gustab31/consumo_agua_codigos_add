# ============================================================
# 74_base_unificada_setores_v2.py
#
# BASE MESTRE DOS SETORES CENSITÁRIOS
#
# Etapa:
# - localizar arquivos
# - carregar shapefile
# - carregar IBGE
# - preparar cruzamento por CD_SETOR
#
# ============================================================

import os
import glob
import time
import warnings

import pandas as pd
import geopandas as gpd

warnings.filterwarnings("ignore")

inicio = time.time()

print("=" * 70)
print("BASE UNIFICADA DOS SETORES CENSITÁRIOS")
print("=" * 70)


# ============================================================
# CONFIGURAÇÕES
# ============================================================

PASTA = "."

RESULTADOS = "resultados"

os.makedirs(
    RESULTADOS,
    exist_ok=True
)


# ============================================================
# FUNÇÕES
# ============================================================

def localizar_arquivo(lista_padroes):

    for padrao in lista_padroes:

        arquivos = glob.glob(
            os.path.join(
                PASTA,
                padrao
            )
        )

        if arquivos:

            print(
                "OK:",
                arquivos[0]
            )

            return arquivos[0]

    return None



def encontrar_coluna_setor(df):

    candidatos = [

        "CD_SETOR",
        "cd_setor",
        "CD_GEOCODI",
        "cd_geocodi",
        "SETOR",
        "setor"

    ]

    for c in candidatos:

        if c in df.columns:

            return c


    for c in df.columns:

        nome = str(c).upper()

        if "SETOR" in nome:

            return c


    return None



def padronizar_setor(df, coluna):

    df = df.copy()

    df[coluna] = (

        df[coluna]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()

    )

    return df



# ============================================================
# LOCALIZAR SHAPEFILE
# ============================================================

print("\nLocalizando shapefile...")

arquivo_shp = localizar_arquivo([

    "*joinville_setores_mapa.shp",

    "*Joinville_setores_mapa.shp"

])


if arquivo_shp is None:

    raise FileNotFoundError(
        "Shapefile de setores não encontrado."
    )



# ============================================================
# LOCALIZAR IBGE
# ============================================================

print("\nLocalizando IBGE...")

arquivo_ibge = localizar_arquivo([

    "*Agregados_por_setores*.xlsx",

    "*IBGE*.xlsx"

])


if arquivo_ibge is None:

    raise FileNotFoundError(
        "Arquivo IBGE não encontrado."
    )



# ============================================================
# LOCALIZAR RELATORIO 75
# ============================================================

print("\nLocalizando Relatório 75...")

arquivo_relatorio = localizar_arquivo([

    "*75*.xlsx",

    "*relatorio*.xlsx"

])


# ============================================================
# LOCALIZAR CSV
# ============================================================

print("\nLocalizando CSV...")

csv_periodos = [

    c for c in glob.glob(
        "*.csv"
    )

    if "diagnostico" not in c.lower()

]


for c in csv_periodos:

    print(
        "CSV:",
        c
    )



# ============================================================
# LER SHAPEFILE
# ============================================================

print("\nLendo shapefile...")

gdf = gpd.read_file(
    arquivo_shp
)


print(
    "Registros:",
    len(gdf)
)


col_setor_shape = encontrar_coluna_setor(
    gdf
)


if col_setor_shape is None:

    raise Exception(
        "CD_SETOR não encontrado no shapefile."
    )


gdf = padronizar_setor(
    gdf,
    col_setor_shape
)


gdf.rename(
    columns={
        col_setor_shape:"CD_SETOR"
    },
    inplace=True
)


print(
    "Setores:",
    gdf["CD_SETOR"].nunique()
)


print(
    "Shapefile carregado."
)

# ============================================================
# LEITURA DO IBGE
# ============================================================

print("\n" + "="*70)
print("LENDO BASE IBGE")
print("="*70)


abas_ibge = pd.ExcelFile(
    arquivo_ibge
).sheet_names


print("\nAbas encontradas:")

for aba in abas_ibge:

    print(" -", aba)



ibge_final = None


for aba in abas_ibge:

    print(
        "\nTestando aba:",
        aba
    )


    try:

        df = pd.read_excel(
            arquivo_ibge,
            sheet_name=aba
        )


        print(
            "Linhas:",
            len(df),
            "Colunas:",
            len(df.columns)
        )


        coluna = encontrar_coluna_setor(
            df
        )


        if coluna is not None:

            print(
                "CD_SETOR encontrado:",
                coluna
            )


            ibge_final = df.copy()

            coluna_ibge = coluna

            break


    except Exception as erro:

        print(
            "Erro:",
            erro
        )



if ibge_final is None:

    raise Exception(
        "Não foi possível encontrar CD_SETOR na base IBGE."
    )



# ============================================================
# PADRONIZAÇÃO IBGE
# ============================================================

ibge_final = padronizar_setor(
    ibge_final,
    coluna_ibge
)


ibge_final.rename(
    columns={
        coluna_ibge:"CD_SETOR"
    },
    inplace=True
)



print(
    "\nSetores IBGE:",
    ibge_final["CD_SETOR"].nunique()
)



# ============================================================
# EXPORTAR DIAGNÓSTICO IBGE
# ============================================================


with pd.ExcelWriter(

    os.path.join(
        RESULTADOS,
        "diagnostico_ibge.xlsx"
    )

) as writer:


    pd.DataFrame({

        "coluna":
        ibge_final.columns,

        "tipo":
        ibge_final.dtypes.astype(str)

    }).to_excel(

        writer,
        sheet_name="colunas",
        index=False

    )


    ibge_final.head(100).to_excel(

        writer,
        sheet_name="amostra",

        index=False

    )



print(
    "Diagnóstico IBGE salvo."
)



# ============================================================
# CRUZAMENTO SHAPE + IBGE
# ============================================================

print("\nCruzando setores com IBGE...")


base_setores = gdf.merge(

    ibge_final,

    on="CD_SETOR",

    how="left",

    suffixes=(
        "",
        "_IBGE"
    )

)



print(
    "Setores totais:",
    len(base_setores)
)



colunas_ibge = [

    c for c in ibge_final.columns

    if c != "CD_SETOR"

]



base_setores["tem_ibge"] = (

    base_setores[colunas_ibge]

    .notna()

    .any(axis=1)

)



print(
    "\nCobertura IBGE:"
)


print(

    base_setores["tem_ibge"]

    .value_counts()

)



# ============================================================
# SALVAR BASE INTERMEDIÁRIA
# ============================================================


saida = os.path.join(

    RESULTADOS,

    "base_setores_ibge.gpkg"

)


base_setores.to_file(

    saida,

    driver="GPKG"

)



print(

    "\nArquivo criado:",

    saida

)

# ============================================================
# LEITURA RELATÓRIO 75
# ============================================================

print("\n" + "="*70)
print("LENDO RELATÓRIO 75")
print("="*70)


if arquivo_relatorio is None:

    print(
        "Relatório 75 não encontrado. Pulando etapa."
    )

    relatorio_final = None


else:


    abas_relatorio = pd.ExcelFile(
        arquivo_relatorio
    ).sheet_names


    print("\nAbas encontradas:")

    for aba in abas_relatorio:

        print(" -", aba)



    relatorio_final = None


    for aba in abas_relatorio:


        print(
            "\nTestando aba:",
            aba
        )


        try:


            df = pd.read_excel(

                arquivo_relatorio,

                sheet_name=aba

            )


            print(

                "Linhas:",

                len(df),

                "Colunas:",

                len(df.columns)

            )


            coluna = encontrar_coluna_setor(

                df

            )


            if coluna is not None:


                print(

                    "Setor encontrado:",

                    coluna

                )


                relatorio_final = df.copy()

                coluna_relatorio = coluna

                break



        except Exception as erro:


            print(

                "Erro:",

                erro

            )





    if relatorio_final is not None:


        relatorio_final = padronizar_setor(

            relatorio_final,

            coluna_relatorio

        )


        relatorio_final.rename(

            columns={

                coluna_relatorio:
                "CD_SETOR"

            },

            inplace=True

        )


        print(

            "\nSetores Relatório 75:",

            relatorio_final["CD_SETOR"].nunique()

        )



        with pd.ExcelWriter(

            os.path.join(

                RESULTADOS,

                "diagnostico_relatorio75.xlsx"

            )

        ) as writer:


            pd.DataFrame({

                "coluna":
                relatorio_final.columns,

                "tipo":
                relatorio_final.dtypes.astype(str)

            }).to_excel(

                writer,

                sheet_name="colunas",

                index=False

            )


            relatorio_final.head(100).to_excel(

                writer,

                sheet_name="amostra",

                index=False

            )



        print(
            "Diagnóstico Relatório 75 salvo."
        )



    else:

        print(

            "Não foi encontrada coluna CD_SETOR no Relatório 75."

        )



# ============================================================
# CRUZAMENTO COM BASE DE SETORES
# ============================================================


if relatorio_final is not None:


    print(
        "\nCruzando Relatório 75..."
    )


    base_setores = base_setores.merge(

        relatorio_final,

        on="CD_SETOR",

        how="left",

        suffixes=(

            "",

            "_REL75"

        )

    )


    colunas_rel = [

        c for c in relatorio_final.columns

        if c != "CD_SETOR"

    ]


    base_setores["tem_relatorio75"] = (

        base_setores[colunas_rel]

        .notna()

        .any(axis=1)

    )


    print(

        base_setores["tem_relatorio75"]

        .value_counts()

    )


else:


    base_setores["tem_relatorio75"] = False



print(

    "\nEtapa Relatório 75 concluída."

)

# ============================================================
# LEITURA CSV CAJ
# ============================================================

print("\n" + "="*70)
print("LENDO DADOS DE CONSUMO CAJ")
print("="*70)


lista_caj = []


for arquivo_csv in csv_periodos:


    print(
        "\nLendo:",
        arquivo_csv
    )


    try:


        df = pd.read_csv(

            arquivo_csv,

            sep=None,

            engine="python",

            encoding_errors="ignore"

        )


        print(

            "Registros:",

            len(df)

        )


        print(

            "Colunas:",

            list(df.columns)

        )


        coluna = encontrar_coluna_setor(

            df

        )


        if coluna is not None:


            print(

                "Setor encontrado:",

                coluna

            )


            df = padronizar_setor(

                df,

                coluna

            )


            df.rename(

                columns={

                    coluna:
                    "CD_SETOR"

                },

                inplace=True

            )


            df["arquivo_origem"] = os.path.basename(

                arquivo_csv

            )


            lista_caj.append(df)



        else:


            print(

                "Sem CD_SETOR neste arquivo."

            )



    except Exception as erro:


        print(

            "Erro lendo CSV:",

            erro

        )




# ============================================================
# CONSOLIDAR CAJ
# ============================================================


if lista_caj:


    caj = pd.concat(

        lista_caj,

        ignore_index=True

    )


    print(

        "\nTotal CAJ:",

        len(caj)

    )


    print(

        "Setores CAJ:",

        caj["CD_SETOR"].nunique()

    )



    with pd.ExcelWriter(

        os.path.join(

            RESULTADOS,

            "diagnostico_caj.xlsx"

        )

    ) as writer:


        pd.DataFrame({

            "coluna":
            caj.columns,

            "tipo":
            caj.dtypes.astype(str)

        }).to_excel(

            writer,

            sheet_name="colunas",

            index=False

        )


        caj.head(100).to_excel(

            writer,

            sheet_name="amostra",

            index=False

        )



    print(
        "Diagnóstico CAJ salvo."
    )



    # --------------------------------------------------------
    # Agregação por setor
    # --------------------------------------------------------

    caj_setor = (

        caj

        .groupby("CD_SETOR")

        .size()

        .reset_index(

            name="qtd_registros_caj"

        )

    )


    base_setores = base_setores.merge(

        caj_setor,

        on="CD_SETOR",

        how="left"

    )


    base_setores["tem_caj"] = (

        base_setores["qtd_registros_caj"]

        .fillna(0)

        > 0

    )


else:


    print(

        "Nenhum CSV com CD_SETOR encontrado."

    )


    base_setores["tem_caj"] = False



# ============================================================
# TXT
# ============================================================

print("\nLendo TXT...")


txts = glob.glob(

    "*.txt"

)


if txts:


    arquivo_txt = txts[0]


    try:


        with open(

            arquivo_txt,

            "r",

            encoding="utf-8",

            errors="ignore"

        ) as f:


            linhas = f.readlines()



        pd.DataFrame({

            "texto":

            linhas

        }).to_excel(

            os.path.join(

                RESULTADOS,

                "diagnostico_txt.xlsx"

            ),

            index=False

        )


        print(

            "TXT salvo."

        )


    except Exception as erro:


        print(

            "Erro TXT:",

            erro

        )



# ============================================================
# EXPORTAÇÃO FINAL DO 74
# ============================================================

print("\nSalvando base mestre...")


saida_final = os.path.join(

    RESULTADOS,

    "base_mestre_setores_74.gpkg"

)



base_setores.to_file(

    saida_final,

    driver="GPKG"

)



print(
    "\nArquivo final:"
)

print(
    saida_final
)



print(

    "\nResumo final"

)


print(

    "Setores:",
    len(base_setores)

)


for c in [

    "tem_ibge",

    "tem_relatorio75",

    "tem_caj"

]:

    if c in base_setores.columns:

        print(

            c,

            base_setores[c].sum()

        )



print(

    "\nTempo:",

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim do Código 74.")