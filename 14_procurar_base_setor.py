import os
import pandas as pd


pasta = "resultados"


print("="*60)
print("PROCURANDO BASE COM CD_SETOR")
print("="*60)


for raiz, pastas, arquivos in os.walk("."):

    for arquivo in arquivos:

        if arquivo.endswith(".csv"):

            caminho = os.path.join(
                raiz,
                arquivo
            )

            try:

                df = pd.read_csv(
                    caminho,
                    nrows=5,
                    low_memory=False
                )

                cols = list(df.columns)


                tem_setor = (
                    "CD_SETOR" in cols
                )

                tem_matricula = any(
                    "matricula" in c.lower()
                    for c in cols
                )


                if tem_setor and tem_matricula:

                    df2 = pd.read_csv(
                        caminho,
                        usecols=[
                            c for c in cols
                            if "matricula" in c.lower()
                            or c=="CD_SETOR"
                        ],
                        low_memory=False
                    )


                    print("\nEncontrado:")
                    print(caminho)

                    print(
                        "Linhas:",
                        len(df2)
                    )

                    print(
                        "Colunas:",
                        df2.columns.tolist()
                    )


            except Exception:
                pass