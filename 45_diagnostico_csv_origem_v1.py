# ============================================================
# 45_diagnostico_csv_origem_v1.py
#
# LEITURA DOS CSV ORIGINAIS
#
# ============================================================


import pandas as pd
import time
import os


inicio = time.time()


print("="*70)
print("DIAGNOSTICO CSV ORIGINAIS")
print("="*70)



arquivos = [

    "abr22 a maio24.csv",

    "fev20 a mar22.csv"

]



saida = "diagnostico_csv_origem_v1.csv"

saida_colunas = "diagnostico_csv_colunas_v1.csv"



resultado=[]

colunas=[]



for arquivo in arquivos:


    print("\n")

    print("="*60)

    print("Arquivo:", arquivo)

    print("="*60)



    df=None

    encoding_usado=None



    for enc in [

        "utf-8",

        "latin1",

        "cp1252"

    ]:


        try:

            print(

                "Tentando:",

                enc

            )


            df=pd.read_csv(

                arquivo,

                encoding=enc,

                low_memory=False,

                nrows=5

            )


            encoding_usado=enc

            break


        except Exception as e:

            pass



    if df is None:


        print(

            "Não foi possível abrir"

        )

        continue



    print(

        "Encoding:",

        encoding_usado

    )


    print(

        "Colunas:"

    )


    for c in df.columns:

        print("-",c)


    # conta linhas

    total = pd.read_csv(

        arquivo,

        encoding=encoding_usado,

        low_memory=False

    ).shape[0]



    print(

        "Linhas:",

        total

    )



    resultado.append({

        "arquivo":arquivo,

        "encoding":encoding_usado,

        "linhas":total,

        "colunas":len(df.columns)

    })



    for c in df.columns:


        colunas.append({

            "arquivo":arquivo,

            "coluna":c

        })





pd.DataFrame(resultado).to_csv(

    saida,

    index=False,

    encoding="utf-8-sig"

)


pd.DataFrame(colunas).to_csv(

    saida_colunas,

    index=False,

    encoding="utf-8-sig"

)



print("\n")

print("="*70)

print("Arquivos gerados:")

print(saida)

print(saida_colunas)



print("\nTempo:")

print(

    round(

        time.time()-inicio,

        2

    ),

    "segundos"

)


print("\nFim.")