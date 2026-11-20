"""
ZenitCheck — Superposición Gráfica de Hallazgos de IA sobre Imágenes.
Dibuja cajas delimitadoras (bounding boxes), etiquetas y niveles de confianza con código de color estricto.
"""

import os
from PIL import Image, ImageDraw, ImageFont


COLOR_MAP = {
    'CRITICAL': '#DC2626',  # Rojo Carmesí
    'MAJOR': '#EAB308',     # Ámbar
    'MINOR': '#16A34A',     # Verde Esmeralda
}


def draw_defect_overlays(input_image_path, findings, output_image_path=None):
    """
    Superpone los bounding boxes y textos de los hallazgos sobre la imagen.

    Parámetros:
    - input_image_path: Ruta a la imagen original.
    - findings: Lista de diccionarios o modelos DefectFinding.
    - output_image_path: Ruta donde guardar la imagen resultante. Si es None, sobreescribe o crea _analyzed.

    Retorna la ruta absoluta del archivo resultante.
    """
    if not os.path.exists(input_image_path):
        raise FileNotFoundError(f"No existe el archivo de imagen: {input_image_path}")

    img = Image.open(input_image_path).convert('RGB')
    draw = ImageDraw.Draw(img)
    w, h = img.size

    for finding in findings:
        # Extraer coordenadas
        bx = getattr(finding, 'box_x', None) or (finding.get('box_x') if isinstance(finding, dict) else 0.0)
        by = getattr(finding, 'box_y', None) or (finding.get('box_y') if isinstance(finding, dict) else 0.0)
        bw = getattr(finding, 'box_width', None) or (finding.get('box_width') if isinstance(finding, dict) else 0.2)
        bh = getattr(finding, 'box_height', None) or (finding.get('box_height') if isinstance(finding, dict) else 0.2)
        d_type = getattr(finding, 'defect_type', '') or (finding.get('defect_type', '') if isinstance(finding, dict) else '')
        severity = getattr(finding, 'severity', 'CRITICAL') or (finding.get('severity', 'CRITICAL') if isinstance(finding, dict) else 'CRITICAL')
        conf = getattr(finding, 'confidence', 0.0) if hasattr(finding, 'confidence') else (finding.get('confidence', 0.0) if isinstance(finding, dict) else 0.0)

        # Coordenadas en píxeles absolutos
        left = int(bx * w)
        top = int(by * h)
        right = int((bx + bw) * w)
        bottom = int((by + bh) * h)

        color = COLOR_MAP.get(severity, '#DC2626')

        # Dibujar rectángulo grueso
        box_width_px = max(3, int(min(w, h) * 0.005))
        for i in range(box_width_px):
            draw.rectangle(
                [left - i, top - i, right + i, bottom + i],
                outline=color
            )

        # Etiqueta de texto con fondo
        label_text = f" {d_type} ({conf:.0%}) "
        # Dibujar fondo de texto para legibilidad alta
        text_bbox = draw.textbbox((left, max(0, top - 22)), label_text)
        draw.rectangle(text_bbox, fill=color)
        draw.text((left, max(0, top - 22)), label_text, fill='#FFFFFF')

    if output_image_path is None:
        base, ext = os.path.splitext(input_image_path)
        output_image_path = f"{base}_analyzed{ext}"

    os.makedirs(os.path.dirname(os.path.abspath(output_image_path)), exist_ok=True)
    img.save(output_image_path, format='JPEG', quality=88)
    return output_image_path
