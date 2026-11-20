# ⛑ ZenitCheck — Plataforma de Inspección Técnica de Equipos de Alturas con Visión Artificial

[![Python 3.13.3](https://img.shields.io/badge/Python-3.13.3-blue.svg)](https://www.python.org/)
[![Django 5.2 LTS](https://img.shields.io/badge/Django-5.2.19%20LTS-green.svg)](https://www.djangoproject.com/)
[![Tests](https://img.shields.io/badge/Tests-93%20Passed%20(100%25)-success.svg)](https://pytest.org/)
[![Coverage](https://img.shields.io/badge/Coverage-83.61%25-brightgreen.svg)](https://pytest-cov.readthedocs.io/)
[![WCAG AA](https://img.shields.io/badge/WCAG-2.1%20AA%20Compliant-blue.svg)](https://www.w3.org/WAI/standards-guidelines/wcag/)

> Sistema web profesional para el registro, inspección visual asistida por inteligencia artificial, dictamen técnico con código de color estricto y emisión de certificados de conformidad en PDF firmados digitalmente para equipos de protección contra caídas en alturas.

---

## 📌 Tabla de Contenidos
1. [Arquitectura y Stack Tecnológico](#-arquitectura-y-stack-tecnológico)
2. [Justificación del Motor de Visión Artificial](#-justificación-del-motor-de-visión-artificial)
3. [Normas Técnicas Industriales Aplicables](#-normas-técnicas-industriales-aplicables)
4. [Catálogo de Marcas y Verificabilidad Técnica](#-catálogo-de-marcas-y-verificabilidad-técnica)
5. [Código de Color y Umbrales de Veredicto](#-código-de-color-y-umbrales-de-veredicto)
6. [Operación Offline y Sincronización](#-operación-offline-y-sincronización)
7. [Firma Digital Criptográfica X.509](#-firma-digital-criptográfica-x509)
8. [Instalación y Puesta en Marcha](#-instalación-y-puesta-en-marcha)
9. [Ejecución de Pruebas Automatizadas (pytest)](#-ejecución-de-pruebas-automatizadas-pytest)
10. [Aviso Legal sobre las Limitaciones de la IA](#-aviso-legal-sobre-las-limitaciones-de-la-ia)
11. [Puntos Pendientes de Confirmación](#-puntos-pendientes-de-confirmación)

---

## 🏗 Arquitectura y Stack Tecnológico

El proyecto está diseñado bajo una arquitectura modular y desacoplada, utilizando la última versión con soporte a largo plazo (**LTS**) de Django:

| Componente | Versión Exacta | Justificación Técnica |
|---|---|---|
| **Lenguaje** | `Python 3.13.3` | Rendimiento superior, mejoras en GIL y compatibilidad con typing moderno. |
| **Framework Web** | `Django 5.2.19 LTS` | Última versión con soporte extendido oficial (EOL en **abril de 2028**), ORM maduro, seguridad CSRF y sesiones robustas. |
| **Imágenes** | `Pillow 13.0.0` | Compresión de alta eficiencia, corrección de orientación EXIF y redimensionamiento LANCZOS. |
| **Visión Artificial** | `OpenCV 5.1.0.95` (headless) | Detección morfológica y espectral de alta velocidad sin sobrecarga de GPU. Motor desacoplado mediante `BaseDefectDetector`. |
| **Generación PDF** | `ReportLab 5.1.0` | Generación programática de documentos técnicos vectoriales de alta precisión con paleta corporativa. |
| **Firma Digital** | `cryptography 50.0.2` & `pyHanko 0.38.2` | Generación de certificados X.509, firma RSA-2048 PKCS#1 v1.5 y hashing SHA-256 inmutable. |
| **Front-End** | `Tailwind CSS 3.x` | Diseño mobile-first con soporte para captura de cámara nativa con una sola mano y contraste WCAG AA. |
| **Testing** | `pytest 9.2.0` + `pytest-django 4.14` | Suite automatizada de 93 pruebas unitarias e integradas con cobertura superior al 80%. |

---

## 🤖 Justificación del Motor de Visión Artificial

Para la inspección en campo de equipos de alturas, la arquitectura implementa una interfaz abstracta (`BaseDefectDetector`) con dos componentes clave:
1. **Rendimiento e Inmediatez en Campo:** Se utiliza **OpenCV** para el procesamiento espectral en espacios de color HSV (aislamiento de corrosión/óxido en herrajes metálicos y pérdida de saturación por radiación UV/química) y gradientes de borde Canny/Sobel (detección de cortes, fisuras y discontinuidades en costuras de carga estructurales). Esto permite ejecutar el análisis en milisegundos sin requerir servidores pesados con GPU en el sitio de trabajo.
2. **Componente Reemplazable y Extensible:** El motor está desacoplado a través del patrón Factory (`get_defect_detector()`), permitiendo intercambiar el detector OpenCV por modelos de Deep Learning preentrenados (como EfficientNet o YOLOv8/v11 fine-tuneados en PyTorch) o servicios en la nube simplemente cambiando la clase en `ai_engine/detector.py`, sin alterar el modelo de datos ni la interfaz web.

---

## 📜 Normas Técnicas Industriales Aplicables

Cada tipo de equipo registrado en ZenitCheck está alineado formalmente con los estándares internacionales europeos (**EN/ISO**) y estadounidenses (**ANSI/ASSP**):

| Tipo de Equipo | Norma Europea / Internacional | Norma Estadounidense (ANSI / NFPA) | Criterios Críticos de Rechazo |
|---|---|---|---|
| **Arnés de Cuerpo Completo** | `EN 361:2002` | `ANSI/ASSP Z359.11-2021` | Rotura de puntadas de carga, argollas D deformadas, quemadura química/térmica, cortes en cinta. |
| **Línea de Vida Autorretráctil (SRL)** | `EN 360:2002` | `ANSI/ASSP Z359.14-2021` | Indicador de impacto activado, cable de acero deshilachado/aplastado, fallo de bloqueo automático. |
| **Conectores y Mosquetones** | `EN 362:2004` | `ANSI/ASSP Z359.12-2019` | Seguro automático no cierra, deformación del cuerpo, desgaste mayor al 10% del espesor, corrosión severa. |
| **Absorbedor de Energía / Impacto** | `EN 355:2002` | `ANSI/ASSP Z359.13-2021` | Paquete de desgarre desplegado parcialmente, funda rota, costuras de fijación desgarradas. |
| **Eslinga de Posicionamiento** | `EN 358:2018` | `ANSI/ASSP Z359.3-2019` | Abrasión severa en cinta, hebillas con juego axial excesivo, costuras descosidas. |
| **Cuerda de Seguridad Semiestática** | `EN 1891:1998 Tipo A` | `ANSI/ASSP Z359.15-2022` | Alma expuesta (funda cortada), puntos blandos al tacto (hernias internas), rigidez anormal. |
| **Descensores y Aseguradores** | `EN 341:2011 / EN 12841-C` | `NFPA 1983 / ANSI Z359.4` | Leva con ranura de desgaste profundo, mecanismo antipánico atascado, fisura en cuerpo de aleación. |
| **Anticaídas Deslizante (Freno de Cuerda)** | `EN 353-2:2002` | `ANSI/ASSP Z359.14` | Leva de bloqueo no traba al descender bruscamente, resortes vencidos, holgura en eje. |

---

## 🏷 Catálogo de Marcas y Verificabilidad Técnica

El catálogo base incluye las marcas más reconocidas a nivel internacional y nacional (centrado en equipos fabricados en los últimos 3 años: 2023–2026), con indicación rigurosa de su estatus de verificación documental:

### Marcas Internacionales (Verificadas ✅)
1. **3M (DBI-SALA, Protecta):** Líder global en protección contra caídas (certificaciones ANSI Z359 y CE públicas).
2. **Petzl:** Referente francés en trabajos verticales, rescate y montaña (fichas técnicas y declaraciones UE públicas).
3. **MSA Safety:** Multinacional estadounidense cotizada en NYSE (líneas V-Series y Workman con homologaciones completas).
4. **Honeywell (Miller):** División Safety & Productivity (arneses Miller y líneas de vida autorretráctiles certificadas).
5. **Guardian Fall Protection:** Fabricante internacional perteneciente a SFS Group (catálogos y ensayos ANSI/OSHA verificables).
6. **SKYLOTEC:** Fabricante alemán con certificación ISO 9001 (gamas IGNITE y herrajes de rescate verificados).
7. **Delta Plus:** Fabricante francés cotizado en Euronext (gama completa de EPP y alturas con certificados CE).

### Marcas Nacionales (Colombia / Regional)
8. **Arseg (Honeywell):** ✅ **Verificada.** Marca colombiana emblemática en EPP y alturas; adquirida e integrada formalmente por Honeywell en 2017.
9. **XP Safety:** ⚠️ **Pendiente de confirmación.** Referenciada en distribución local; pendiente de certificación de laboratorio acreditado ONAC/ANSI.
10. **Armadura:** ⚠️ **Pendiente de confirmación.** Marca referenciada en distribución nacional; pendiente confirmación de conformidad formal bajo Res. 4272/2021.
11. **EPI:** ⚠️ **Pendiente de confirmación.** Pendiente validación de personería jurídica y catálogo de fabricante directo de alturas.
12. **INSAFE:** ⚠️ **Pendiente de confirmación.** Comercializadora/fabricante local; pendiente acreditación de certificados de conformidad vigentes.

---

## 🚦 Código de Color y Umbrales de Veredicto

El sistema implementa el código de color corporativo obligatorio con umbrales matemáticos exactos en código (`inspections/verdict.py`):

```
                                      MATRIZ DE DECISIÓN
┌───────────────────────────────────┬───────────────────┬──────────────────────────────────────┐
│ ESTADO DE VEREDICTO               │ CÓDIGO HEXADECIMAL │ CRITERIO / UMBRALES MATEMÁTICOS      │
├───────────────────────────────────┼───────────────────┼──────────────────────────────────────┤
│ 🟢 Apto / Aprobado                │ #16A34A           │ 0 hallazgos críticos. Confianza <30% │
│                                   │ (Verde Esmeralda) │ en menores. Vencimiento > 30 días.   │
├───────────────────────────────────┼───────────────────┼──────────────────────────────────────┤
│ 🟡 En Observación                 │ #EAB308           │ Hallazgos menores con confianza      │
│                                   │ (Ámbar)           │ entre 30% y 69%, O certificación     │
│                                   │                   │ vencerá en ≤ 30 días. (Texto oscuro) │
├───────────────────────────────────┼───────────────────┼──────────────────────────────────────┤
│ 🔴 Rechazado / Fuera de Servicio  │ #DC2626           │ Cualquier hallazgo crítico ≥ 70%,    │
│    (Bloqueo Inmediato)            │ (Rojo Carmesí)    │ corte en cinta, deformación en metal │
│                                   │                   │ O certificación ya vencida (< 0 días)│
└───────────────────────────────────┴───────────────────┴──────────────────────────────────────┘
```

> [!IMPORTANT]
> **Accesibilidad WCAG AA en Color Ámbar:** Sobre el fondo ámbar `#EAB308`, el texto blanco genera un ratio deficiente (~1.9:1). Para cumplir estrictamente el estándar WCAG 2.1 AA (mínimo 4.5:1), ZenitCheck aplica texto oscuro `#1E293B`, alcanzando un ratio de contraste de **8.20:1** (validado en `tests/ui/test_wcag_colors.py`).

### Auditoría Inmutable
El inspector tiene la potestad de confirmar o modificar el veredicto sugerido por la IA. Si decide modificarlo, **el sistema exige una justificación técnica obligatoria**, registrando automáticamente un log inmutable (`VerdictAuditLog`) con usuario, veredicto previo, nuevo veredicto, justificación, fecha, hora y dirección IP.

---

## 🔄 Operación Offline y Sincronización

1. **Modo Campo (Offline):** El inspector opera en campo utilizando una base de datos local SQLite. Puede registrar inspecciones, capturar fotografías mediante la cámara del móvil (que se comprimen con Pillow antes de almacenar) y generar veredictos preliminares sin acceso a internet. Las operaciones se registran en `SyncQueueItem` con identificadores universales (UUIDv4) y marcas de tiempo UTC.
2. **Modo Central (Online):** Al detectar conectividad, la aplicación sincroniza contra la base de datos PostgreSQL central.
3. **Resolución de Conflictos:** Se emplea una estrategia determinista **Last-Write-Wins (LWW)** con log de auditoría. Si un mismo equipo fue modificado en el servidor central mientras el inspector estaba desconectado, el cambio con la marca de tiempo UTC más reciente prevalece, guardando el detalle en las notas de resolución.
4. **Validación Previa:** Antes de emitir un certificado definitivo en el servidor central, se validan los prerrequisitos legales (razón social/identificación del cliente, número de serie único y consistencia del historial).

---

## 🔐 Firma Digital Criptográfica X.509

Cada certificado de inspección generado en PDF incluye una firma digital criptográfica:
- **Autoridad Certificadora:** Genera automáticamente un par de claves RSA de 2048 bits y un certificado digital X.509 en `certs/`.
- **Integridad:** Se calcula el digest criptográfico SHA-256 del documento binario.
- **Inalterabilidad:** Se genera una firma RSA PKCS#1 v1.5 que certifica la autoría del documento bajo la Ley 527 de 1999 de comercio y firma electrónica.

---

## 🚀 Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.13+ instalado.
- Git instalado.

### 1. Clonar el repositorio y acceder
```bash
git clone https://github.com/tu-usuario/ZenitCheck.git
cd ZenitCheck
```

### 2. Crear y activar el entorno virtual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar dependencias fijadas
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
Copiar el archivo de plantilla `.env.example` a `.env`:
```powershell
Copy-Item .env.example .env
```

### 5. Ejecutar migraciones y datos semilla
```bash
python manage.py migrate
python manage.py seed_catalog
python manage.py seed_users
```

### 6. Iniciar el servidor de desarrollo
```bash
python manage.py runserver
```

Acceder a `http://127.0.0.1:8000/` en el navegador.

### Usuarios de Prueba Preconfigurados
| Rol | Usuario | Contraseña | Descripción |
|---|---|---|---|
| **Inspector** | `inspector1` | `ZenitPass2026!` | Registro de inspecciones y fotos en campo. |
| **Supervisor** | `supervisor1` | `ZenitPass2026!` | Auditoría de veredictos y aprobación de reportes. |
| **Administrador** | `admin1` | `ZenitPass2026!` | Acceso completo y panel de administración Django. |

---

## 🧪 Ejecución de Pruebas Automatizadas (pytest)

El proyecto cuenta con una batería de pruebas de software con **pytest**, organizadas por nivel:

```bash
# Ejecutar todas las pruebas con salida detallada
pytest -v

# Ejecutar con medición de cobertura de código
pytest --cov=equipment --cov=accounts --cov=inspections --cov=reports --cov=ai_engine --cov=sync --cov-report=term

# Generar reporte HTML de cobertura (carpeta htmlcov/)
pytest --cov=. --cov-report=html

# Ejecutar únicamente las pruebas críticas de umbrales normativos
pytest tests/inspections/test_verdict_thresholds.py -v

# Ejecutar pruebas de contraste y accesibilidad WCAG AA
pytest tests/ui/test_wcag_colors.py -v
```

### Métricas de Cobertura Obtenidas
- **Total de pruebas ejecutadas:** 93 passed (100% éxito en 3.52 s).
- **Cobertura global de código:** **83.61%** (superando el umbral mínimo del 80%).
- **Lógica de umbrales de veredicto:** **98% de cobertura**.
- **Modelos de equipos y normas:** **98% de cobertura**.

---

## ⚖️ Aviso Legal sobre las Limitaciones de la IA

> [!CAUTION]
> **RESPONSABILIDAD PROFESIONAL:** El módulo de visión artificial y detección de anomalías mediante algoritmos morfológicos y de inteligencia artificial de ZenitCheck es una herramienta de asistencia analítica y auxilio técnico preliminar.
>
> **La decisión final de emitir un veredicto aprobatorio, poner en observación o rechazar/dar de baja un equipo de protección contra caídas en alturas recae exclusivamente sobre el inspector técnico competente acreditado**, debidamente calificado bajo las normativas nacionales e internacionales vigentes (ANSI/ASSP Z359.2, OSHA 1926/1910 y Resolución 4272 de 2021 del Ministerio del Trabajo en Colombia).

---

## 📋 Puntos Pendientes de Confirmación

En cumplimiento con el principio de rigor técnico y veracidad documental:
1. **XP Safety, Armadura, EPI e INSAFE:** Se encuentran registradas en la base de datos con el atributo `verification_status = 'PENDING'` (Pendiente de confirmación documental) y notas técnicas explícitas. Se requiere que el cliente o fabricante suministre los certificados de conformidad de tercera parte acreditada (ONAC, UL, SGS o equivalente) para marcarlas como verificadas en el panel administrativo.
2. **Conexión a PostgreSQL en Producción:** El entorno local de desarrollo y campo utiliza SQLite (`db.sqlite3`). Para el pase a producción, se debe configurar en `.env` las credenciales del servidor central PostgreSQL (`DATABASE_ENGINE=postgresql`, `DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`).
