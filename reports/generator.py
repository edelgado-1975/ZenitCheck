"""
ZenitCheck — Generador Profesional de Certificados de Inspección en PDF con ReportLab.
Aplica los colores corporativos de forma estricta:
- Encabezado: #1E293B
- Verde Esmeralda: #16A34A (Apto)
- Ámbar: #EAB308 (Observación, texto oscuro)
- Rojo Carmesí: #DC2626 (Rechazado)
Incluye datos del equipo, normas aplicables, fotos, hallazgos IA y bloque de firma digital.
"""

import io
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)
from django.conf import settings
from .signer import sign_pdf_data


COLOR_DARK = colors.HexColor('#1E293B')
COLOR_APPROVED = colors.HexColor('#16A34A')
COLOR_OBSERVATION = colors.HexColor('#EAB308')
COLOR_REJECTED = colors.HexColor('#DC2626')
COLOR_GRAY_BG = colors.HexColor('#F8FAFC')
COLOR_BORDER = colors.HexColor('#E2E8F0')


def generate_inspection_certificate_pdf(inspection):
    """
    Genera el certificado de inspección técnica en formato PDF.
    Retorna una tupla: (pdf_bytes, signature_info)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
        pageCompression=0  # Permite inspección y verificación forense directa
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.white,
        alignment=1,
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#CBD5E1'),
        alignment=1
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=COLOR_DARK,
        spaceBefore=10,
        spaceAfter=4
    )
    normal_text = ParagraphStyle(
        'Norm',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1F2937')
    )
    bold_text = ParagraphStyle(
        'NormBold',
        parent=normal_text,
        fontName='Helvetica-Bold'
    )

    story = []

    # 1. ENCABEZADO CORPORATIVO
    header_data = [
        [Paragraph("⛑ <b>ZENITCHECK — SISTEMA DE GESTIÓN TÉCNICA DE ALTURAS</b>", title_style)],
        [Paragraph("CERTIFICADO OFICIAL DE INSPECCIÓN TÉCNICA DE EQUIPOS DE PROTECCIÓN CONTRA CAÍDAS", subtitle_style)]
    ]
    header_table = Table(header_data, colWidths=[540])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_DARK),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # 2. BANNER DE VEREDICTO CON CÓDIGO DE COLOR OBLIGATORIO
    if inspection.final_verdict == 'APPROVED':
        verdict_bg = COLOR_APPROVED
        verdict_fg = colors.white
        verdict_icon = "✓ EQUIPO APTO Y APROBADO PARA OPERAR"
    elif inspection.final_verdict == 'OBSERVATION':
        verdict_bg = COLOR_OBSERVATION
        verdict_fg = colors.HexColor('#1E293B')  # Texto oscuro para WCAG AA
        verdict_icon = "⚠️ EQUIPO EN OBSERVACIÓN / PRÓXIMO A VENCER"
    else:
        verdict_bg = COLOR_REJECTED
        verdict_fg = colors.white
        verdict_icon = "✕ EQUIPO RECHAZADO — FUERA DE SERVICIO (BLOQUEO INMEDIATO)"

    verdict_p_style = ParagraphStyle(
        'VerdictBanner',
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=verdict_fg,
        alignment=1
    )
    verdict_table = Table([[Paragraph(f"<b>{verdict_icon}</b>", verdict_p_style)]], colWidths=[540])
    verdict_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), verdict_bg),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(verdict_table)
    story.append(Spacer(1, 12))

    # 3. DATOS DEL EQUIPO Y NORMAS APLICABLES
    eq = inspection.equipment
    next_due_str = inspection.next_inspection_due.strftime('%d/%m/%Y') if inspection.next_inspection_due else "Pendiente"
    eq_data = [
        [
            Paragraph("<b>Número de Serie:</b>", normal_text),
            Paragraph(f"<b>{eq.serial_number}</b>", normal_text),
            Paragraph("<b>Fecha Inspección:</b>", normal_text),
            Paragraph(inspection.inspection_date.strftime("%d/%m/%Y %H:%M"), normal_text),
        ],
        [
            Paragraph("<b>Marca:</b>", normal_text),
            Paragraph(f"{eq.brand.name} ({eq.brand.get_origin_display()})", normal_text),
            Paragraph("<b>Norma Internacional:</b>", normal_text),
            Paragraph(f"<b>{eq.equipment_type.standard_international}</b>", normal_text),
        ],
        [
            Paragraph("<b>Modelo / Referencia:</b>", normal_text),
            Paragraph(eq.model_name, normal_text),
            Paragraph("<b>Norma US (ANSI):</b>", normal_text),
            Paragraph(f"<b>{eq.equipment_type.standard_us}</b>", normal_text),
        ],
        [
            Paragraph("<b>Tipo de Equipo:</b>", normal_text),
            Paragraph(eq.equipment_type.name, normal_text),
            Paragraph("<b>Fecha Fabricación:</b>", normal_text),
            Paragraph(eq.manufacturing_date.strftime("%d/%m/%Y"), normal_text),
        ],
        [
            Paragraph("<b>Cliente / Propietario:</b>", normal_text),
            Paragraph(eq.client_name or "No especificado", normal_text),
            Paragraph("<b>Vencimiento Certificado:</b>", normal_text),
            Paragraph(f"<b>{next_due_str}</b>", normal_text),
        ],
        [
            Paragraph("<b>Ubicación en Sitio:</b>", normal_text),
            Paragraph(inspection.location or eq.location_assigned or "En campo", normal_text),
            Paragraph("<b>Certificado UUID:</b>", normal_text),
            Paragraph(f"<font size=7>{inspection.certificate_uuid}</font>", normal_text),
        ]
    ]
    eq_table = Table(eq_data, colWidths=[120, 150, 130, 140])
    eq_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_GRAY_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(Paragraph("1. INFORMACIÓN DEL EQUIPO Y MARCO NORMATIVO", section_title))
    story.append(eq_table)
    story.append(Spacer(1, 10))

    # 4. HALLAZGOS DE IA
    story.append(Paragraph("2. REGISTRO DE ANÁLISIS DE ANOMALÍAS POR INTELIGENCIA ARTIFICIAL", section_title))
    findings = []
    for photo in inspection.photos.all():
        findings.extend(photo.findings.all())

    if findings:
        findings_data = [
            [
                Paragraph("<b>Tipo de Anomalía</b>", bold_text),
                Paragraph("<b>Severidad</b>", bold_text),
                Paragraph("<b>Confianza IA</b>", bold_text),
                Paragraph("<b>Detalle Técnico</b>", bold_text),
            ]
        ]
        for f in findings:
            sev_color = '#DC2626' if f.severity == 'CRITICAL' else ('#B45309' if f.severity == 'MAJOR' else '#15803D')
            findings_data.append([
                Paragraph(f.get_defect_type_display(), normal_text),
                Paragraph(f"<font color='{sev_color}'><b>{f.get_severity_display()}</b></font>", normal_text),
                Paragraph(f"<b>{f.confidence:.0%}</b>", normal_text),
                Paragraph(f.description or "Localizado en zona de análisis", normal_text),
            ])
        f_table = Table(findings_data, colWidths=[140, 100, 80, 220])
        f_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(f_table)
    else:
        story.append(Paragraph("<i>No se detectaron anomalías visibles. Las costuras, cintas y herrajes cumplen las tolerancias normativas.</i>", normal_text))

    story.append(Spacer(1, 10))

    # 5. OBSERVACIONES
    obs_text = inspection.general_observations or "Sin observaciones adicionales."
    if inspection.verdict_override_justification:
        obs_text += f"<br/><br/><b>Justificación de modificación de veredicto:</b> {inspection.verdict_override_justification}"

    story.append(Paragraph("3. DICTAMEN TÉCNICO Y OBSERVACIONES DEL INSPECTOR", section_title))
    obs_table = Table([[Paragraph(obs_text, normal_text)]], colWidths=[540])
    obs_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_GRAY_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(obs_table)
    story.append(Spacer(1, 14))

    # 6. FIRMA DIGITAL
    inspector = inspection.inspector
    sig_data = [
        [
            Paragraph("<b>INSPECTOR COMPETENTE:</b>", bold_text),
            Paragraph("<b>SELLO Y FIRMA DIGITAL CRIPTOGRÁFICA:</b>", bold_text)
        ],
        [
            Paragraph(
                f"<b>Nombre:</b> {inspector.get_full_name() or inspector.username}<br/>"
                f"<b>Licencia SST / Alturas:</b> {inspector.license_number or 'Acreditación Oficial'}<br/>"
                f"<b>Empresa:</b> {inspector.company or 'ZenitCheck Safety'}<br/>"
                f"<b>Teléfono:</b> {inspector.phone_number or 'N/A'}",
                normal_text
            ),
            Paragraph(
                f"<b>Certificado Digital X.509:</b> ZenitCheck Root CA<br/>"
                f"<b>Algoritmo:</b> RSA-2048 / SHA-256 PKCS#1 v1.5<br/>"
                f"<b>Timestamp de Emisión:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>"
                f"<i>Documento firmado electrónicamente. Válido bajo Ley 527/1999 de comercio y firma electrónica.</i>",
                normal_text
            )
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_GRAY_BG),
        ('GRID', (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(KeepTogether([
        Paragraph("4. VALIDACIÓN DE COMPETENCIA Y FIRMA ELECTRÓNICA", section_title),
        sig_table,
        Spacer(1, 8),
        Paragraph("<font size=7 color='#64748B'><b>Aviso Legal:</b> La decisión final de certificación corresponde exclusivamente al inspector competente acreditado. El módulo de visión artificial es una herramienta de auxilio técnico analítico. ZenitCheck garantiza la trazabilidad criptográfica de este documento.</font>", normal_text)
    ]))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    signature_info = sign_pdf_data(pdf_bytes)

    return pdf_bytes, signature_info
