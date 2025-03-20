from PIL import Image
from scipy.cluster.vq import kmeans
from scipy.spatial import KDTree
import numpy as np

def obtener_colores_representativos(ruta_imagen, k=80):
    imagen = Image.open(ruta_imagen).convert("RGB")
    pixeles = np.array(imagen).reshape(-1, 3)
    pixeles = np.unique(pixeles, axis=0)
    k = min(len(pixeles), k)
    centroides, _ = kmeans(pixeles.astype(float), k)
    colores = [tuple(map(int, c)) for c in centroides]
    return colores

def obtener_color_mas_cercano(pixel, colores_representativos):
    kdtree = KDTree(colores_representativos)
    color_mas_cercano = colores_representativos[kdtree.query(pixel)[1]]
    if color_mas_cercano in colores_representativos:
        return color_mas_cercano
    else:
        raise Exception(f"{color_mas_cercano} no se encuentra en los colores representativos.")

def recolorear_imagen(ruta_imagen, colores_representativos):
    imagen = Image.open(ruta_imagen).convert("RGB")
    pixeles = np.array(imagen)
    pixeles_recoloreados = np.array([obtener_color_mas_cercano(pixel, colores_representativos) for pixel in pixeles.reshape(-1, 3)], dtype=np.uint8)
    pixeles_recoloreados = pixeles_recoloreados.reshape(pixeles.shape)
    nueva_imagen = Image.fromarray(pixeles_recoloreados)
    nueva_imagen.save("imagen_recoloreada.jpg")
    nueva_imagen.show()

def obtener_cantidad_colores(ruta_imagen):
    imagen = Image.open(ruta_imagen).convert("RGB")
    pixeles = np.array(imagen)
    pixeles = pixeles.reshape(-1, 3)
    colores_unicos = np.unique(pixeles, axis=0)
    return colores_unicos

def main():
    try:
        ruta_imagen = input("Ingrese la ruta de la imagen: ").strip()
        print(f"La imagen original tiene {obtener_cantidad_colores(ruta_imagen)} colores.")
        # colores_representativos = obtener_colores_representativos(ruta_imagen)
        # print("\nColores representativos:")
        # for i in range(len(colores_representativos)):
        #     print(f"{"0" * (len(str(len(colores_representativos))) - len(str(i + 1)))}{i + 1} - {colores_representativos[i]}")
        # recolorear_imagen(ruta_imagen, colores_representativos)
        print(f"La imagen recoloreada tiene {obtener_cantidad_colores("imagen_recoloreada.png")} colores.")
    except FileNotFoundError:
        print("Error: La imagen no fue encontrada. Verifica la ruta e inténtalo nuevamente.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()