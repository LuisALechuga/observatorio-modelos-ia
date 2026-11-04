# Observatorio de Modelos de IA (castellano)

Aplicación web estática alimentada por la API pública de Models.dev. Incluye buscador, filtros, comparación de hasta 4 modelos e histórico de sincronizaciones.

## Portada ilustrativa

La portada presenta la infografía «Árbol de modelos de IA 2026» antes del catálogo con aviso visible de que sus modelos y fechas no están validados, incluida la fecha de verificación dibujada en la imagen. Conserva los controles, el comparador y el histórico; el catálogo es la fuente consultable. La imagen es una maqueta, no una captura verificada de Models.dev.

Para sustituir la ilustración, con Python y Pillow instalados:

```bash
python scripts/prepare_infographic.py "/ruta/a/Árbol de modelos de IA 2026.png"
```

El script crea variantes WebP y JPEG de hasta 640, 1280 y 1920 píxeles, sin ampliar el original, y coloca la imagen en la portada. Incluye texto alternativo, dimensiones para reservar espacio, selección responsive, prioridad de carga y enlace a la imagen ampliada. La conversión elimina metadatos del archivo original. Los textos y fechas dibujados en la imagen no se consideran datos del catálogo.

Antes de publicar, comprobar la legibilidad de la imagen en ordenador y móvil. La incorporación no modifica `scripts/sync.py`, los JSON ni el flujo de actualización y despliegue.

Verificación: navegador Edge a 375, 768 y 1440 píxeles sin desbordamiento horizontal de página; búsqueda, filtros combinados, paginación, histórico y comparación (incluido límite de cuatro y conservación al filtrar), sin errores JavaScript. La ilustración se adapta a la pantalla y enlaza a su versión de 1536 × 1024 píxeles para ampliar los textos en móvil. El original pesa 1,99 MB; la variante WebP mayor pesa 287 kB y la de 640 píxeles, 83 kB.

## Despliegue sin instalar nada en tu PC

1. Crea un repositorio **público** nuevo en GitHub llamado `observatorio-modelos-ia` y selecciona la rama `main`.
2. Sube el contenido de esta carpeta **manteniendo la estructura**, incluida la carpeta oculta `.github/workflows` (no subas el ZIP sin descomprimir).
3. En GitHub abre **Settings → Actions → General → Workflow permissions** y selecciona **Read and write permissions**; guarda los cambios. Esto permite al proceso guardar el histórico en el repositorio.
4. En **Settings → Pages → Build and deployment → Source**, elige **GitHub Actions**.
5. Abre **Actions → Actualizar y publicar observatorio → Run workflow** para lanzar la primera sincronización.
6. Cuando termine correctamente, abre `https://TU_USUARIO.github.io/observatorio-modelos-ia/` (sustituye TU_USUARIO).

## Funcionamiento

- Programación automática cada 6 horas en UTC, con posibles retrasos de GitHub Actions.
- `scripts/sync.py` obtiene `https://models.dev/api.json?type=all`, valida datos y produce `site/data/models.json` y `site/data/history.json`.
- Si falla la API o la validación, el trabajo falla y la última web publicada permanece disponible.
- Se guardan los últimos 180 eventos de sincronización en el repositorio. No es un histórico indefinido.
- No se requiere token de los proveedores de IA ni servidor propio.

## Comprobación local opcional

Necesitas Python 3.12 o posterior:

```bash
python scripts/sync.py
cd site
python -m http.server 8000
```

Abre `http://localhost:8000`.

## Precauciones

- El catálogo no confirma la operatividad real de cada modelo; los estados y precios son los de la fuente.
- El histórico registra diferencias entre capturas, no necesariamente lanzamientos o retiradas reales.
- No se deben publicar secretos en el repositorio ni incorporar datos personales.
- GitHub puede retrasar o desactivar tareas programadas en determinadas circunstancias. Revisa Actions periódicamente.
- Las acciones de terceros están referenciadas por versiones mayores para facilitar el ejemplo; para un entorno crítico, fija cada acción a un SHA verificado y utiliza protección de ramas.
- Si se activan reglas de protección de `main`, el commit automático puede requerir un flujo con PR o almacenamiento externo.

Fuente original: https://github.com/anomalyco/models.dev
