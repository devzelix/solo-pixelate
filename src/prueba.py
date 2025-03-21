from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None
ruta_imagen = input("\nIngrese la ruta de la imagen: ")
imagen = Image.open(ruta_imagen)
imagen = imagen.convert("RGB")
directorio_imagen = os.path.dirname(ruta_imagen)
ruta_imagen = f"{directorio_imagen}/{os.path.splitext(os.path.basename(ruta_imagen))[0]}.jpg"
imagen.save(ruta_imagen, quality=100)
print()