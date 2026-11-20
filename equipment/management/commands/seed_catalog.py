"""
ZenitCheck — Comando de datos semilla (Seed Catalog).
Carga las marcas nacionales e internacionales (con indicación de verificabilidad),
los tipos de equipo con normas EN y ANSI vigentes, y equipos de demostración fabricados
en los últimos 3 años (2023-2026).
"""

from datetime import date, timedelta
from django.core.management.base import BaseCommand
from equipment.models import Brand, EquipmentType, Equipment, Accessory


class Command(BaseCommand):
    help = 'Carga el catálogo inicial con las marcas, tipos de equipo con normas EN/ANSI y equipos semilla.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Iniciando carga de catálogo de alturas ZenitCheck...'))

        # ============================================================
        # 1. Tipos de Equipo y Normas Vigentes
        # ============================================================
        equipment_types_data = [
            {
                'code': 'HARNESS_FULL_BODY',
                'name': 'Arnés de Cuerpo Completo',
                'standard_international': 'EN 361:2002',
                'standard_us': 'ANSI/ASSP Z359.11-2021',
                'inspection_interval_months': 12,
                'max_lifespan_years': 10,
                'critical_points': 'Costuras principales de carga, argollas dorsales/esternales tipo D, hebillas de ajuste, etiquetas de inspección legibles, tejido sintético sin cortes ni quemaduras.',
                'description': 'Dispositivo de prensión del cuerpo destinado a parar las caídas.'
            },
            {
                'code': 'RETRACTABLE_LIFELINE',
                'name': 'Línea de Vida Autorretráctil (SRL)',
                'standard_international': 'EN 360:2002',
                'standard_us': 'ANSI/ASSP Z359.14-2021',
                'inspection_interval_months': 12,
                'max_lifespan_years': 10,
                'critical_points': 'Mecanismo de frenado centrífugo, estado del cable de acero o cinta, indicador de caída accionado, carcasa sin fracturas, mosquetón giratorio (destorcedor).',
                'description': 'Dispositivo anticaídas con función de bloqueo automático y sistema de retroceso.'
            },
            {
                'code': 'CONNECTOR_CARABINER',
                'name': 'Conector / Mosquetón de Seguridad',
                'standard_international': 'EN 362:2004',
                'standard_us': 'ANSI/ASSP Z359.12-2019',
                'inspection_interval_months': 12,
                'max_lifespan_years': 15,
                'critical_points': 'Cierre automático y bloqueo de seguridad funcional (triple acción / doble seguro), sin corrosión severa ni rebabas, desgaste de cuerpo menor al 10% del espesor, resorte sin fatiga.',
                'description': 'Elemento de conexión o componente de un sistema anticaídas.'
            },
            {
                'code': 'ENERGY_ABSORBER',
                'name': 'Absorbedor de Impacto / Energía',
                'standard_international': 'EN 355:2002',
                'standard_us': 'ANSI/ASSP Z359.13-2021',
                'inspection_interval_months': 12,
                'max_lifespan_years': 10,
                'critical_points': 'Funda protectora intacta, sin despliegue del paquete de desgarre de energía, costuras de seguridad íntegras, sin daño térmico ni químico.',
                'description': 'Elemento que limita la fuerza máxima de impacto sobre el cuerpo a menos de 6 kN (EN) o 8 kN (ANSI).'
            },
            {
                'code': 'POSITIONING_BELT',
                'name': 'Eslinga y Cinturón de Posicionamiento',
                'standard_international': 'EN 358:2018',
                'standard_us': 'ANSI/ASSP Z359.3-2019',
                'inspection_interval_months': 12,
                'max_lifespan_years': 10,
                'critical_points': 'Costuras de fijación a argollas laterales, cinta textil sin abrasión, hebillas de graduación sin holgura.',
                'description': 'Dispositivo para sujetar al usuario en su lugar de trabajo con manos libres (no apto para detención de caídas libre).'
            },
            {
                'code': 'SAFETY_ROPE',
                'name': 'Cuerda de Seguridad Semiestática',
                'standard_international': 'EN 1891:1998 Tipo A',
                'standard_us': 'ANSI/ASSP Z359.15-2022',
                'inspection_interval_months': 12,
                'max_lifespan_years': 10,
                'critical_points': 'Funda sin cortes ni deshilachado (alma expuesta), sin herniaciones o puntos blandos al tacto, extremos termoterminados con etiqueta.',
                'description': 'Cuerda textil de bajo alargamiento con funda y alma para progresión y rescate.'
            },
            {
                'code': 'DESCENDER',
                'name': 'Descensor Manual y Dispositivo de Evacuación',
                'standard_international': 'EN 341:2011 / EN 12841-C',
                'standard_us': 'NFPA 1983 / ANSI Z359.4',
                'inspection_interval_months': 12,
                'max_lifespan_years': 12,
                'critical_points': 'Leva de frenado sin desgaste excesivo, palanca antipánico operativa, leva de bloqueo sin trabamiento.',
                'description': 'Aparato que permite descender a velocidad regulada por una cuerda.'
            },
            {
                'code': 'FALL_ARRESTER_SLIDER',
                'name': 'Dispositivo Anticaídas Deslizante (Freno de Cuerda/Cable)',
                'standard_international': 'EN 353-2:2002',
                'standard_us': 'ANSI/ASSP Z359.14 / Z359.15',
                'inspection_interval_months': 12,
                'max_lifespan_years': 12,
                'critical_points': 'Mecanismo de leva de bloqueo instantáneo al descender súbitamente, sin deformación en cuerpo de aleación, compatibilidad con diámetro de cuerda certificada.',
                'description': 'Dispositivo que acompaña al usuario y se bloquea automáticamente en caso de caída sobre línea de anclaje flexible.'
            },
        ]

        types_created = 0
        for data in equipment_types_data:
            obj, created = EquipmentType.objects.update_or_create(
                code=data['code'],
                defaults=data
            )
            if created:
                types_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {types_created} tipos de equipo registrados / actualizados con normas EN y ANSI.'))

        # ============================================================
        # 2. Catálogo de Marcas (10+ Internacionales y Nacionales)
        # ============================================================
        brands_data = [
            # --- Internacionales ---
            {
                'name': '3M (DBI-SALA, Protecta)',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Estados Unidos',
                'website': 'https://www.3m.com/fallprotection',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Fabricante líder global tras adquirir Capital Safety (marcas DBI-SALA y Protecta). Certificaciones ANSI/ASSP Z359 y CE/EN disponibles públicamente.'
            },
            {
                'name': 'Petzl',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Francia',
                'website': 'https://www.petzl.com',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Fabricante histórico referente en trabajos verticales, rescate y montaña. Fichas técnicas y declaraciones UE de conformidad públicas para cada equipo.'
            },
            {
                'name': 'MSA Safety',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Estados Unidos',
                'website': 'https://www.msasafety.com',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Empresa pública cotizada en NYSE (MSA). Fabricante de las líneas V-Series, V-FIT y Workman. Documentación técnica certificada bajo ANSI y EN.'
            },
            {
                'name': 'Honeywell (Miller)',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Estados Unidos',
                'website': 'https://sps.honeywell.com/miller',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Línea de protección contra caídas Miller by Honeywell. Cumple normas ANSI Z359 y EN. Manuales y certificados de homologación verificables.'
            },
            {
                'name': 'Guardian Fall Protection',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Estados Unidos / Reino Unido',
                'website': 'https://guardianfall.com',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Parte de SFS Group. Catálogos técnicos y fichas de prueba de laboratorio bajo norma ANSI y OSHA 1926/1910 verificables.'
            },
            {
                'name': 'SKYLOTEC',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Alemania',
                'website': 'https://www.skylotec.com',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Fabricante alemán con certificación ISO 9001. Especialista en arneses IGNITE y líneas SKYLOTEC. Normas CE EN y ANSI verificadas.'
            },
            {
                'name': 'Delta Plus',
                'origin': Brand.Origin.INTERNATIONAL,
                'country': 'Francia',
                'website': 'https://www.deltaplus.eu',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Compañía multinacional francesa cotizada en Euronext. Catálogo de protección en alturas (gama Froment y Delta Plus) con certificados CE públicos.'
            },

            # --- Nacionales (Colombia / Regional) ---
            {
                'name': 'Arseg (Honeywell)',
                'origin': Brand.Origin.NATIONAL,
                'country': 'Colombia',
                'website': 'https://sps.honeywell.com',
                'verification_status': Brand.VerificationStatus.VERIFIED,
                'verification_notes': 'Marca colombiana histórica con más de 60 años en EPP y alturas en Bogotá. Adquirida e integrada formalmente por Honeywell en 2017. Verificada en registros de industria y comercio.'
            },
            {
                'name': 'XP Safety',
                'origin': Brand.Origin.NATIONAL,
                'country': 'Colombia',
                'website': '',
                'verification_status': Brand.VerificationStatus.PENDING,
                'verification_notes': 'Marca referenciada en el mercado de seguridad industrial en Colombia. Pendiente confirmación documental de laboratorio acreditado ONAC/ANSI y ficha técnica oficial.'
            },
            {
                'name': 'Armadura',
                'origin': Brand.Origin.NATIONAL,
                'country': 'Colombia',
                'website': '',
                'verification_status': Brand.VerificationStatus.PENDING,
                'verification_notes': 'Marca nacional referenciada en distribución de EPP en Colombia. Pendiente confirmación de certificados de conformidad bajo Resolución 4272 de 2021 de MinTrabajo.'
            },
            {
                'name': 'EPI',
                'origin': Brand.Origin.NATIONAL,
                'country': 'Colombia / Regional',
                'website': '',
                'verification_status': Brand.VerificationStatus.PENDING,
                'verification_notes': 'Sigla habitual de Equipos de Protección Individual o marca local. Pendiente confirmación de personería jurídica y catálogo de fabricante de alturas.'
            },
            {
                'name': 'INSAFE',
                'origin': Brand.Origin.NATIONAL,
                'country': 'Colombia',
                'website': '',
                'verification_status': Brand.VerificationStatus.PENDING,
                'verification_notes': 'Comercializadora / fabricante de líneas de seguridad en Colombia. Pendiente de verificación formal de certificados de conformidad vigentes.'
            },
        ]

        brands_created = 0
        for data in brands_data:
            obj, created = Brand.objects.update_or_create(
                name=data['name'],
                defaults=data
            )
            if created:
                brands_created += 1

        self.stdout.write(self.style.SUCCESS(f'✓ {brands_created} marcas registradas / actualizadas (con etiquetas de verificación técnica).'))

        # ============================================================
        # 3. Equipos de Demostración Semilla (Últimos 3 años: 2023-2026)
        # ============================================================
        today = date.today()
        harness_type = EquipmentType.objects.get(code='HARNESS_FULL_BODY')
        srl_type = EquipmentType.objects.get(code='RETRACTABLE_LIFELINE')
        carabiner_type = EquipmentType.objects.get(code='CONNECTOR_CARABINER')
        absorber_type = EquipmentType.objects.get(code='ENERGY_ABSORBER')

        brand_3m = Brand.objects.get(name='3M (DBI-SALA, Protecta)')
        brand_petzl = Brand.objects.get(name='Petzl')
        brand_msa = Brand.objects.get(name='MSA Safety')
        brand_honeywell = Brand.objects.get(name='Honeywell (Miller)')
        brand_skylotec = Brand.objects.get(name='SKYLOTEC')

        sample_equipments = [
            {
                'brand': brand_3m,
                'equipment_type': harness_type,
                'model_name': 'DBI-SALA ExoFit STRATA (4 Argollas)',
                'serial_number': '3M-EXO-2024-98412',
                'manufacturing_date': date(2024, 3, 15),
                'first_use_date': date(2024, 4, 1),
                'last_inspection_date': today - timedelta(days=60),
                'certification_expiry_date': today + timedelta(days=305),
                'status': Equipment.Status.OPERATIONAL,
                'client_name': 'Consorcio Vial Metropolitano',
                'location_assigned': 'Frente 3 - Puente Atirantado',
                'notes': 'Arnés de cuerpo completo ergonómico. Inspección visual previa satisfactoria.'
            },
            {
                'brand': brand_petzl,
                'equipment_type': harness_type,
                'model_name': 'AVAO BOD FAST (Internacional)',
                'serial_number': 'PET-AVAO-2023-45109',
                'manufacturing_date': date(2023, 8, 20),
                'first_use_date': date(2023, 9, 10),
                'last_inspection_date': today - timedelta(days=340),
                'certification_expiry_date': today + timedelta(days=25),  # Próximo a vencer (Ámbar)
                'status': Equipment.Status.OBSERVATION,
                'client_name': 'Mantenimiento Eólico SAS',
                'location_assigned': 'Torre Aerogenerador 12',
                'notes': 'Certificación próxima a expirar en menos de 30 días. Requiere re-inspección inmediata.'
            },
            {
                'brand': brand_msa,
                'equipment_type': srl_type,
                'model_name': 'V-SHOCK 6m Mini Retráctil',
                'serial_number': 'MSA-VSHK-2024-00129',
                'manufacturing_date': date(2024, 1, 10),
                'first_use_date': date(2024, 2, 1),
                'last_inspection_date': today - timedelta(days=400),
                'certification_expiry_date': today - timedelta(days=35),  # Vencido (Rojo)
                'status': Equipment.Status.OUT_OF_SERVICE,
                'client_name': 'Estructuras Andinas SA',
                'location_assigned': 'Bodega Central de Equipos',
                'notes': 'Certificación expirada hace 35 días. Bloqueado automáticamente hasta recertificación.'
            },
            {
                'brand': brand_honeywell,
                'equipment_type': absorber_type,
                'model_name': 'Miller Manyard HP Shock-Absorbing Lanyard',
                'serial_number': 'HON-MAN-2025-11048',
                'manufacturing_date': date(2025, 2, 5),
                'first_use_date': date(2025, 2, 20),
                'last_inspection_date': today - timedelta(days=30),
                'certification_expiry_date': today + timedelta(days=335),
                'status': Equipment.Status.OPERATIONAL,
                'client_name': 'Petroquímica del Caribe',
                'location_assigned': 'Planta Hidrocarburos Tanque 4',
                'notes': 'Eslinga con absorbedor doble ramal en Y con ganchos de 2 1/4".'
            },
            {
                'brand': brand_skylotec,
                'equipment_type': carabiner_type,
                'model_name': 'OVALSTEEL Tri-Lock 30kN',
                'serial_number': 'SKY-CAR-2024-88301',
                'manufacturing_date': date(2024, 6, 1),
                'first_use_date': date(2024, 6, 15),
                'last_inspection_date': today - timedelta(days=120),
                'certification_expiry_date': today + timedelta(days=245),
                'status': Equipment.Status.OPERATIONAL,
                'client_name': 'Telecomunicaciones del Sur',
                'location_assigned': 'Antena Repetidora Cerro Verde',
                'notes': 'Mosquetón oval de acero con seguro automático triple acción.'
            },
        ]

        equipments_created = 0
        for eq_data in sample_equipments:
            obj, created = Equipment.objects.update_or_create(
                serial_number=eq_data['serial_number'],
                defaults=eq_data
            )
            if created:
                equipments_created += 1
                # Crear accesorio de ejemplo
                Accessory.objects.get_or_create(
                    equipment=obj,
                    name='Mosquetón de anclaje rápido al arnés',
                    defaults={
                        'serial_number': f'ACC-{obj.serial_number[-5:]}',
                        'brand': obj.brand,
                        'is_critical': True,
                        'notes': 'Verificado solidario al conjunto.'
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'✓ {equipments_created} equipos de demostración (2023-2026) registrados con accesorios.'))
        self.stdout.write(self.style.SUCCESS('Catálogo semilla cargado exitosamente.'))
