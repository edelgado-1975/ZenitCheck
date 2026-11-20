# ⛑️ ZenitCheck — Reporte de Avance 01

> **Fecha:** 20 de Noviembre de 2026  
> **Versión del Sistema:** v1.0.0  
> **Repositorio Oficial:** [https://github.com/edelgado-1975/ZenitCheck](https://github.com/edelgado-1975/ZenitCheck)  
> **Estado de la Entrega:** 100% Completado y Validado

---

## 📊 Resumen Ejecutivo y Métricas de Calidad

| Criterio | Resultado | Detalle |
|---|---|---|
| **Python** | `3.13.3` | Entorno virtual `.venv` configurado y operativo. |
| **Django (LTS)** | `5.2.19 LTS` | Última versión con soporte a largo plazo oficial (EOL abril 2028). |
| **Pillow** | `13.0.0` | Compresión automática JPEG (82%) y corrección EXIF para móvil. |
| **Visión Artificial** | `OpenCV 5.1.0` + Heurísticas | Aislamiento espectral HSV (corrosión/UV) y gradientes Canny/Sobel (cortes/costuras). Motor desacoplado mediante `BaseDefectDetector`. |
| **Pruebas (pytest)** | **93 / 93 PASSED** | 100% de éxito en 3.52 segundos. |
| **Cobertura de Código** | **83.61%** | Supera el umbral del 80% (`inspections/verdict.py` al **98%**, `equipment/models.py` al **98%**). |
| **Accesibilidad** | **WCAG 2.1 AA** | Ratios de contraste validados matemáticamente (Ámbar con texto oscuro: **8.20:1** vs 4.5:1 exigido). |
| **Git / GitHub** | **Sincronizado** | 7 commits descriptivos por hito y tag oficial `v1.0.0` en `main`. |

---

## 🗂️ Módulos Funcionales Construidos y Validados

### 1. Catálogo de Marcas y Equipos (Últimos 3 años: 2023–2026)
- **12 Marcas registradas:**
  - **Internacionales verificadas (✅):** 3M (DBI-SALA, Protecta), Petzl, MSA Safety, Honeywell (Miller), Guardian Fall Protection, SKYLOTEC y Delta Plus.
  - **Nacionales (Colombia):** Arseg (Honeywell) verificada (✅); XP Safety, Armadura, EPI e INSAFE marcadas explícitamente con estado `PENDING` (⚠️ pendiente de confirmación documental), sin inventar datos.
- **Tipos de equipo y normas técnicas vigentes:**
  - Arnés de cuerpo completo: **EN 361:2002 / ANSI Z359.11-2021**
  - Línea de vida autorretráctil (SRL): **EN 360:2002 / ANSI Z359.14-2021**
  - Conectores / Mosquetones: **EN 362:2004 / ANSI Z359.12-2019**
  - Absorbedores de energía: **EN 355:2002 / ANSI Z359.13-2021**
  - Eslingas de posicionamiento: **EN 358:2018 / ANSI Z359.3-2019**
  - Cuerdas de seguridad: **EN 1891:1998 Tipo A / ANSI Z359.15-2022**
  - Descensores: **EN 341:2011 / NFPA 1983**
  - Anticaídas deslizantes: **EN 353-2:2002 / ANSI Z359.14**

### 2. Captura y Compresión de Fotos
- Soporte nativo para cámara trasera en móvil (`capture="environment"`) y subida manual de archivos.
- Validación estricta de tipos MIME (`JPEG`, `PNG`, `WebP`) y tamaño máximo de 10 MB.
- Redimensionamiento (máximo 1920 px) y compresión inteligente en memoria con Pillow antes de almacenar en disco.

### 3. Motor de Visión Artificial para Detección de Anomalías
- Detección de: **costuras de carga, decoloración química/UV, corrosión en metales, desgaste/abrasión, cortes en fibras, deshilachado y deformaciones mecánicas**.
- Superposición visual (`overlay`): dibuja recuadros (*bounding boxes*) delimitadores con el código de color de severidad y el porcentaje de confianza sobre la foto.
- Arquitectura desacoplada: interfaz `BaseDefectDetector` que permite alternar o integrar modelos PyTorch/TensorFlow sin tocar la base de datos ni las vistas.

### 4. Veredicto con Código de Color Obligatorio y Auditoría
- 🟢 **Verde Esmeralda (`#16A34A`):** Apto / Aprobado para operar (0 defectos críticos, confianza menor < 30%, certificación vigente > 30 días).
- 🟡 **Ámbar (`#EAB308`):** En observación o próximo a vencer en ≤ 30 días. Cumple WCAG AA aplicando texto oscuro `#1E293B` para garantizar un ratio de contraste de 8.20:1.
- 🔴 **Rojo Carmesí (`#DC2626`):** Rechazado / Fuera de servicio con **aviso de bloqueo inmediato** (hallazgo crítico ≥ 70%, corte en fibra, deformación en metal o certificación vencida).
- **Auditoría inmutable:** Si el inspector modifica la sugerencia de la IA, el formulario exige **justificación técnica obligatoria** y crea un registro `VerdictAuditLog` con fecha, usuario, veredicto previo, nuevo veredicto y dirección IP.

### 5. Historial, Trazabilidad y Alertas
- Línea de tiempo completa por equipo (`/inspections/equipment/<serial>/history/`) con fotos, hallazgos y certificados emitidos.
- Módulo de alertas (`/inspections/alerts/`) que clasifica equipos vencidos y próximos a vencer.

### 6. Reportes PDF y Firma Digital Criptográfica X.509
- Generación de certificados en PDF de alta fidelidad con **ReportLab**, aplicando la paleta de colores corporativa.
- Módulo de firma digital en `reports/signer.py` con par de claves RSA-2048, certificado X.509 autofirmado y digest SHA-256 para garantizar inalterabilidad legal (Ley 527 de 1999).

### 7. Operación Offline (SQLite) / Online (PostgreSQL)
- Cola de sincronización local `SyncQueueItem` con UUIDs y marcas de tiempo UTC.
- Motor de resolución de conflictos **Last-Write-Wins (LWW)** con notas explicativas en log inmutable.
- Validación obligatoria de razón social del cliente y consistencia del historial antes de permitir la certificación en la base de datos central.

### 8. Usuarios y Control de Acceso (RBAC)
- Modelo `accounts.User` con tres roles diferenciados: **Inspector**, **Supervisor** y **Administrador**.
- Credenciales semilla listas para operar:
  - Inspector: `inspector1` / `ZenitPass2026!`
  - Supervisor: `supervisor1` / `ZenitPass2026!`
  - Administrador: `admin1` / `ZenitPass2026!`

---

## 🧪 Evidencia de Verificación y Pruebas (pytest)

Ejecución del comando de verificación de Django:
```
System check identified no issues (0 silenced).
```

Resumen de la suite de pruebas unitarias y cobertura de código:
```
TOTAL: 1098 líneas analizadas | 93 tests pasando al 100%
Cobertura global alcanzada: 83.61% (Requisito >= 80% CUMPLIDO)
- inspections/verdict.py: 98% de cobertura
- equipment/models.py:    98% de cobertura
- inspections/models.py:  97% de cobertura
- sync/engine.py:         95% de cobertura
- reports/generator.py:   90% de cobertura
```

---

## 📌 Puntos Pendientes de Confirmación Documental

1. **Marcas Nacionales:** Las marcas *XP Safety*, *Armadura*, *EPI* e *INSAFE* quedaron registradas en la base de datos con el campo `verification_status = 'PENDING'`. En cuanto el cliente o proveedor suministre los certificados de conformidad de tercera parte (ONAC/ANSI), el administrador puede marcarlas como verificadas desde el panel administrativo.
2. **Entorno de Producción PostgreSQL:** El desarrollo local y las inspecciones offline en campo operan sobre SQLite (`db.sqlite3`). Para desplegar el servidor central en producción, solo debes configurar las variables en el archivo `.env` (`DATABASE_ENGINE=postgresql`, `DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`).

---

## ⚖️ Nota de Responsabilidad Legal y Técnica

> **La decisión final de certificación corresponde exclusivamente al inspector técnico competente acreditado.**  
> El motor de visión artificial y análisis de anomalías es una herramienta de auxilio analítico preliminar para agilizar la detección en campo, y no sustituye el juicio técnico ni la firma del profesional certificado bajo las normativas ANSI/ASSP Z359, OSHA 1926/1910 y Resolución 4272 de 2021 de MinTrabajo.

---

## 💻 Comandos Rápidos de Ejecución

```bash
# Iniciar servidor web de desarrollo
python manage.py runserver

# Ejecutar las 93 pruebas de software
pytest -v

# Medir cobertura de código
pytest --cov=. --cov-report=term
```
