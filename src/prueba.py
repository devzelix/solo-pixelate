from PIL import Image
import numpy as np

colores_rgb = [
    [(255, 0, 0), (0, 255, 0), (255, 0, 0)],
    [(0, 0, 255), (255, 255, 0), (0, 0, 255)]
]
pixeles = np.array(colores_rgb, dtype=np.uint8)
imagen = Image.fromarray(pixeles)
imagen.save("imagen_generada.png")
imagen.show()