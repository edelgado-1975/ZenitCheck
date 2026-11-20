"""
Comando para crear usuarios semilla con los tres roles:
- Inspector Técnico
- Supervisor de Seguridad
- Administrador
"""

from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Crea usuarios de prueba para cada rol del sistema.'

    def handle(self, *args, **options):
        users_data = [
            {
                'username': 'inspector1',
                'email': 'inspector@zenitcheck.local',
                'first_name': 'Carlos',
                'last_name': 'Mendoza',
                'role': User.Role.INSPECTOR,
                'license_number': 'SST-COL-2023-8841',
                'company': 'Inspecciones Técnicas del Norte',
                'phone_number': '+57 310 123 4567',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'supervisor1',
                'email': 'supervisor@zenitcheck.local',
                'first_name': 'Dra. Elena',
                'last_name': 'Restrepo',
                'role': User.Role.SUPERVISOR,
                'license_number': 'SST-COL-2018-1092',
                'company': 'Auditorías y Certificaciones Andinas',
                'phone_number': '+57 320 987 6543',
                'is_staff': False,
                'is_superuser': False,
            },
            {
                'username': 'admin1',
                'email': 'admin@zenitcheck.local',
                'first_name': 'Administrador',
                'last_name': 'ZenitCheck',
                'role': User.Role.ADMIN,
                'license_number': 'SST-COL-MASTER-001',
                'company': 'ZenitCheck Central',
                'phone_number': '+57 300 000 0000',
                'is_staff': True,
                'is_superuser': True,
            },
        ]

        password = 'ZenitPass2026!'
        for u_data in users_data:
            username = u_data['username']
            user, created = User.objects.update_or_create(
                username=username,
                defaults=u_data
            )
            user.set_password(password)
            user.save()
            action = 'creado' if created else 'actualizado'
            self.stdout.write(self.style.SUCCESS(f"✓ Usuario {username} ({user.get_role_display()}) {action}."))
