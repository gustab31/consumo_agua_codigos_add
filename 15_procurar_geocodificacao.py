import os
import pandas as pd


print("="*60)
print("PROCURANDO BASES COM ENDEREÇO / COORDENADAS")
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


                cols = [
                    c.lower()
                    for c in df.columns
                ]


                tem_matricula = any(
                    "matricula" in c
                    for c in cols
                )


                tem_endereco = any(
                    "endereco" in c
                    or "logradouro" in c
                    or "localizacao" in c
                    for c in cols
                )


                tem_coord = (
                    any(
                        "latitude" in c
                        for c in cols
                    )
                    or
                    any(
                        "longitude" in c
                        for c in cols
                    )
                )


                if tem_matricula and (
                    tem_endereco or tem_coord
                ):

                    df2 = pd.read_csv(
                        caminho,
                        nrows=1,
                        low_memory=False
                    )


                    print("\nEncontrado:")
                    print(caminho)

                    print(
                        "Colunas:",
                        df2.columns.tolist()
                    )


            except Exception:
                pass