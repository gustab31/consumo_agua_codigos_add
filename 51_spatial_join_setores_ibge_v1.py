# ============================================================
# localizar shapefile
# ============================================================

import os

print("="*60)
print("PROCURANDO SHAPEFILES")
print("="*60)

for raiz, pastas, arquivos in os.walk("."):

    for arquivo in arquivos:

        if arquivo.lower().endswith(".shp"):

            print(
                os.path.join(
                    raiz,
                    arquivo
                )
            )

print("\nFim.")