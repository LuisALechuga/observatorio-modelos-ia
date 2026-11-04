"""Vector artwork inspired by the supplied illustrated tree; no external assets."""
import html
import textwrap


def render_tree(groups, generated_at, declared_date):
    def txt(x, y, value, size=22, color="#10233f", weight=400, extra=""):
        return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" {extra}>{html.escape(str(value))}</text>'

    def leaf(x, y, angle=0, color="url(#leaf)", scale=1):
        return f'<g transform="translate({x} {y}) rotate({angle}) scale({scale})"><path d="M0 0 C-28 -8 -34 -37 -26 -60 C0 -52 20 -23 0 0Z" fill="{color}"/><path d="M0 0 L-22 -48" stroke="white" stroke-opacity=".6" stroke-width="1.5"/></g>'

    def capability(model):
        output = (model.get("modalities") or {}).get("output") or []
        if any(m in output for m in ("image", "video", "audio")):
            return "#e85494", "#ffedf5", "Multimodal · " + ", ".join({"image": "imagen", "video": "vídeo", "audio": "audio", "text": "texto"}.get(m, m) for m in output)
        if model.get("reasoning"):
            return "#159bea", "#e9f5ff", "Razonamiento" + (" · herramientas" if model.get("tool_call") else "")
        if any(word in str(model.get("name", "")).lower() for word in ("flash", "mini", "haiku", "lite", "fast", "highspeed")):
            return "#f3ac12", "#fff7df", "Variante ligera / rápida según su denominación"
        return "#57b535", "#edf9e8", "Uso general" + (" · herramientas" if model.get("tool_call") else " · capacidades según catálogo")

    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1200" viewBox="0 0 1800 1200" role="img" aria-labelledby="title desc">',
           '<title id="title">Árbol de modelos de IA: últimos tres registrados por empresa</title>',
           '<desc id="desc">Árbol azul con hojas verdes y siete ramas por empresa. Fechas declaradas por Models.dev. Selección provisional sin validación independiente.</desc>',
           '''<defs>
<linearGradient id="navy" x2="0" y2="1"><stop stop-color="#213f72"/><stop offset="1" stop-color="#092851"/></linearGradient>
<linearGradient id="wood"><stop stop-color="#064eab"/><stop offset=".45" stop-color="#0c9fff"/><stop offset="1" stop-color="#0052b0"/></linearGradient>
<linearGradient id="leaf" x2="1" y2="1"><stop stop-color="#bce92b"/><stop offset=".5" stop-color="#72c913"/><stop offset="1" stop-color="#2e9f17"/></linearGradient>
<linearGradient id="pale" x2="0" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#edf4ff"/></linearGradient>
<filter id="shadow" x="-20%" y="-20%" width="150%" height="160%"><feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#14375b" flood-opacity=".18"/></filter>
<pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse"><path d="M28 0H0V28" fill="none" stroke="#e7edf5" stroke-width=".7"/></pattern>
<symbol id="calendar" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16" rx="2" fill="none" stroke="currentColor" stroke-width="1.7"/><path d="M3 10H21M7 2V7M17 2V7M7 14H9M12 14H14M7 17H9M12 17H14" stroke="currentColor" stroke-width="1.7"/></symbol>
</defs><rect width="1800" height="1200" fill="#fff"/><rect width="1800" height="1200" fill="url(#grid)"/>
<g font-family="Arial, sans-serif">''',
           '<rect x="24" y="18" width="1368" height="64" rx="24" fill="url(#navy)" filter="url(#shadow)"/>',
           txt(51, 62, "ÁRBOL DE MODELOS DE IA · ÚLTIMOS 3 POR EMPRESA", 37, "white", 800),
           '<rect x="1410" y="18" width="366" height="90" rx="24" fill="url(#pale)" stroke="#cad9ef"/>',
           '<use href="#calendar" x="1430" y="37" width="40" height="40"/>',
           txt(1480, 44, "Generado el", 18, weight=700), txt(1480, 74, generated_at, 18, weight=700),
           '<rect x="177" y="94" width="1210" height="35" rx="17" fill="#e7f3ff"/>',
           txt(199, 119, "Fuente: Models.dev · Fechas declaradas · Selección provisional, sin validación independiente", 21, weight=700)]

    # A tapered organic trunk and curved branches, rather than an organizational chart.
    svg += ['<path d="M854 1034 C861 920 877 820 877 707 C878 593 876 509 900 418 C901 528 916 600 916 709 C915 836 934 945 944 1034Z" fill="url(#wood)" filter="url(#shadow)"/>']
    layout = {
        "openai": (20, 155, 620, 270, 730, 449, "GPT", "O"),
        "xai": (20, 448, 620, 270, 730, 652, "Grok", "xAI"),
        "meta": (20, 741, 620, 270, 730, 871, "Muse / Llama", "∞"),
        "anthropic": (1160, 150, 620, 210, 1060, 430, "Claude", "AI"),
        "google": (1160, 378, 620, 210, 1060, 610, "Gemini", "G"),
        "deepseek": (1160, 606, 620, 210, 1060, 784, "DeepSeek", "D"),
        "moonshotai": (1160, 834, 620, 210, 1060, 958, "Kimi", "K"),
    }
    active = [g for g in groups if g[0] in layout]
    for pid, company, models in active:
        x, y, w, h, bx, by, family, badge = layout[pid]
        left = x < 900
        edge = x + w if left else x
        branch_y = by + 120 if left else by + 95
        svg += [f'<path d="M900 {branch_y} C{900 if left else 920} {by + 10} {bx + (80 if left else -80)} {by} {bx} {by}" fill="none" stroke="url(#wood)" stroke-width="25" stroke-linecap="round"/>',
                f'<path d="M{bx} {by} C{edge + (40 if left else -40)} {by} {edge + (40 if left else -40)} {y + h / 2} {edge} {y + h / 2}" fill="none" stroke="#0982e7" stroke-width="5"/>',
                f'<circle cx="{edge}" cy="{y + h / 2}" r="5" fill="#0878d8"/>',
                f'<rect x="{bx-42}" y="{by-42}" width="84" height="84" rx="23" fill="white" stroke="#e5edf8" filter="url(#shadow)"/>',
                txt(bx, by + 17, badge, 43 if len(badge) < 3 else 29, "#0878d8" if pid in ("google", "meta", "deepseek") else "#15253b", 800, 'text-anchor="middle"')]

    for x, y, angle, scale in [(891,457,-10,.8),(922,485,80,.7),(871,550,-65,.85),(940,590,90,.8),(872,677,-60,.85),(946,737,85,.8),(865,803,-65,.75),(952,878,80,.8),(881,924,-70,.7),(838,603,-80,.7),(983,690,85,.65),(822,847,-70,.6)]:
        svg.append(leaf(x, y, angle, scale=scale))

    # Central legend follows the hierarchy and color cues of the reference.
    svg += ['<rect x="672" y="154" width="456" height="232" rx="23" fill="white" stroke="#c3d4eb" filter="url(#shadow)"/>',
            txt(696, 185, "LEYENDA · Capacidad orientativa", 22, weight=800)]
    for j, (color, bg, label) in enumerate([("#159bea", "#e9f5ff", "Razonamiento y tareas complejas"),("#57b535", "#edf9e8", "Uso general y herramientas"),("#f3ac12", "#fff7df", "Variantes ligeras / rápidas"),("#e85494", "#ffedf5", "Salida de imagen, vídeo o audio")]):
        yy = 198 + j * 44
        svg += [f'<rect x="684" y="{yy}" width="432" height="40" rx="14" fill="{bg}"/>', leaf(716, yy+32, 40, color, .45), txt(744, yy+27, label, 19, weight=700)]

    for pid, company, models in active:
        x, y, w, h, bx, by, family, badge = layout[pid]
        roomy = h == 270
        row_h = 65 if roomy else 46
        svg += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="27" fill="url(#pale)" stroke="#9fb9dc" stroke-width="1.5" filter="url(#shadow)"/>',
                txt(x+22, y+40, badge, 29, "#077adb", 800), txt(x+88, y+40, company, 33, weight=800),
                f'<rect x="{x+w-156}" y="{y+12}" width="136" height="33" rx="16" fill="#e8f3ff" stroke="#b3cff0"/>',
                txt(x+w-88, y+35, family, 18, weight=700, extra='text-anchor="middle"')]
        for j, model in enumerate(models):
            top = y+57+j*row_h
            color, bg, description = capability(model)
            name = str(model.get("name") or model["id"])
            lines = textwrap.wrap(name, 32)[:2]
            name_size = 21 if len(name) < 29 else 18
            svg += [f'<rect x="{x+10}" y="{top}" width="600" height="{row_h-4}" rx="14" fill="{bg}"/>',
                    f'<rect x="{x+20}" y="{top+9}" width="32" height="32" rx="9" fill="{color}"/>',
                    txt(x+36, top+33, j+1, 23, "white", 800, 'text-anchor="middle"'),
                    leaf(x+79, top+38, 40, color, .46)]
            if len(lines) > 1 and not roomy:
                for k, line in enumerate(lines):
                    svg.append(txt(x+100, top+18+k*18, line, 17, weight=700))
            else:
                svg.append(txt(x+100, top+25, name, name_size, weight=800))
                if roomy:
                    svg.append(txt(x+100, top+47, textwrap.shorten(description, width=43, placeholder="…"), 15))
            svg += [f'<use href="#calendar" x="{x+466}" y="{top+11}" width="19" height="19"/>', txt(x+494, top+27, declared_date(model), 16, weight=700)]
        if len(models) < 3:
            svg.append(txt(x+22, y+h-12, f"{len(models)} modelos disponibles en el catálogo", 16))

    svg += ['<rect x="850" y="1001" width="100" height="83" rx="22" fill="url(#navy)" stroke="#119cff" stroke-width="5" filter="url(#shadow)"/>', txt(900, 1060, "IA", 48, "white", 800, 'text-anchor="middle"'),
            '<rect x="670" y="1094" width="460" height="42" rx="21" fill="url(#navy)"/>', txt(900,1123,"MODELOS DE IA · SELECCIÓN PROVISIONAL",20,"white",800,'text-anchor="middle"'),
            '<rect x="24" y="1148" width="1752" height="40" rx="20" fill="#edf4ff" stroke="#cfdef0"/>',
            txt(48,1175,f"{len(active)} empresas  ·  {sum(len(g[2]) for g in active)} modelos  |  Fechas declaradas; no acreditan lanzamiento ni disponibilidad. Consulta el catálogo.",21,weight=700), '</g></svg>']
    return "\n".join(svg)
