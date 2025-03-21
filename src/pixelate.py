from PIL import Image, ImageDraw, ImageFont
from scipy.cluster.vq import kmeans
from scipy.spatial import KDTree
import numpy as np
import os

Image.MAX_IMAGE_PIXELS = None

def abrir_imagen(ruta_imagen):
    imagen = Image.open(ruta_imagen).convert("RGB")
    if imagen.width * imagen.height > 100000000:
        ancho = imagen.width
        alto = imagen.height
        return imagen.resize((round(ancho // 4), round(round(ancho // 4) / (ancho / alto))))
    else:
        return imagen

def redimensionar_imagen(ruta_imagen_original, ruta_imagen_nueva):
    imagen_original = Image.open(ruta_imagen_original)
    ancho = imagen_original.width
    imagen_nueva = Image.open(ruta_imagen_nueva)
    imagen_redimensionada = imagen_nueva.resize((ancho, round(ancho / (imagen_nueva.width / imagen_nueva.height))))
    imagen_redimensionada = imagen_redimensionada.convert("RGB")
    imagen_redimensionada.save(ruta_imagen_nueva)

def obtener_colores_representativos(ruta_imagen, k=80):
    imagen = abrir_imagen(ruta_imagen)
    pixeles = np.array(imagen).reshape(-1, 3)
    pixeles = np.unique(pixeles, axis=0)
    k = min(len(pixeles), k)
    centroides, _ = kmeans(pixeles.astype(float), k)
    colores = [tuple(map(int, c)) for c in centroides]
    return colores

def obtener_color_mas_cercano(pixel, colores):
    kdtree = KDTree(colores)
    return colores[kdtree.query(pixel)[1]]

def recolorear_imagen(ruta_imagen_original, ruta_imagen_recoloreada, colores_representativos):
    imagen_original = abrir_imagen(ruta_imagen_original)
    pixeles_formateados = np.array(imagen_original)
    lista_pixeles = pixeles_formateados.tolist()
    lista_pixeles_recoloreados = [[obtener_color_mas_cercano(pixel, colores_representativos) for pixel in fila] for fila in lista_pixeles]
    pixeles_recoloreados_formateados = np.array(lista_pixeles_recoloreados, dtype=np.uint8)
    imagen_recoloreada = Image.fromarray(pixeles_recoloreados_formateados)
    imagen_recoloreada.save(ruta_imagen_recoloreada)

def pixelar_imagen(ruta_imagen_original, ruta_imagen_pixelada):
    imagen_original = abrir_imagen(ruta_imagen_original)
    imagen_pequegna = imagen_original.resize((imagen_original.width // 20, imagen_original.height // 20), resample=Image.NEAREST)
    imagen_pixelada = imagen_pequegna.resize((imagen_original.width, imagen_original.height), resample=Image.NEAREST)
    imagen_pixelada.save(ruta_imagen_pixelada)

def obtener_colores(lista_pixeles):
    lista_colores = []
    for fila in lista_pixeles:
        for pixel in fila:
            if not pixel in lista_colores:
                lista_colores.append(pixel)
    return lista_colores

def obtener_numeros_colores(ruta_imagen):
    imagen = abrir_imagen(ruta_imagen)
    pixeles = np.array(imagen)
    lista_colores = obtener_colores(pixeles.tolist())
    diccionario_colores = {}
    for i in range(len(lista_colores)):
        diccionario_colores[str(i + 1)] = tuple(lista_colores[i])
    return diccionario_colores

def determinar_color_bloque(imagen, x, y, ancho, alto, colores):
    suma_rojo, suma_verde, suma_azul = 0, 0, 0
    cantidad_pixeles = 0
    for j in range(y, min(y + 19, alto)):
        for i in range(x, min(x + 19, ancho)):
            color = imagen.getpixel((i, j))
            suma_rojo += color[0]
            suma_verde += color[1]
            suma_azul += color[2]
            cantidad_pixeles += 1
    color_promedio = (suma_rojo // cantidad_pixeles, suma_verde // cantidad_pixeles, suma_azul // cantidad_pixeles)
    return obtener_color_mas_cercano(color_promedio, colores)

def enumerar_colores(ruta_imagen_original, ruta_imagen_enumerada, diccionario_colores):
    imagen_original = abrir_imagen(ruta_imagen_original)
    ancho, alto = imagen_original.size
    nuevo_ancho = ancho + ((20 - (ancho % 20)) % 20)
    nuevo_alto = round(nuevo_ancho / (ancho / alto)) + ((20 - (round(nuevo_ancho / (ancho / alto)) % 20)) % 20)
    imagen_aumentada = imagen_original.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
    imagen_enumerada = Image.new("RGB", (nuevo_ancho, nuevo_alto), color=(255, 255, 255))
    draw = ImageDraw.Draw(imagen_enumerada)
    try:
        fuente = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    except IOError:
        fuente = ImageFont.load_default()
    for y in range(0, nuevo_alto, 20):
        for x in range(0, nuevo_ancho, 20):
            color_bloque = determinar_color_bloque(imagen_aumentada, x, y, nuevo_ancho, nuevo_alto, list(diccionario_colores.values()))
            numero_correspondiente = next((k for k, v in diccionario_colores.items() if v == color_bloque), None)
            bbox = draw.textbbox((0, 0), numero_correspondiente, font=fuente)
            ancho_texto = bbox[2] - bbox[0]
            alto_texto = bbox[3] - bbox[1]
            posicion_texto = (x + (20 - ancho_texto) // 2, y + (20 - alto_texto) // 2 - 2)
            draw.text(posicion_texto, numero_correspondiente, font=fuente, fill=(0, 0, 0))
            draw.rectangle([x, y, x + 19, y + 19], outline=(0, 0, 0), width=1)
    imagen_enumerada.save(ruta_imagen_enumerada)

def generar_paleta(ruta_imagen, diccionario_colores):
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
    ruta_paleta_colores = f"{os.path.dirname(ruta_imagen)}/paleta_{os.path.splitext(os.path.basename(ruta_imagen))[0]}.png"
    imagen.save(ruta_paleta_colores)

def main():
    # try:
    sistema = os.name
    if sistema == "nt":
        os.system("cls")
    else:
        os.system("clear")
    ruta_imagen_original = input("Ingrese la ruta absoluta de la imagen: ")
    colores_representativos = obtener_colores_representativos(ruta_imagen_original)
    directorio_imagen = os.path.dirname(ruta_imagen_original)
    nombre_imagen_recoloreada = input("\nIngrese el nombre para la imagen recoloreada: ")
    ruta_imagen_recoloreada = f"{directorio_imagen}/{nombre_imagen_recoloreada}.png"
    recolorear_imagen(ruta_imagen_original, ruta_imagen_recoloreada, colores_representativos)
    nombre_imagen_pixelada = input("\nIngrese el nombre para la imagen pixelada: ")
    ruta_imagen_pixelada = f"{directorio_imagen}/{nombre_imagen_pixelada}.png"
    pixelar_imagen(ruta_imagen_recoloreada, ruta_imagen_pixelada)
    diccionario_colores = obtener_numeros_colores(ruta_imagen_pixelada)
    nombre_imagen_enumerada = input("\nIngrese el nombre para la imagen enumerada: ")
    ruta_imagen_enumerada = f"{directorio_imagen}/{nombre_imagen_enumerada}.png"
    enumerar_colores(ruta_imagen_pixelada, ruta_imagen_enumerada, diccionario_colores)
    generar_paleta(ruta_imagen_enumerada, diccionario_colores)
    redimensionar_imagen(ruta_imagen_original, ruta_imagen_recoloreada)
    redimensionar_imagen(ruta_imagen_original, ruta_imagen_pixelada)
    redimensionar_imagen(ruta_imagen_original, ruta_imagen_enumerada)
    print()
    # except FileNotFoundError:
    #     print("Error: La imagen no fue encontrada. Verifica la ruta e inténtalo nuevamente.")
    # except Exception as e:
    #     print(f"Error inesperado: {e}")

if __name__ == "__main__":
    main()