"""Generate a provisional model tree from the catalog, without a validation gate."""
import datetime as dt
import html
import json
from pathlib import Path
import re

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
    from infographic_art import render_tree
    return render_tree(groups, generated_at, declared_date)


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
<img src="assets/arbol-modelos.svg" width="1800" height="1200" fetchpriority="high" decoding="async" alt="Árbol de los últimos tres modelos registrados por empresa en Models.dev, ordenados por fecha declarada. Selección provisional sin validación independiente." aria-describedby="infografia-caption">
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
