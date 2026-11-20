"""
Pruebas de Accesibilidad de Color WCAG AA.
Valida matemáticamente que los ratios de contraste de los colores de veredicto
cumplan el estándar WCAG AA:
- UI Componentes / Texto Grande (≥ 14pt bold): Ratio mínimo 3.0:1 (Criterio 1.4.11 y 1.4.3).
- Texto Normal: Ratio mínimo 4.5:1 (Criterio 1.4.3).
- Texto oscuro (#1E293B) obligatorio sobre fondo Ámbar (#EAB308) para superar 4.5:1.
"""

import pytest


def hex_to_relative_luminance(hex_str):
    """Calcula la luminancia relativa según la fórmula oficial W3C WCAG 2.1."""
    hex_str = hex_str.lstrip('#')
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0

    def adjust(val):
        return val / 12.92 if val <= 0.03928 else ((val + 0.055) / 1.055) ** 2.4

    r_adj, g_adj, b_adj = adjust(r), adjust(g), adjust(b)
    return 0.2126 * r_adj + 0.7152 * g_adj + 0.0722 * b_adj


def calculate_contrast_ratio(hex1, hex2):
    """Calcula el ratio de contraste (L1 + 0.05) / (L2 + 0.05)."""
    l1 = hex_to_relative_luminance(hex1)
    l2 = hex_to_relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


class TestWCAGColorAccessibility:
    def test_approved_green_contrast_with_white_text(self):
        """
        Verde Esmeralda #16A34A con texto blanco #FFFFFF.
        Cumple WCAG 2.1 Nivel AA para insignias (badges), componentes de interfaz y texto destacado (>= 3.0:1).
        """
        ratio = calculate_contrast_ratio('#16A34A', '#FFFFFF')
        assert ratio >= 3.0, f"Debe cumplir mínimo 3.0:1 para badges y texto grande (Obtenido: {ratio:.2f}:1)"

    def test_approved_green_body_text_contrast(self):
        """Texto verde oscuro en fondos claros para legibilidad AA (>= 4.5:1)."""
        ratio = calculate_contrast_ratio('#15803D', '#FFFFFF')
        assert ratio >= 4.5

    def test_amber_contrast_with_dark_text(self):
        """CRÍTICO: Ámbar #EAB308 DEBE usar texto oscuro (#1E293B) para cumplir WCAG AA >= 4.5:1."""
        dark_text = '#1E293B'
        amber_bg = '#EAB308'
        ratio = calculate_contrast_ratio(amber_bg, dark_text)
        assert ratio >= 4.5, f"El contraste de Ámbar con texto oscuro debe ser >= 4.5:1 (Obtenido: {ratio:.2f}:1)"

    def test_amber_with_white_fails_wcag_justifying_dark_text(self):
        """Demuestra por qué el texto blanco sobre ámbar es inaccesible (ratio ~ 1.9:1 < 4.5:1)."""
        white_text = '#FFFFFF'
        amber_bg = '#EAB308'
        ratio = calculate_contrast_ratio(amber_bg, white_text)
        assert ratio < 4.5  # Justifica el requisito de usar texto oscuro sobre ámbar

    def test_rejected_crimson_contrast_with_white_text(self):
        """Rojo Carmesí #DC2626 con texto blanco #FFFFFF (>= 4.5:1)."""
        ratio = calculate_contrast_ratio('#DC2626', '#FFFFFF')
        assert ratio >= 4.5
