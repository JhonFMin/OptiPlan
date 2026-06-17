import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime

COLOR_VERDE   = colors.HexColor("#0b2b26")
COLOR_ACENTO  = colors.HexColor("#34d399")
COLOR_CLARO   = colors.HexColor("#f0fdf4")
COLOR_GRIS    = colors.HexColor("#6b7280")
COLOR_BLANCO  = colors.white
COLOR_FILA_ALT = colors.HexColor("#ecfdf5")


def _estilo_tabla_base(col_widths=None):
    return TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), COLOR_VERDE),
        ("TEXTCOLOR",    (0, 0), (-1, 0), COLOR_BLANCO),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 9),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [COLOR_BLANCO, COLOR_FILA_ALT]),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",     (0, 1), (-1, -1), 8),
        ("GRID",         (0, 0), (-1, -1), 0.4, COLOR_GRIS),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ])


def generar_pdf(resultado, datos):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm,  bottomMargin=2*cm,
    )

    estilos = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "titulo", parent=estilos["Title"],
        fontSize=20, textColor=COLOR_VERDE,
        spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold"
    )
    subtitulo_style = ParagraphStyle(
        "subtitulo", parent=estilos["Normal"],
        fontSize=11, textColor=COLOR_GRIS,
        spaceAfter=2, alignment=TA_CENTER
    )
    seccion_style = ParagraphStyle(
        "seccion", parent=estilos["Heading2"],
        fontSize=12, textColor=COLOR_VERDE,
        spaceBefore=14, spaceAfter=6, fontName="Helvetica-Bold",
        borderPad=4,
    )
    normal_style = ParagraphStyle(
        "normal_custom", parent=estilos["Normal"],
        fontSize=9, textColor=colors.black, leading=13
    )
    kpi_style = ParagraphStyle(
        "kpi", parent=estilos["Normal"],
        fontSize=9, textColor=COLOR_GRIS, alignment=TA_CENTER
    )

    story = []
    nombres = [p["nombre"] for p in datos["productos"]]
    periodos_res = resultado["periodos"]
    resumen = resultado["resumenCostos"]
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    story.append(Paragraph("OptiPlan", titulo_style))
    story.append(Paragraph("Planificación de Producción Multiperiodo — Reporte de Resultados", subtitulo_style))
    story.append(Paragraph(f"Generado: {fecha}", ParagraphStyle("fecha", parent=estilos["Normal"],
        fontSize=8, textColor=COLOR_GRIS, alignment=TA_CENTER, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=2, color=COLOR_ACENTO, spaceAfter=12))

    story.append(Paragraph("Resumen Ejecutivo", seccion_style))

    kpi_data = [
        ["Ingreso Total", "Costo Total", "Utilidad Total", "Periodos"],
        [
            f"${resumen['ingresoTotal']:,.0f}",
            f"${resumen['costoTotal']:,.0f}",
            f"${resumen['utilidadTotal']:,.0f}",
            str(datos["periodos"]),
        ]
    ]
    kpi_table = Table(kpi_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), COLOR_VERDE),
        ("TEXTCOLOR",     (0, 0), (-1, 0), COLOR_BLANCO),
        ("BACKGROUND",    (0, 1), (-1, 1), COLOR_CLARO),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",      (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 10),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("GRID",          (0, 0), (-1, -1), 0.5, COLOR_ACENTO),
        ("TEXTCOLOR",     (0, 1), (1, 1), COLOR_VERDE),
        ("TEXTCOLOR",     (2, 1), (2, 1),
            colors.HexColor("#16a34a") if resumen["utilidadTotal"] >= 0 else colors.red),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Desglose de Costos", seccion_style))
    costos_data = [
        ["Concepto", "Monto ($)", "% del Total"],
        ["Producción",    f"${resumen['costoProduccion']:,.2f}",
            f"{resumen['costoProduccion']/resumen['costoTotal']*100:.1f}%" if resumen['costoTotal'] else "—"],
        ["Subcontrato",   f"${resumen['costoSubcontrato']:,.2f}",
            f"{resumen['costoSubcontrato']/resumen['costoTotal']*100:.1f}%" if resumen['costoTotal'] else "—"],
        ["Inventario",    f"${resumen['costoInventario']:,.2f}",
            f"{resumen['costoInventario']/resumen['costoTotal']*100:.1f}%" if resumen['costoTotal'] else "—"],
        ["Faltantes",     f"${resumen['costoFaltante']:,.2f}",
            f"{resumen['costoFaltante']/resumen['costoTotal']*100:.1f}%" if resumen['costoTotal'] else "—"],
        ["Horas Extra",   f"${resumen['costoHorasExtra']:,.2f}",
            f"{resumen['costoHorasExtra']/resumen['costoTotal']*100:.1f}%" if resumen['costoTotal'] else "—"],
        ["TOTAL",         f"${resumen['costoTotal']:,.2f}", "100%"],
    ]
    costos_table = Table(costos_data, colWidths=[6*cm, 5*cm, 5*cm])
    costos_table.setStyle(_estilo_tabla_base())
    costos_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0), COLOR_VERDE),
        ("TEXTCOLOR",   (0, 0), (-1, 0), COLOR_BLANCO),
        ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND",  (0, -1), (-1, -1), COLOR_CLARO),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [COLOR_BLANCO, COLOR_FILA_ALT]),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ALIGN",       (0, 0), (-1, -1), "CENTER"),
        ("ALIGN",       (0, 1), (0, -1), "LEFT"),
        ("GRID",        (0, 0), (-1, -1), 0.4, COLOR_GRIS),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(costos_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("Resultados por Periodo", seccion_style))
    for per in periodos_res:
        t = per["periodo"]
        story.append(Paragraph(f"Periodo {t} — Mes {t}", ParagraphStyle(
            "mes", parent=estilos["Normal"],
            fontSize=10, textColor=COLOR_VERDE, fontName="Helvetica-Bold",
            spaceBefore=6, spaceAfter=4
        )))

        headers = ["Producto", "Producción", "Subcontrato", "Inventario", "Faltante"]
        rows = [headers]
        for n in nombres:
            rows.append([
                n,
                f"{per['produccion'].get(n, 0):.0f}",
                f"{per['subcontrato'].get(n, 0):.0f}",
                f"{per['inventario'].get(n, 0):.0f}",
                f"{per['faltante'].get(n, 0):.0f}",
            ])
        rows.append([
            "Costos/Ingresos",
            f"Prod: ${per['costoProduccion']:,.0f}",
            f"Sub: ${per['costoSubcontrato']:,.0f}",
            f"Inv: ${per['costoInventario']:,.0f}",
            f"HE: ${per['costoHorasExtra']:,.0f}",
        ])
        t_table = Table(rows, colWidths=[3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm])
        t_table.setStyle(_estilo_tabla_base())
        story.append(t_table)
        story.append(Paragraph(
            f"Ingresos: <b>${per['ingresosPeriodo']:,.2f}</b>  |  "
            f"Costos: <b>${per['costosPeriodo']:,.2f}</b>  |  "
            f"Utilidad: <b>${per['utilidadPeriodo']:,.2f}</b>  |  "
            f"H.E. Corte: <b>{per['horasExtraCorte']:.1f} h</b>  |  "
            f"H.E. Ensamble: <b>{per['horasExtraEnsamble']:.1f} h</b>",
            ParagraphStyle("resumen_per", parent=estilos["Normal"],
                           fontSize=8, textColor=COLOR_GRIS, spaceAfter=6)
        ))

    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_GRIS, spaceBefore=8, spaceAfter=6))
    story.append(Paragraph(
        "Generado por OptiPlan · Proyecto de Programación Lineal — Investigación de Operaciones · Universidad · Junio 2026",
        ParagraphStyle("pie", parent=estilos["Normal"],
                       fontSize=7, textColor=COLOR_GRIS, alignment=TA_CENTER)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
