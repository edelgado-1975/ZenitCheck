"""
ZenitCheck — Decoradores y Mixins de Control de Acceso Basado en Roles (RBAC).
"""

from functools import wraps
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    """
    Decorador para vistas basadas en funciones.
    Permite el acceso si el rol del usuario está dentro de allowed_roles o si es superusuario.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            if request.user.is_superuser or request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            if hasattr(request, '_messages'):
                messages.error(request, 'No tienes permisos suficientes para acceder a este módulo técnico.')
            raise PermissionDenied('Acceso no autorizado para tu rol.')
        return _wrapped_view
    return decorator


def inspector_required(view_func):
    return role_required(['INSPECTOR', 'SUPERVISOR', 'ADMIN'])(view_func)


def supervisor_required(view_func):
    return role_required(['SUPERVISOR', 'ADMIN'])(view_func)


def admin_required(view_func):
    return role_required(['ADMIN'])(view_func)


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin para vistas basadas en clases que valida roles."""
    allowed_roles = []

    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return user.role in self.allowed_roles

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('accounts:login')
        if hasattr(self.request, '_messages'):
            messages.error(self.request, 'No tienes permisos para acceder a esta vista.')
        raise PermissionDenied('Rol no autorizado.')


class InspectorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['INSPECTOR', 'SUPERVISOR', 'ADMIN']


class SupervisorRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['SUPERVISOR', 'ADMIN']


class AdminRequiredMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']
