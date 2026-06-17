# OptiPlan — Planificación de Producción Multiperiodo

## ▶ Cómo ejecutar (Windows)

1. Descomprime el zip en cualquier carpeta
2. Haz **doble clic** en `INICIAR.bat`
   - La primera vez instalará las librerías automáticamente
   - El navegador se abrirá solo en http://localhost:5000

> ⚠️ Necesitas tener **Python 3.9 o superior** instalado.
> Descárgalo gratis en: https://www.python.org/downloads/
> *(Durante la instalación marca "Add Python to PATH")*

---

## ▶ Cómo ejecutar (Mac / Linux)

```bash
python3 run.py
```

O con doble clic en `INICIAR.sh` (Linux/Mac).

---

## ¿Qué hace la primera vez?

Al ejecutar por primera vez, el lanzador instala automáticamente:
- `flask` — servidor web
- `pulp` — resolutor de programación lineal
- `reportlab` — exportación de PDF

A partir de la segunda vez arranca directamente sin instalar nada.

---

## Estructura

```
OptiPlan/
├── INICIAR.bat       ← Doble clic en Windows
├── INICIAR.sh        ← Doble clic en Mac/Linux  
├── run.py            ← Lanzador principal
├── app.py            ← Servidor Flask
├── config.py
├── backend/          ← Solver LP, PDF, rutas API
└── frontend/         ← Interfaz gráfica (HTML)
```
