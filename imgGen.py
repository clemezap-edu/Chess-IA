#!/usr/bin/env python3
"""
Script para descargar imágenes de piezas de ajedrez desde Wikimedia Commons
y convertirlas al formato adecuado para el juego.
"""

import os
import urllib.request
import sys

# Intentar importar cairosvg para conversión SVG a PNG
try:
    import cairosvg

    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

# Intentar importar PIL como alternativa
try:
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def download_chess_pieces():
    # Crear directorio si no existe
    if not os.path.exists("pieces"):
        os.makedirs("pieces")

    # URLs de imágenes de piezas de ajedrez (conjunto Cburnett de Wikimedia Commons)
    pieces = {
        "white_pawn": "https://upload.wikimedia.org/wikipedia/commons/4/45/Chess_plt45.svg",
        "white_rook": "https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg",
        "white_knight": "https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg",
        "white_bishop": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg",
        "white_queen": "https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg",
        "white_king": "https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg",
        "black_pawn": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg",
        "black_rook": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg",
        "black_knight": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg",
        "black_bishop": "https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg",
        "black_queen": "https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg",
        "black_king": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg"
    }

    # Verificar métodos disponibles para conversión
    if not HAS_CAIROSVG and not HAS_PIL:
        print("Advertencia: No se encontraron bibliotecas para convertir SVG a PNG.")
        print("Las imágenes se guardarán como SVG, pero el juego está configurado para PNG.")
        print("Instala 'cairosvg' o 'PIL' para conversión automática:")
        print("  pip install cairosvg")
        print("  pip install pillow")

        choice = input("¿Continuar de todos modos? (s/n): ")
        if choice.lower() != 's':
            print("Descarga cancelada.")
            return

    # Descargar y convertir las imágenes
    for piece_name, url in pieces.items():
        try:
            print(f"Descargando {piece_name}...")

            # Nombre del archivo SVG temporal
            temp_svg = f"pieces/{piece_name}_temp.svg"

            # Descargar SVG
            urllib.request.urlretrieve(url, temp_svg)

            # Convertir a PNG si es posible
            if HAS_CAIROSVG:
                output_file = f"pieces/{piece_name}.png"
                cairosvg.svg2png(url=temp_svg, write_to=output_file, output_width=200, output_height=200)
                os.remove(temp_svg)  # Eliminar SVG temporal
                print(f"  Convertido y guardado como {output_file}")
            elif HAS_PIL:
                # PIL no puede convertir SVG directamente, así que mantenemos el SVG
                output_file = f"pieces/{piece_name}.svg"
                os.rename(temp_svg, output_file)
                print(f"  Guardado como {output_file} (se necesita modificar el código para usar SVG)")
            else:
                # Sin conversión, solo renombrar
                output_file = f"pieces/{piece_name}.svg"
                os.rename(temp_svg, output_file)
                print(f"  Guardado como {output_file} (se necesita modificar el código para usar SVG)")

        except Exception as e:
            print(f"  Error al procesar {piece_name}: {e}")

    print("\nProceso completado.")

    # Instrucciones adicionales según el resultado
    if not HAS_CAIROSVG and not HAS_PIL:
        print("\nLas imágenes se descargaron como SVG. Necesitarás:")
        print("1. Convertirlas manualmente a PNG usando otra herramienta, o")
        print("2. Modificar el código para cargar archivos SVG en lugar de PNG")
        print("\nPara convertir manualmente, puedes usar herramientas como:")
        print("- Inkscape (GUI): https://inkscape.org/")
        print("- GIMP (GUI): https://www.gimp.org/")
        print("- ImageMagick (línea de comandos): https://imagemagick.org/")
        print("- Servicios web como: https://svgtopng.com/")


if __name__ == "__main__":
    print("Iniciando descarga de imágenes de piezas de ajedrez...")
    download_chess_pieces()