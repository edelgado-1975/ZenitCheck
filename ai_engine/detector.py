"""
ZenitCheck — Motor de IA para Detección de Anomalías en Equipos de Alturas.
Arquitectura desacoplada y reemplazable basada en interfaces abstractas.
Permite alternar entre modelos preentrenados (PyTorch/EfficientNet), OpenCV clásico o servicios cloud.
"""

import abc
import os
import cv2
import numpy as np
from PIL import Image


class BaseDefectDetector(abc.ABC):
    """
    Contrato formal para cualquier motor de visión artificial en ZenitCheck.
    Cualquier nuevo modelo o microservicio de visión debe implementar este método.
    """

    @abc.abstractmethod
    def detect_anomalies(self, image_path, photo_type='OVERALL'):
        """
        Analiza una imagen en busca de anomalías en equipos de altura.

        Retorna una lista de diccionarios con la estructura:
        [
            {
                'defect_type': 'STITCH_FAILURE', # o CUT, CORROSION, etc.
                'severity': 'CRITICAL',           # CRITICAL, MAJOR, MINOR
                'confidence': 0.88,               # Float entre 0.0 y 1.0
                'box_x': 0.25,                    # Coordenada X normalizada (0.0 a 1.0)
                'box_y': 0.30,                    # Coordenada Y normalizada
                'box_width': 0.15,                # Ancho normalizado
                'box_height': 0.20,               # Alto normalizado
                'description': 'Rotura visible en costura de carga estructural'
            },
            ...
        ]
        """
        pass


class ComputerVisionDefectDetector(BaseDefectDetector):
    """
    Detector de visión artificial de alto rendimiento.
    Combina análisis morfológico, análisis espectral de color en espacio HSV y LAB
    (para corrosión y decoloración), detección de bordes y gradientes Canny/Sobel
    (para cortes, deshilachado y rotura de costuras), y detección de contornos irregulares
    (para deformaciones mecánicas).
    """

    def detect_anomalies(self, image_path, photo_type='OVERALL'):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"No se encontró la imagen en: {image_path}")

        findings = []

        # Cargar con OpenCV
        img_bgr = cv2.imread(image_path)
        if img_bgr is None:
            # Fallback con Pillow si OpenCV tiene problemas de ruta en Windows
            pil_img = Image.open(image_path).convert('RGB')
            img_bgr = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

        h, w, _ = img_bgr.shape
        img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

        # -------------------------------------------------------------
        # 1. Detección de Corrosión / Herrumbre (Espacio de Color HSV)
        # Rango de herrumbre: tonos rojizos/naranjas opacos en elementos metálicos
        # -------------------------------------------------------------
        lower_rust = np.array([5, 100, 50])
        upper_rust = np.array([25, 255, 200])
        rust_mask = cv2.inRange(img_hsv, lower_rust, upper_rust)
        rust_ratio = np.sum(rust_mask > 0) / (h * w)

        if rust_ratio > 0.015:  # Más del 1.5% de área con textura de óxido
            contours, _ = cv2.findContours(rust_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if contours:
                c = max(contours, key=cv2.contourArea)
                x, y, bw, bh = cv2.boundingRect(c)
                confidence = min(0.95, round(0.65 + rust_ratio * 3, 2))
                severity = 'CRITICAL' if confidence >= 0.70 else 'MINOR'
                findings.append({
                    'defect_type': 'CORROSION',
                    'severity': severity,
                    'confidence': confidence,
                    'box_x': round(x / w, 4),
                    'box_y': round(y / h, 4),
                    'box_width': round(bw / w, 4),
                    'box_height': round(bh / h, 4),
                    'description': f'Oxidación superficial/corrosión detectada en componente ({rust_ratio*100:.1f}% de área).'
                })

        # -------------------------------------------------------------
        # 2. Detección de Decoloración / Daño UV o Químico
        # Pérdida de saturación en zonas de la cinta textil
        # -------------------------------------------------------------
        saturation = img_hsv[:, :, 1]
        low_sat_mask = cv2.inRange(saturation, 0, 45)
        # Excluir fondos totalmente blancos o negros
        brightness = img_hsv[:, :, 2]
        valid_zone = (brightness > 60) & (brightness < 240)
        discolor_mask = (low_sat_mask > 0) & valid_zone
        discolor_ratio = np.sum(discolor_mask) / (h * w)

        if 0.05 < discolor_ratio < 0.40:
            confidence = min(0.85, round(0.40 + discolor_ratio * 1.2, 2))
            findings.append({
                'defect_type': 'DISCOLORATION',
                'severity': 'MINOR',
                'confidence': confidence,
                'box_x': 0.15,
                'box_y': 0.15,
                'box_width': 0.70,
                'box_height': 0.70,
                'description': f'Zona con posible degradación UV o decoloración química (saturación reducida en {discolor_ratio*100:.1f}%).'
            })

        # -------------------------------------------------------------
        # 3. Detección de Cortes o Discontinuidades Estructurales
        # Bordes pronunciados aislados con gradiente Canny alto
        # -------------------------------------------------------------
        edges = cv2.Canny(img_gray, 100, 200)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=1)
        edge_contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in edge_contours:
            area = cv2.contourArea(c)
            if area > (h * w * 0.02):  # Contorno anómalo grande
                x, y, bw, bh = cv2.boundingRect(c)
                aspect_ratio = bw / float(bh) if bh > 0 else 1.0
                # Relación de aspecto alargada típica de un corte o desgarro
                if aspect_ratio > 3.0 or aspect_ratio < 0.33:
                    findings.append({
                        'defect_type': 'CUT',
                        'severity': 'CRITICAL',
                        'confidence': 0.85,
                        'box_x': round(x / w, 4),
                        'box_y': round(y / h, 4),
                        'box_width': round(bw / w, 4),
                        'box_height': round(bh / h, 4),
                        'description': 'Discontinuidad alargada en patrón de cinta compatible con corte transversal/longitudinal.'
                    })
                    break

        # -------------------------------------------------------------
        # 4. Análisis contextual según tipo de foto técnica (SEAMS, D_RING, LABEL)
        # -------------------------------------------------------------
        if photo_type == 'SEAMS':
            # Análisis de regularidad de textura en costuras
            laplacian_var = cv2.Laplacian(img_gray, cv2.CV_64F).var()
            if laplacian_var < 80.0:  # Textura borrosa / desprendida
                findings.append({
                    'defect_type': 'STITCH_FAILURE',
                    'severity': 'CRITICAL',
                    'confidence': 0.78,
                    'box_x': 0.20,
                    'box_y': 0.30,
                    'box_width': 0.60,
                    'box_height': 0.40,
                    'description': 'Irregularidad detectada en el patrón de puntadas de la costura de carga.'
                })

        return findings


class MockDefectDetector(BaseDefectDetector):
    """
    Detector mock determinista para pruebas unitarias rápidas e independientes.
    """
    def __init__(self, predefined_findings=None):
        self.predefined_findings = predefined_findings or []

    def detect_anomalies(self, image_path, photo_type='OVERALL'):
        return self.predefined_findings


# Factoría para obtener el detector configurado en el sistema
def get_defect_detector():
    """Retorna la implementación configurada del detector."""
    from django.conf import settings
    if getattr(settings, 'AI_USE_MOCK_ENGINE', False):
        return MockDefectDetector()
    return ComputerVisionDefectDetector()
