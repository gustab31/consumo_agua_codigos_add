# ============================================================
# 102_estatisticas_consumo_setor_v2.py
#
# ESTATISTICAS FINAIS CONSUMO x SETOR CENSITARIO
#
# Entrada:
# resultados_04/base_final_consumo_setor.csv
#
# ============================================================


import os
import time
import pandas as pd
import matplotlib.pyplot as plt


inicio = time.time()


print("="*70)
print("ESTATISTICAS FINAIS CONSUMO x SETOR CENSITARIO")
print("="*70)



# ============================================================
# CONFIGURACAO
# ============================================================


PASTA = "resultados_04"


arquivo = os.path.join(
    PASTA,
    "base_final_consumo_setor.csv"
)



# ============================================================
# LEITURA
# ============================================================


print("\nLendo base final...")


if not os.path.exists(arquivo):

    raise FileNotFoundError(
        arquivo
    )


df = pd.read_csv(
    arquivo,
    encoding="utf-8-sig",
    low_memory=False
)



print(
    "Registros:",
    len(df)
)



print("\nColunas:")

for c in df.columns:
    print("-", c)



# ============================================================
# FILTRO SETORES SUSPEITOS
# ============================================================


print("\nFiltrando setores suspeitos...")


total_inicial = len(df)



if "SETOR_SUSPEITO" in df.columns:

    df = df[
        df["SETOR_SUSPEITO"] != True
    ].copy()



print(
    "Após filtro:",
    len(df)
)



# ============================================================
# PREPARAR L/HAB/DIA
# ============================================================


campo = "L_HAB_DIA_FILTRADO"



if campo not in df.columns:

    raise Exception(
        f"Campo {campo} não encontrado"
    )



df[campo] = pd.to_numeric(
    df[campo],
    errors="coerce"
)



df = df.dropna(
    subset=[campo]
)



serie = df[campo]



print(
    "Setores analisados:",
    len(serie)
)



# ============================================================
# CLASSES
# ============================================================


def classe(valor):

    if valor < 100:
        return "Baixo"

    elif valor < 250:
        return "Normal"

    elif valor < 500:
        return "Elevado"

    else:
        return "Muito elevado"



df["CLASSE_CONSUMO"] = (
    serie.apply(classe)
)



classes = (
    df["CLASSE_CONSUMO"]
    .value_counts()
    .reset_index()
)



classes.columns = [
    "CLASSE",
    "QUANTIDADE"
]



classes.to_csv(
    os.path.join(
        PASTA,
        "102_classes_consumo.csv"
    ),
    index=False,
    encoding="utf-8-sig"
)



# ============================================================
# TABELA ESTATISTICA DESCRITIVA
# ============================================================


print("\nCalculando estatisticas...")


media = serie.mean()

desvio = serie.std()

cv = (
    desvio / media
) * 100



tabela = pd.DataFrame(

    {

    "Estatistica":[

        "Numero de setores",

        "Minimo",

        "Media",

        "Mediana",

        "Desvio padrao",

        "1º Quartil (Q1)",

        "3º Quartil (Q3)",

        "Maximo",

        "Coeficiente de variacao (%)"

    ],


    "Valor (L/hab./dia)":[

        len(serie),

        serie.min(),

        media,

        serie.median(),

        desvio,

        serie.quantile(0.25),

        serie.quantile(0.75),

        serie.max(),

        cv

    ]

    }

)



tabela["Valor (L/hab./dia)"] = (
    tabela["Valor (L/hab./dia)"]
    .round(2)
)



tabela.to_csv(

    os.path.join(

        PASTA,

        "102_tabela_estatistica_descritiva.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



with open(

    os.path.join(

        PASTA,

        "102_tabela_estatistica_descritiva.txt"

    ),

    "w",

    encoding="utf-8"

) as f:


    f.write(
        "Estatísticas descritivas do consumo médio diário de água nos setores censitários\n"
    )

    f.write("="*80+"\n\n")

    f.write(
        tabela.to_string(index=False)
    )



# ============================================================
# ESTATISTICAS COMPLETAS
# ============================================================


estat = pd.DataFrame(

    {

    "INDICADOR":[

        "Setores analisados",

        "Media",

        "Mediana",

        "Desvio padrao",

        "Minimo",

        "Q1",

        "Q3",

        "Maximo",

        "CV (%)"

    ],


    "VALOR":[

        len(serie),

        media,

        serie.median(),

        desvio,

        serie.min(),

        serie.quantile(0.25),

        serie.quantile(0.75),

        serie.max(),

        cv

    ]

    }

)



estat.to_csv(

    os.path.join(

        PASTA,

        "102_estatisticas_consumo_setor.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# TOP MAIORES / MENORES
# ============================================================


df.sort_values(

    campo,

    ascending=False

).head(20).to_csv(

    os.path.join(

        PASTA,

        "102_top_maiores_consumo.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



df.sort_values(

    campo,

    ascending=True

).head(20).to_csv(

    os.path.join(

        PASTA,

        "102_top_menores_consumo.csv"

    ),

    index=False,

    encoding="utf-8-sig"

)



# ============================================================
# GRAFICOS
# ============================================================


print("\nGerando gráficos...")



plt.figure(
    figsize=(9,6)
)


plt.hist(

    serie,

    bins=40,

    color="steelblue",

    edgecolor="black"

)


plt.xlabel(
    "L/hab/dia"
)


plt.ylabel(
    "Número de setores"
)


plt.title(
    "Distribuição do consumo por setor censitário"
)


plt.grid(alpha=0.3)


plt.tight_layout()


plt.savefig(

    os.path.join(

        PASTA,

        "102_histograma_lhabdia.png"

    ),

    dpi=300

)


plt.close()



plt.figure(
    figsize=(8,4)
)


plt.boxplot(

    serie,

    vert=False

)


plt.xlabel(
    "L/hab/dia"
)


plt.title(
    "Boxplot consumo por setor censitário"
)


plt.grid(alpha=0.3)


plt.tight_layout()


plt.savefig(

    os.path.join(

        PASTA,

        "102_boxplot_lhabdia.png"

    ),

    dpi=300

)


plt.close()



# ============================================================
# RELATORIO TXT
# ============================================================


with open(

    os.path.join(

        PASTA,

        "102_resumo_estatistico.txt"

    ),

    "w",

    encoding="utf-8"

) as f:


    f.write(
        "RELATORIO ESTATISTICO CONSUMO SETOR CENSITARIO\n"
    )

    f.write("="*60+"\n\n")

    f.write(
        tabela.to_string(index=False)
    )



# ============================================================
# FINAL
# ============================================================


print("\n==============================")
print("ARQUIVOS GERADOS")
print("==============================")


print("102_estatisticas_consumo_setor.csv")
print("102_classes_consumo.csv")
print("102_resumo_estatistico.txt")
print("102_tabela_estatistica_descritiva.csv")
print("102_tabela_estatistica_descritiva.txt")
print("102_top_maiores_consumo.csv")
print("102_top_menores_consumo.csv")
print("102_histograma_lhabdia.png")
print("102_boxplot_lhabdia.png")



print("\nResumo final:")

print(
    "Setores analisados:",
    len(serie)
)


print(
    "Media:",
    round(media,2)
)


print(
    "Mediana:",
    round(serie.median(),2)
)


print(
    "CV (%):",
    round(cv,2)
)



print(
    "\nTempo:",
    round(time.time()-inicio,2),
    "segundos"
)


print("\nFim Código 102 v2.")