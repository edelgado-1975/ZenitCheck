# ZenitCheck — Plan de Trabajo por Hitos

> **Aplicación Django para inspección de equipos de trabajo en alturas con visión artificial**

## Entorno Confirmado

| Componente | Versión | Notas |
|---|---|---|
| Python | 3.13.3 | Última versión estable |
| Django | 5.2.19 LTS | Soporte extendido LTS (EOL abril 2028) |
| Pillow | 13.0.0 | Procesamiento y compresión de imágenes |
| OpenCV | 5.1.0.95 | Visión artificial y análisis morfológico/color |
| ReportLab | 5.1.0 | Generación programática de certificados PDF |
| Cryptography | 50.0.2 | Firma digital X.509 y hashing criptográfico |
| Git | 2.56.1 | Control de versiones |
| Testing | pytest 9.2.0 | Cobertura total > 80% (83.61% alcanzado) |

---

## Hitos de Ejecución

### Hito 0 · Fundación del Proyecto ⏱ [COMPLETADO]
- [x] Inicializar repositorio Git con `.gitignore` exhaustivo
- [x] Entorno virtual con Python 3.13.3 y Django 5.2.19 LTS
- [x] `requirements.txt` con versiones fijadas
- [x] Estructura modular de apps: `accounts`, `equipment`, `inspections`, `reports`, `ai_engine`, `sync`
- [x] Configuración desacoplada en `zenitcheck/settings/` (base, dev, prod, test) con variables en `.env`
- [x] Integración de Tailwind CSS responsivo y accesible
- [x] Configuración de pytest en `pyproject.toml`
- **Resultado:** Commit `1a2ddd0`. `python manage.py runserver` y pytest operativos sin errores.

### Hito 1 · Modelos de Datos y Catálogo 🗄️ [COMPLETADO]
- [x] Modelos: `Brand`, `EquipmentType`, `Equipment`, `Accessory`
- [x] Campos normativos: serial único, fecha fabricación (2023-2026), última inspección, vencimiento
- [x] Normas aplicables por tipo de equipo (ANSI Z359 y EN 360/361/362/355/358/1891/341/353)
- [x] Migraciones iniciales y comando seed: `python manage.py seed_catalog`
- [x] Catálogo con 12 marcas (7 internacionales verificadas y 5 nacionales con estado explícito de verificación)
- [x] Admin Django personalizado con filtros, inlines y date_hierarchy
- [x] 🧪 Tests automatizados con `factory_boy` en `tests/equipment/` (16 tests pasando al 100%)
- **Resultado:** Commit `4145577`.

### Hito 2 · Autenticación y Roles 🔐 [COMPLETADO]
- [x] Modelo `User` extendido con roles: Inspector, Supervisor, Administrador
- [x] Atributos profesionales: Licencia SST/alturas, empresa, teléfono y sello digital
- [x] Sistema de permisos RBAC con decoradores y mixins: `inspector_required`, `supervisor_required`, `admin_required`
- [x] Vistas de login/logout con protección CSRF y redirección por rol
- [x] Comando seed de usuarios de prueba: `python manage.py seed_users`
- [x] 🧪 Tests de modelos, autenticación y permisos en `tests/accounts/` (15 tests pasando al 100%)
- **Resultado:** Commit `c48f5bb`.

### Hito 3 · Captura de Fotos y Gestión de Imágenes 📷 [COMPLETADO]
- [x] Modelo `InspectionPhoto` con tipos de toma técnica (costuras, argollas, cintas, etiquetas, etc.)
- [x] Captura directa con cámara móvil (`capture="environment"`) y subida manual
- [x] Validación estricta de tipo MIME y tamaño máximo (10 MB)
- [x] Compresión y redimensionamiento inteligente con Pillow (JPEG 82% manteniendo EXIF)
- [x] 🧪 Tests de carga, compresión y relación fotográfica en `tests/inspections/` (5 tests pasando al 100%)
- **Resultado:** Commit `5e5e8f2`.

### Hito 4 · Motor de IA para Detección de Anomalías 🤖 [COMPLETADO]
- [x] Módulo `ai_engine` con arquitectura abstracta desacoplada (`BaseDefectDetector`)
- [x] Detector por visión artificial (`ComputerVisionDefectDetector`): costuras, decoloración UV/química, corrosión en metales, desgaste, cortes, deshilachado y deformación
- [x] Generador de superposición gráfica de hallazgos (`draw_defect_overlays`) con bounding boxes coloreados
- [x] Modelo `DefectFinding` con coordenadas relativas, severidad y nivel de confianza
- [x] 🧪 Tests de analizador, tipos de anomalía, confianza y superposición en `tests/ai_engine/` (5 tests pasando al 100%)
- **Resultado:** Commit `5e5e8f2`.

### Hito 5 · Veredicto con Código de Color Obligatorio 🚦 [COMPLETADO]
- [x] Implementación estricta de umbrales en `inspections/verdict.py`:
  - 🟢 **Verde Esmeralda `#16A34A`:** Apto / Aprobado para operar (0 críticos, certificación vigente).
  - 🟡 **Ámbar `#EAB308`:** En observación / Próximo a vencer en ≤ 30 días (con texto oscuro `#1E293B` para WCAG AA).
  - 🔴 **Rojo Carmesí `#DC2626`:** Rechazado / Fuera de servicio con aviso de bloqueo inmediato (hallazgo crítico ≥ 70% o certificación vencida).
- [x] Flujo de confirmación y anulación por el inspector con justificación técnica obligatoria
- [x] Modelo `VerdictAuditLog` con trazabilidad inmutable (quién, cuándo, veredicto anterior, nuevo, justificación, IP)
- [x] 🧪 Tests parametrizados de matriz de veredictos, colores y auditoría en `tests/inspections/` (19 tests pasando al 100%)
- **Resultado:** Commit `5e5e8f2`.

### Hito 6 · Historial, Trazabilidad y Alertas 📋 [COMPLETADO]
- [x] Línea de tiempo histórica por equipo (`/equipment/<serial>/history/`)
- [x] Módulo de alertas técnicas preventivas (`/alerts/`) para equipos vencidos y próximos a vencer
- [x] Panel de métricas operativas en tiempo real en el Dashboard
- [x] 🧪 Tests de historial, alertas y dashboard en `tests/inspections/` (3 tests pasando al 100%)
- **Resultado:** Commit `475daf1`.

### Hito 7 · Generación de Reportes PDF y Firma Digital 📄 [COMPLETADO]
- [x] Generador de certificados oficiales en PDF con ReportLab (`reports/generator.py`)
- [x] Aplicación rigurosa de colores corporativos (#1E293B, #16A34A, #EAB308, #DC2626)
- [x] Módulo de firma digital criptográfica X.509 (`reports/signer.py`) con par RSA-2048 y digest SHA-256
- [x] Descarga directa y vista previa con cabeceras de integridad criptográfica
- [x] 🧪 Tests de generación PDF, colores, firma X.509 y contenido en `tests/reports/` (5 tests pasando al 100%)
- **Resultado:** Commit `14b145c`.

### Hito 8 · Sincronización Offline/Online 🔄 [COMPLETADO]
- [x] Modelo `SyncQueueItem` con cola de operaciones locales (UUID, entidad, operación, payload JSON)
- [x] Motor de sincronización con resolución de conflictos "Last-Write-Wins" (LWW) y notas inmutables
- [x] Validación obligatoria de datos del cliente e historial antes de certificar en la BD central
- [x] Consistencia de almacenamiento de imágenes entre SQLite y PostgreSQL
- [x] 🧪 Tests de cola, LWW, validación previa y consistencia de fotos en `tests/sync/` (5 tests pasando al 100%)
- **Resultado:** Commit `14b145c`.

### Hito 9 · UI/UX Responsiva y Accesibilidad WCAG AA ♿ [COMPLETADO]
- [x] Plantillas Tailwind CSS optimizadas para operación en campo con una sola mano en móvil
- [x] Compatibilidad con navegadores modernos: Chrome, Firefox, Safari y Edge
- [x] Verificación matemática de ratio de contraste WCAG AA (≥ 4.5:1 para texto normal, texto oscuro sobre ámbar)
- [x] Indicadores visuales de carga (loading spinners) durante compresión y análisis de IA
- [x] 🧪 Tests de estados HTTP 200, validación de formularios y fórmulas de luminancia WCAG en `tests/ui/` (6 tests pasando al 100%)
- **Resultado:** Commit `475daf1`.

### Hito 10 · Tests Finales, Documentación y Cierre 🚀 [COMPLETADO]
- [x] Suite completa de 93 pruebas unitarias e integradas pasando al 100%
- [x] Cobertura de código alcanzada: **83.61%** (superando el 80% requerido)
- [x] `requirements.txt` congelado con versiones exactas
- [x] Documentación técnica completa en `README.md`
- [x] Tag de versión `v1.0.0`
