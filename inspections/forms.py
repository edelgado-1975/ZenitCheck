"""
Formularios de Inspección, Carga de Fotos y Emisión de Veredictos.
"""

from django import forms
from django.core.exceptions import ValidationError
from .models import Inspection, InspectionPhoto
from equipment.models import Equipment
from .image_utils import validate_image_file, compress_image


class MultipleFileInput(forms.FileInput):
    """Widget de carga múltiple compatible con Django 5.2."""
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Campo de formulario que permite múltiples archivos."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={
            'accept': 'image/*',
            'capture': 'environment',
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-3 file:px-6 file:rounded-xl file:border-0 file:text-sm file:font-bold file:bg-zenit-green file:text-white hover:file:bg-green-700 cursor-pointer border border-dashed border-gray-300 rounded-xl p-4 bg-gray-50',
            'aria-label': 'Tomar foto con cámara o seleccionar imágenes'
        }))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)] if data else []
        return result


class InspectionCreateForm(forms.ModelForm):
    photos = MultipleFileField(
        required=False,
        help_text='Captura fotos con la cámara del dispositivo móvil o sube archivos JPG/PNG (máx. 10 MB).'
    )

    class Meta:
        model = Inspection
        fields = ['equipment', 'location', 'general_observations']
        widgets = {
            'equipment': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-gray-900',
                'aria-label': 'Seleccionar equipo de trabajo en alturas'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-gray-900',
                'placeholder': 'Ej: Proyecto Puente Atirantado — Frente 2',
                'aria-label': 'Ubicación física de la inspección'
            }),
            'general_observations': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-gray-900',
                'rows': 3,
                'placeholder': 'Condiciones climáticas, entorno de operación o detalles observados en sitio...',
                'aria-label': 'Observaciones generales del inspector'
            }),
        }


class VerdictConfirmationForm(forms.ModelForm):
    """
    Formulario de confirmación o modificación de veredicto.
    Exige justificación técnica obligatoria si el inspector modifica el veredicto sugerido por la IA.
    """
    class Meta:
        model = Inspection
        fields = ['final_verdict', 'verdict_override_justification', 'general_observations']
        widgets = {
            'final_verdict': forms.RadioSelect(attrs={
                'class': 'focus:ring-green-500 h-5 w-5 text-zenit-green border-gray-300'
            }),
            'verdict_override_justification': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-gray-900',
                'rows': 3,
                'placeholder': 'Debe justificar técnicamente el motivo si el veredicto final difiere del sugerido por la IA...',
                'aria-label': 'Justificación de modificación de veredicto'
            }),
            'general_observations': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 text-gray-900',
                'rows': 2,
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        final_verdict = cleaned_data.get('final_verdict')
        justification = cleaned_data.get('verdict_override_justification', '').strip()

        # Si el veredicto difiere del sugerido por la IA, la justificación es obligatoria
        if self.instance and self.instance.suggested_verdict:
            if final_verdict != self.instance.suggested_verdict and not justification:
                self.add_error(
                    'verdict_override_justification',
                    'Es OBLIGATORIO ingresar una justificación técnica detallada para modificar el veredicto sugerido por la IA.'
                )
        return cleaned_data


class PhotoUploadForm(forms.ModelForm):
    photo_type = forms.ChoiceField(
        choices=InspectionPhoto.PhotoType.choices,
        widget=forms.Select(attrs={'class': 'w-full px-3 py-2 border rounded-lg'})
    )
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'accept': 'image/*',
            'capture': 'environment',
            'class': 'w-full px-3 py-2 border rounded-lg'
        })
    )

    class Meta:
        model = InspectionPhoto
        fields = ['photo_type', 'image', 'notes']

    def clean_image(self):
        uploaded_image = self.cleaned_data.get('image')
        if uploaded_image:
            validate_image_file(uploaded_image)
            compressed = compress_image(uploaded_image)
            return compressed
        return uploaded_image
