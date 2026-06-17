#  OptiPlan — Planificación de Producción Multiperiodo

OptiPlan es una aplicación web de escritorio (autocontenida) para resolver problemas de **planificación agregada de producción multiperiodo** mediante **programación lineal**. Permite definir productos, demanda por periodo, capacidades de planta y políticas de inventario, y obtiene el plan de producción óptimo que minimiza costos (o maximiza utilidad), incluyendo análisis de escenarios y exportación de resultados a PDF.

---

##  Tabla de contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Estructura del proyecto](#-estructura-del-proyecto)
- [Requisitos previos](#-requisitos-previos)
- [Instalación y ejecución](#-instalación-y-ejecución)
- [Modelo de optimización](#-modelo-de-optimización)
- [API del backend](#-api-del-backend)
- [Análisis de escenarios](#-análisis-de-escenarios)
- [Asistente IA integrado](#-asistente-ia-integrado)
- [Exportación a PDF](#-exportación-a-pdf)
- [Persistencia de sesiones](#-persistencia-de-sesiones)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

##  Características

- **Resolución de planes de producción óptimos** mediante el solver `CBC` (a través de PuLP), considerando horas regulares, horas extra (con dos tarifas escalonadas), subcontratación, inventario y faltantes.
- **Validación de datos de entrada** antes de resolver, con mensajes de error descriptivos.
- **Análisis de sensibilidad / escenarios**: compara automáticamente 5 escenarios (base, demanda +20 %, demanda −20 %, sin horas extra, capacidad +10 %).
- **Visualización de resultados** con gráficos interactivos (Chart.js): producción, demanda, inventario, costos, utilidad y comparación de escenarios.
- **Exportación a PDF** del plan óptimo y su resumen de costos/utilidad.
- **Asistente conversacional integrado** (basado en reglas, sin llamadas externas) que responde preguntas sobre los resultados obtenidos.
- **Historial de sesiones** guardado localmente en el navegador (`localStorage`), sin necesidad de base de datos.
- **Autoinstalación de dependencias**: la primera ejecución instala automáticamente las librerías de Python necesarias.
- **Cero configuración**: un solo doble clic (`INICIAR.bat` / `INICIAR.sh`) levanta el servidor y abre el navegador.

---

##  Tecnologías

| Capa | Tecnología |
|---|---|
| Backend | Python 3.9+, Flask |
| Optimización | PuLP (solver CBC) |
| Exportación | ReportLab (PDF) |
| Frontend | HTML5, CSS3, JavaScript (vanilla) |
| Gráficos | Chart.js 4 (vía CDN) |
| Persistencia ligera | `localStorage` del navegador |

---

##  Estructura del proyecto

```
OptiPlan/
├── INICIAR.bat              # Lanzador con doble clic (Windows)
├── INICIAR.sh                # Lanzador con doble clic (Mac/Linux)
├── run.py                    # Punto de entrada que invoca app.py
├── app.py                    # Servidor Flask + autoinstalador de dependencias
├── config.py                  # Configuración (host, puerto, claves)
├── requirements.txt           # Dependencias de Python
│
├── backend/
│   ├── __init__.py            # Fábrica de la app Flask (create_app)
│   ├── solver.py               # Modelo de programación lineal (PuLP)
│   ├── validator.py             # Validación de los datos de entrada
│   ├── pdf_export.py            # Generación del reporte PDF
│   └── routes/
│       ├── __init__.py          # Registro de blueprints
│       ├── solver_routes.py      # Endpoints /api/resolver y /api/escenarios
│       └── export_routes.py      # Endpoint /api/exportar-pdf
│
└── frontend/
    ├── index.html              # Interfaz completa (SPA de una sola página)
    └── *.png / *.jpg            # Iconos y fondos de la interfaz
```

---

##  Requisitos previos

- **Python 3.9 o superior** instalado y disponible en el `PATH`.
  Descárgalo en [python.org/downloads](https://www.python.org/downloads/) (en Windows, marca la opción *"Add Python to PATH"* durante la instalación).
- Conexión a internet **solo la primera vez**, para instalar las dependencias.

---

##  Instalación y ejecución

### Windows

1. Descarga o clona el repositorio.
2. Haz doble clic en **`INICIAR.bat`**.
3. La primera vez instalará automáticamente `flask`, `pulp` y `reportlab`.
4. El navegador se abrirá solo en `http://localhost:5000`.

### Mac / Linux

```bash
git clone https://github.com/JhonFMin/OptiPlan.git
cd OptiPlan
python3 run.py
```

También puedes ejecutar `INICIAR.sh` con doble clic (si tu sistema lo permite) o:

```bash
chmod +x INICIAR.sh
./INICIAR.sh
```

### Instalación manual de dependencias (opcional)

```bash
pip install -r requirements.txt
```

> A partir de la segunda ejecución, la app arranca directamente sin reinstalar nada.

---

##  Modelo de optimización

El núcleo de OptiPlan (`backend/solver.py`) formula y resuelve un modelo de **programación lineal** por periodo y producto, con el objetivo de **minimizar el costo total** (producción + subcontratación + inventario + faltantes + horas extra).

**Variables de decisión** (por periodo *t* y producto *n*):

- `x[t,n]` — unidades producidas en planta.
- `s[t,n]` — unidades subcontratadas.
- `I[t,n]` — inventario final (acotado por la capacidad máxima de almacenamiento).
- `f[t,n]` — unidades de demanda no satisfecha (faltante).
- `hec1[t]`, `hec2[t]` — horas extra de corte, en dos tramos con tarifas distintas.
- `hee[t]` — horas extra de ensamble.

**Restricciones principales:**

- Balance de inventario: inventario anterior + producción + subcontratación = demanda + inventario final + faltante.
- Capacidad de corte y ensamble por periodo (regular + horas extra), con reducción configurable de capacidad en el periodo 3.
- Límite de inventario máximo por producto.
- Inventario mínimo final exigido al cierre del horizonte de planeación.

El resultado incluye, por periodo y en total: producción, subcontratación, inventario, faltantes, horas extra utilizadas, desglose de costos, ingresos y utilidad.

---

## API del backend

Todas las rutas están bajo el prefijo `/api`.

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/resolver` | Recibe los datos del problema y devuelve el plan óptimo. |
| `POST` | `/api/escenarios` | Resuelve el mismo problema bajo los 5 escenarios predefinidos y devuelve la comparación. |
| `POST` | `/api/exportar-pdf` | Recibe `{ datos, resultado }` de un plan óptimo y devuelve un PDF descargable. |

Si los datos enviados no son válidos, la API responde `422` con el detalle de los errores de validación; si ocurre un error interno al resolver, responde `500`.

---

##  Análisis de escenarios

Desde la pestaña de **Escenarios**, OptiPlan resuelve automáticamente el mismo problema bajo 5 variantes para evaluar la robustez del plan:

1. **Base** — datos originales sin cambios.
2. **Demanda +20 %** — incremento del 20 % en toda la demanda.
3. **Demanda −20 %** — reducción del 20 % en toda la demanda.
4. **Sin horas extra** — sin disponibilidad de horas extra de corte ni ensamble.
5. **Capacidad +10 %** — incremento del 10 % en las capacidades regulares.

Los resultados se muestran de forma comparativa en gráficos dedicados.

---

##  Asistente IA integrado

La interfaz incluye un chat flotante ("Asistente OptiPlan") que responde preguntas sobre los resultados obtenidos (costos, utilidad, horas extra, faltantes, etc.). Es un asistente **basado en reglas que corre enteramente en el navegador**, sin llamadas a APIs externas ni envío de datos a terceros.

---

##  Exportación a PDF

Una vez obtenido un plan óptimo, el botón de exportación genera un reporte en PDF (`backend/pdf_export.py`, con ReportLab) que incluye el plan de producción por periodo y el resumen de costos y utilidad.

---

##  Persistencia de sesiones

OptiPlan no usa base de datos: el historial de configuraciones y resultados se guarda en el `localStorage` del navegador, lo que permite recuperar sesiones anteriores sin necesidad de un servidor con estado.

---

##  Contribuir

Las contribuciones son bienvenidas. Para proponer cambios:

1. Haz un fork del repositorio.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. Haz commit de tus cambios (`git commit -m "Agrega nueva funcionalidad"`).
4. Haz push a tu rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request describiendo el cambio.

---

##  Licencia

Este proyecto no especifica actualmente un archivo de licencia. Se recomienda añadir uno (por ejemplo, MIT) si planeas distribuirlo o aceptar contribuciones externas.
