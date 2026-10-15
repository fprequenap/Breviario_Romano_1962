# Breviarium Romanum MCMLXII — PWA

Breviario Romano, edición típica de 1962 (rúbricas del Código de 1960). Horas diurnas: Laudes, Prima, Tercia, Sexta, Nona, Vísperas y Completas. Sin Maitines.

## Contenido
- Oficio completo y calculado para cada día del **1-oct-2026 al 31-dic-2028** (823 días × 7 horas): temporal, santoral, conmemoraciones, primeras Vísperas, Triduo Sacro, Martirologio en Prima.
- Latín, bilingüe (latín/español) o español. En móvil, el bilingüe intercala verso a verso; en pantalla ancha, dos columnas.
- Temas: Pergamino, Azul claro, Noche. Tamaño de letra, números de versículo, pantalla encendida durante el rezo.
- Funciona sin conexión tras la primera carga (service worker con auto-actualización).

## Horario por defecto (editable en «Avisos»)
| Hora | Aviso |
|---|---|
| Laudes | 05:30 |
| Prima | 07:00 |
| Tercia | 09:00 |
| Sexta | 12:00 |
| Nona | 15:00 |
| Vísperas | 19:00 |
| Completas | 21:30 |

## Avisos: dos mecanismos
1. **Calendario del teléfono (.ics)** — botón «Añadir al calendario». Crea siete eventos diarios recurrentes con alarma. Es el único método que suena con la aplicación cerrada en iOS y Android, porque una PWA no puede programar alarmas locales exactas sin servidor de notificaciones push.
2. **Avisos internos** — notificación del sistema y campana (tres toques) mientras la aplicación está abierta o en segundo plano reciente.

## Publicación en GitHub Pages
1. Subir el contenido de esta carpeta (raíz: `index.html`, `sw.js`, `manifest.json`, iconos, `fonts/`, `data/`) a un repositorio.
2. Settings → Pages → Branch `main` / root.
3. Abrir la URL en el móvil → «Añadir a pantalla de inicio».

## Regenerar años posteriores
`tools/generar.sh 2029-01-01 2029-12-31` (Linux/WSL con perl + python3). Usa el motor de Divinum Officium para calcular el oficio y reempaqueta `data/`.

## Fuentes
Textos y cómputo litúrgico: proyecto Divinum Officium (github.com/DivinumOfficium, licencia MIT).
**Atención:** la traducción española de los salmos en esos archivos coincide con la de la Liturgia de las Horas de la Conferencia Episcopal Española (texto con derechos). Para uso privado no plantea problema; para distribución pública conviene sustituirla por una versión de dominio público (p. ej. Torres Amat) o publicar sólo en latín.
