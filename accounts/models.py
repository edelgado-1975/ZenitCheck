"""
ZenitCheck — Modelo de Usuario y Roles.
Soporta Inspector, Supervisor y Administrador con campos profesionales para trazabilidad.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Usuario extendido para el sistema de inspección de alturas.
    Roles diferenciados:
    - INSPECTOR: Registra inspecciones, toma fotos y ejecuta análisis en campo.
    - SUPERVISOR: Audita veredictos, aprueba certificados y revisa reportes.
    - ADMIN: Gestión de catálogo, usuarios y configuraciones del sistema.
    """

    class Role(models.TextChoices):
        INSPECTOR = 'INSPECTOR', 'Inspector Técnico'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor de Seguridad'
        ADMIN = 'ADMIN', 'Administrador del Sistema'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.INSPECTOR,
        verbose_name='Rol en el Sistema',
        help_text='Define los permisos y nivel de acceso en la plataforma.'
    )
    license_number = models.CharField(
        max_length=60,
        blank=True,
        verbose_name='Número de Licencia / Certificación SST',
        help_text='Número de acreditación como inspector de trabajo seguro en alturas.'
    )
    phone_number = models.CharField(
        max_length=25,
        blank=True,
        verbose_name='Teléfono de Contacto'
    )
    company = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Empresa u Organización'
    )
    digital_signature_stamp = models.ImageField(
        upload_to='signatures/',
        null=True,
        blank=True,
        verbose_name='Sello / Rúbrica Digital (Imagen opcional)',
        help_text='Imagen PNG transparente con firma manuscrita para imprimir en el PDF.'
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['username']

    def __str__(self):
        full_name = self.get_full_name()
        display = full_name if full_name else self.username
        return f"{display} ({self.get_role_display()})"

    @property
    def is_inspector(self):
        return self.role == self.Role.INSPECTOR or self.is_superuser

    @property
    def is_supervisor(self):
        return self.role == self.Role.SUPERVISOR or self.is_superuser

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser
