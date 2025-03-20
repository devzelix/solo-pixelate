from PIL import Image, ImageDraw, ImageFont
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

def obtener_color_mas_cercano(pixel, colores):
    kdtree = KDTree(colores)
    return colores[kdtree.query(pixel)[1]]

def recolorear_imagen(ruta_imagen, colores_representativos):
    imagen = Image.open(ruta_imagen).convert("RGB")
    pixeles_formateados = np.array(imagen)
    lista_pixeles = pixeles_formateados.tolist()
    lista_pixeles_recoloreados = [[obtener_color_mas_cercano(pixel, colores_representativos) for pixel in fila] for fila in lista_pixeles]
    pixeles_recoloreados_formateados = np.array(lista_pixeles_recoloreados, dtype=np.uint8)
    nueva_imagen = Image.fromarray(pixeles_recoloreados_formateados)
    nueva_imagen.save("imagen_recoloreada.png")

def pixelar_imagen(ruta_imagen):
    original_image = Image.open(ruta_imagen)
    small_image = original_image.resize((original_image.width // 20, original_image.height // 20), resample=Image.NEAREST)
    pixelated_image = small_image.resize((original_image.width, original_image.height), resample=Image.NEAREST)
    pixelated_image.save("imagen_pixelada.png")

def obtener_colores(lista_pixeles):
    lista_colores = []
    for fila in lista_pixeles:
        for pixel in fila:
            if not pixel in lista_colores:
                lista_colores.append(pixel)
    return lista_colores

def obtener_numeros_colores(ruta_imagen):
    imagen = Image.open(ruta_imagen).convert("RGB")
    pixeles = np.array(imagen)
    lista_colores = obtener_colores(pixeles.tolist())
    diccionario_colores = {}
    for i in range(len(lista_colores)):
        diccionario_colores[str(i + 1)] = tuple(lista_colores[i])
    return diccionario_colores

def determinar_color_bloque(imagen, x, y, ancho, alto, colores):
    suma_rojo, suma_verde, suma_azul = 0, 0, 0
    cantidad_pixeles = 0
    for j in range(y, min(y + 20, alto)):
        for i in range(x, min(x + 20, ancho)):
            color = imagen.getpixel((i, j))
            suma_rojo += color[0]
            suma_verde += color[1]
            suma_azul += color[2]
            cantidad_pixeles += 1
    color_promedio = (suma_rojo // cantidad_pixeles, suma_verde // cantidad_pixeles, suma_azul // cantidad_pixeles)
    return obtener_color_mas_cercano(color_promedio, colores)

def encasillar_numeros(ruta_imagen, diccionario_colores):
    imagen = Image.open(ruta_imagen)
    ancho, alto = imagen.size
    nuevo_ancho = ancho + ((20 - (ancho % 20)) % 20)
    nuevo_alto = round(nuevo_ancho / (ancho / alto)) + ((20 - (round(nuevo_ancho / (ancho / alto)) % 20)) % 20)
    imagen = imagen.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    imagen_resultante = Image.new("RGB", (nuevo_ancho, nuevo_alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(imagen_resultante)
    try:
        fuente = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except IOError:
        fuente = ImageFont.load_default()
    for y in range(0, nuevo_alto, 20):
        for x in range(0, nuevo_ancho, 20):
            color_bloque = determinar_color_bloque(imagen, x, y, ancho, alto, list(diccionario_colores.values()))
            numero_correspondiente = next((k for k, v in diccionario_colores.items() if v == color_bloque), None)
            bbox = draw.textbbox((0, 0), numero_correspondiente, font=fuente)
            ancho_texto = bbox[2] - bbox[0]
            alto_texto = bbox[3] - bbox[1]
            posicion_texto = (x + (20 - ancho_texto) // 2, y + (20 - alto_texto) // 2 - 2)
            draw.text(posicion_texto, numero_correspondiente, font=fuente, fill=(0, 0, 0))
            draw.rectangle([x, y, x + 19, y + 19], outline=(0, 0, 0), width=1)
    imagen_resultante.save("imagen_colorear.png")

def generar_paleta(diccionario_colores):
    numeros = list(diccionario_colores.keys())
    colores = list(diccionario_colores.values())
    ancho = 5 * 50
    filas = (len(colores) + ((5 - (len(colores) % 5)) % 5)) // 5
    alto = filas * 50
    imagen = Image.new("RGB", (ancho, alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(imagen)
    try:
        fuente = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
    except IOError:
        fuente = ImageFont.load_default()
    i = 0
    for fila in range(filas):
        for columna in range(5):
            x0 = columna * 50
            y0 = fila * 50
            x1 = x0 + 49
            y1 = y0 + 49
            if i < len(colores):
                color = colores[i]
                draw.rectangle([x0, y0, x1, y1], fill=color, outline=(0, 0, 0))
                numero_correspondiente = numeros[i]
                bbox = draw.textbbox((0, 0), numero_correspondiente, font=fuente)
                ancho_texto = bbox[2] - bbox[0]
                alto_texto = bbox[3] - bbox[1]
                posicion_texto = (x0 + (50 - ancho_texto) // 2, y0 + (50 - alto_texto) // 2 - 2)
                draw.text(posicion_texto, numero_correspondiente, font=fuente, fill=(0, 0, 0))
                i += 1
    imagen.save("paleta_colores.png")

def main():
    # try:
    ruta_imagen = input("Ingrese la ruta de la imagen: ")
    colores_representativos = obtener_colores_representativos(ruta_imagen)
    recolorear_imagen(ruta_imagen, colores_representativos)
    pixelar_imagen("imagen_recoloreada.png")
    diccionario_colores = obtener_numeros_colores("imagen_pixelada.png")
    encasillar_numeros("imagen_pixelada.png", diccionario_colores)
    generar_paleta(diccionario_colores)
    # except FileNotFoundError:
    #     print("Error: La imagen no fue encontrada. Verifica la ruta e inténtalo nuevamente.")
    # except Exception as e:
    #     print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()