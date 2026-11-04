"""Generate a provisional model tree from the catalog, without a validation gate."""
import datetime as dt
import html
import json
from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]
COMPANIES = [
    ("openai", "OpenAI"), ("anthropic", "Anthropic"),
    ("google", "Google"), ("xai", "xAI"), ("meta", "Meta"),
    ("deepseek", "DeepSeek"), ("moonshotai", "Moonshot AI"),
]


def release_date(model):
    try:
        return dt.date.fromisoformat(model.get("release_date") or "")
    except (ValueError, TypeError):
        return dt.date.min


def latest_models(models, provider_id):
    # Use the company's own provider entry, not third-party resellers.
    candidates = [m for m in models if m.get("provider_id") == provider_id]
    candidates.sort(key=lambda m: (-release_date(m).toordinal(), str(m.get("id", ""))))
    seen, chosen = set(), []
    for model in candidates:
        # Collapse an explicitly named "latest" alias of the same dated model.
        name = re.sub(r"\s*\(latest\)\s*$", "", str(model.get("name") or model.get("id")), flags=re.I)
        identity = (name.casefold(), release_date(model))
        if identity not in seen:
            seen.add(identity)
            chosen.append(model)
        if len(chosen) == 3:
            break
    return chosen


def declared_date(model):
    date = release_date(model)
    return date.strftime("%d/%m/%Y") if date != dt.date.min else "Sin fecha declarada"


def text(x, y, value, size=22, color="#17243a", weight="400"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}">{html.escape(str(value))}</text>'


def build_svg(groups, generated_at):
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1480" viewBox="0 0 1600 1480" role="img" aria-labelledby="title desc">',
           '<title id="title">Árbol de modelos de IA: últimos tres registrados por empresa</title>',
           '<desc id="desc">Selección provisional de Models.dev. Orden por fecha de lanzamiento declarada; los modelos sin fecha van al final. No hay validación independiente.</desc>',
           '<rect width="1600" height="1480" fill="#f5f7fb"/>',
           '<g font-family="Arial, sans-serif">',
           '<rect x="24" y="20" width="1552" height="100" rx="22" fill="#10233f"/>',
           text(50, 65, "ÁRBOL DE MODELOS DE IA", 34, "white", "700"),
           text(50, 100, "Los tres más recientes registrados por empresa · Models.dev", 23, "#d5e3f6"),
           text(32, 158, f"Generado el {generated_at} · Selección provisional, sin validación independiente", 22),
           '<path d="M800 1340 V220" stroke="#1673bf" stroke-width="20" fill="none"/>']
    for i, (provider, company, models) in enumerate(groups):
        left = i % 2 == 0
        row = i // 2
        x, y = (32 if left else 890), 190 + row * 295
        edge = x + 678 if left else x
        svg += [f'<path d="M800 {y + 120} Q800 {y + 55} {edge} {y + 55}" stroke="#1673bf" stroke-width="8" fill="none"/>',
                f'<rect x="{x}" y="{y}" width="678" height="275" rx="18" fill="white" stroke="#c5d5e9" stroke-width="2"/>',
                text(x + 20, y + 37, company, 29, weight="700")]
        for j, model in enumerate(models):
            top = y + 54 + j * 70
            svg += [f'<rect x="{x + 12}" y="{top}" width="654" height="64" rx="8" fill="#eaf3fc"/>',
                    text(x + 24, top + 29, str(j + 1), 23, "#2563eb", "700")]
            lines = textwrap.wrap(str(model.get("name") or model["id"]), width=34)[:2]
            for k, line in enumerate(lines):
                svg.append(text(x + 56, top + 24 + k * 25, line, 22, weight="700"))
            svg += [text(x + 492, top + 25, declared_date(model), 16),
                    text(x + 492, top + 48, "No validado", 16, "#785014")]
        if len(models) < 3:
            svg.append(text(x + 20, y + 263, f"{len(models)} modelos disponibles; no se inventan registros.", 17, "#52647c"))
    svg += [text(800, 1300, "IA", 36, "#1673bf", "700"),
            '<rect x="32" y="1400" width="1536" height="60" rx="12" fill="#fff5df"/>',
            text(50, 1437, "Fechas declaradas por la fuente. No acreditan lanzamiento ni disponibilidad. Consulta el catálogo.", 22, "#603b0a"),
            '</g></svg>']
    return "\n".join(svg)


def main():
    site = ROOT / "site"
    data = json.loads((site / "data/models.json").read_text(encoding="utf-8"))
    groups = [(pid, name, latest_models(data["models"], pid)) for pid, name in COMPANIES]
    generated_at = dt.datetime.now(dt.timezone.utc).strftime("%d/%m/%Y %H:%M UTC")
    assets = site / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "arbol-modelos.svg").write_text(build_svg(groups, generated_at), encoding="utf-8")
    listing = []
    for _, company, models in groups:
        items = "".join(f'<li>{html.escape(str(m.get("name") or m["id"]))} · {declared_date(m)} · No validado</li>' for m in models)
        listing.append(f'<h4>{company}</h4><ol>{items}</ol>' if models else f'<h4>{company}</h4><p>Sin registros disponibles.</p>')
    markup = f'''<!-- INFOGRAPHIC:START -->
<figure>
<a href="assets/arbol-modelos.svg" aria-label="Abrir el árbol de modelos a tamaño completo">
<img src="assets/arbol-modelos.svg" width="1600" height="1480" fetchpriority="high" decoding="async" alt="Árbol de los últimos tres modelos registrados por empresa en Models.dev, ordenados por fecha declarada. Selección provisional sin validación independiente." aria-describedby="infografia-caption">
</a>
<figcaption id="infografia-caption">Generado el {generated_at}. Selección provisional: se incluyen modelos aunque no estén validados. Las fechas son las declaradas por la fuente, no fechas verificadas. Pulsa la imagen para ampliarla o consulta el <a href="#catalogo">catálogo</a>.</figcaption>
</figure>
<details class="infographic-models"><summary>Consultar los modelos representados en formato de texto</summary>{"".join(listing)}</details>
<!-- INFOGRAPHIC:END -->'''
    page = site / "index.html"
    content = page.read_text(encoding="utf-8")
    pattern = r"<!-- INFOGRAPHIC:START -->.*?<!-- INFOGRAPHIC:END -->"
    if not re.search(pattern, content, flags=re.S):
        raise ValueError("No se encuentra el espacio de la infografía")
    page.write_text(re.sub(pattern, lambda _: markup, content, flags=re.S), encoding="utf-8")
    print(f"Árbol generado: {sum(len(g[2]) for g in groups)} modelos, {len(groups)} empresas")


if __name__ == "__main__":
    main()
