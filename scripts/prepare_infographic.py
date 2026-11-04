"""Install the supplied illustration; requires Pillow. Never alters catalog data."""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageOps


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="Original generated infographic")
    args = parser.parse_args()
    site = Path(__file__).resolve().parents[1] / "site"
    page = site / "index.html"
    content = page.read_text(encoding="utf-8")
    pattern = r"<!-- INFOGRAPHIC:START -->.*?<!-- INFOGRAPHIC:END -->"
    if not re.search(pattern, content, flags=re.S):
        raise SystemExit("No se encuentra el espacio de la infografía")
    with Image.open(args.image) as original:
        image = ImageOps.exif_transpose(original).convert("RGBA")
        background = Image.new("RGBA", image.size, "white")
        background.alpha_composite(image)
        image = background.convert("RGB")
    assets = site / "assets"
    assets.mkdir(exist_ok=True)
    widths = sorted({min(w, image.width) for w in (640, 1280, 1920)})
    sizes = "(max-width: 600px) calc(100vw - 70px), (max-width: 1200px) calc(100vw - 118px), 1082px"
    for width in widths:
        resized = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
        resized.save(assets / f"arbol-modelos-{width}.webp", "WEBP", quality=88, method=6)
        resized.save(assets / f"arbol-modelos-{width}.jpg", "JPEG", quality=88, optimize=True, progressive=True)
    width = widths[-1]
    height = round(image.height * width / image.width)
    def srcset(ext):
        return ", ".join(f"assets/arbol-modelos-{w}.{ext} {w}w" for w in widths)
    markup = f'''<!-- INFOGRAPHIC:START -->
<figure>
<a href="assets/arbol-modelos-{width}.jpg" aria-label="Abrir la infografía ilustrativa a tamaño completo">
<picture>
<source type="image/webp" srcset="{srcset('webp')}" sizes="{sizes}">
<img src="assets/arbol-modelos-{width}.jpg" srcset="{srcset('jpg')}" sizes="{sizes}" width="{width}" height="{height}" fetchpriority="high" decoding="async" alt="Árbol ilustrativo de modelos de IA organizado por empresas: OpenAI, Anthropic, Google, xAI, Meta, DeepSeek y Moonshot AI. Los nombres y fechas mostrados no están validados." aria-describedby="infografia-caption">
</picture></a>
<figcaption id="infografia-caption">Maqueta ilustrativa, no información validada. Pulsa la imagen para ampliarla. Para consultar fichas y comparar modelos, utiliza el <a href="#catalogo">catálogo</a>.</figcaption>
</figure>
<!-- INFOGRAPHIC:END -->'''
    page.write_text(re.sub(pattern, lambda _: markup, content, flags=re.S), encoding="utf-8")
    print(f"Infografía incorporada: {width} × {height}; variantes {widths}")
    for asset in sorted(assets.glob("arbol-modelos-*")):
        print(f"{asset.name}: {asset.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
