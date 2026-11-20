"""
ZenitCheck — Lógica y Umbrales Explícitos para Veredictos de Inspección.
Alineado con normas ANSI Z359 y EN 361/360/362/355/358.

CÓDIGO DE COLORES OBLIGATORIO:
- Verde Esmeralda (#16A34A): Apto / Aprobado para operar.
- Ámbar (#EAB308): En observación o próximo a vencer certificación (texto oscuro para WCAG AA).
- Rojo Carmesí (#DC2626): Rechazado / Fuera de servicio con aviso de bloqueo inmediato.
"""

from datetime import date
from django.conf import settings


# Códigos de color corporativos oficiales
HEX_APPROVED = '#16A34A'     # Verde Esmeralda
HEX_OBSERVATION = '#EAB308'  # Ámbar
HEX_REJECTED = '#DC2626'     # Rojo Carmesí

# Umbrales explícitos
CRITICAL_CONFIDENCE_THRESHOLD = 0.70  # ≥ 70% en hallazgo crítico → ROJO
OBSERVATION_CONFIDENCE_MIN = 0.30     # 30% - 69% en hallazgo o menor → ÁMBAR
DAYS_BEFORE_EXPIRY_ALERT = 30         # ≤ 30 días para vencimiento → ÁMBAR


# Anomalías intrínsecamente críticas según normas EN/ANSI
CRITICAL_DEFECT_TYPES = {
    'STITCH_FAILURE',   # Rotura de costura de carga estructural
    'CUT',              # Corte en cinta de fibra o cable
    'DEFORMATION',      # Deformación mecánica en metal (mosquetón, argolla D)
    'LABEL_UNREADABLE', # Pérdida total de trazabilidad del fabricante
}

# Anomalías de severidad moderada / observacional
OBSERVATION_DEFECT_TYPES = {
    'DISCOLORATION',    # Decoloración química o solar moderada
    'WEAR_ABRASION',    # Abrasión superficial
    'FRAYING',          # Deshilachado menor de orillas
    'CORROSION',        # Corrosión incipiente sin pérdida de sección
}


def calculate_inspection_verdict(equipment, findings=None, today=None):
    """
    Calcula el veredicto sugerido y las razones técnicas de la decisión.

    Parámetros:
    - equipment: Instancia de Equipment (o mock con certification_expiry_date)
    - findings: Lista de diccionarios o instancias DefectFinding con 'defect_type', 'severity', 'confidence'
    - today: date opcional para control de tiempo en tests

    Retorna una tupla: (verdict_code, hex_color, reasons_list, is_critical_lock)
    """
    if today is None:
        today = date.today()

    findings = findings or []
    reasons = []

    # 1. Regla Crítica: Certificación del equipo ya vencida (> 12 meses o fecha pasada)
    if equipment.certification_expiry_date:
        days_remaining = (equipment.certification_expiry_date - today).days
        if days_remaining < 0:
            reasons.append(f"Certificación del equipo VENCIDA hace {abs(days_remaining)} días. Fuera de servicio por norma.")
            return ('REJECTED', HEX_REJECTED, reasons, True)

    # 2. Regla Crítica: Hallazgos críticos con confianza ≥ 70% o defectos intrínsecamente fatales
    has_critical_defect = False
    has_observation_defect = False

    for f in findings:
        # Extraer atributos compatibles con modelos o diccionarios
        d_type = getattr(f, 'defect_type', None) or (f.get('defect_type') if isinstance(f, dict) else None)
        sev = getattr(f, 'severity', None) or (f.get('severity') if isinstance(f, dict) else None)
        conf = getattr(f, 'confidence', 0.0) if hasattr(f, 'confidence') else (f.get('confidence', 0.0) if isinstance(f, dict) else 0.0)

        # Caso crítico
        if (d_type in CRITICAL_DEFECT_TYPES and conf >= CRITICAL_CONFIDENCE_THRESHOLD) or sev == 'CRITICAL' and conf >= CRITICAL_CONFIDENCE_THRESHOLD:
            has_critical_defect = True
            reasons.append(f"Hallazgo crítico detectado: {d_type} con confianza {conf:.0%} (umbral ≥ {CRITICAL_CONFIDENCE_THRESHOLD:.0%}).")
        # Caso observación
        elif conf >= OBSERVATION_CONFIDENCE_MIN:
            has_observation_defect = True
            reasons.append(f"Anomalía en observación detectada: {d_type} con confianza {conf:.0%}.")

    if has_critical_defect:
        return ('REJECTED', HEX_REJECTED, reasons, True)

    # 3. Regla Ámbar: Certificación próxima a expirar en ≤ 30 días
    if equipment.certification_expiry_date:
        days_remaining = (equipment.certification_expiry_date - today).days
        if 0 <= days_remaining <= DAYS_BEFORE_EXPIRY_ALERT:
            reasons.append(f"Certificación vigente próxima a expirar en {days_remaining} días (umbral de alerta ≤ {DAYS_BEFORE_EXPIRY_ALERT} días).")
            return ('OBSERVATION', HEX_OBSERVATION, reasons, False)

    # 4. Regla Ámbar: Hallazgos de severidad moderada
    if has_observation_defect:
        return ('OBSERVATION', HEX_OBSERVATION, reasons, False)

    # 5. Regla Verde Esmeralda: 0 hallazgos críticos, equipo vigente y en óptimas condiciones
    reasons.append("Equipo apto y operativo. Sin anomalías críticas detectadas y certificación vigente.")
    return ('APPROVED', HEX_APPROVED, reasons, False)
