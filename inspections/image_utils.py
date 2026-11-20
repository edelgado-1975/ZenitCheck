"""
ZenitCheck — Utilidades de Procesamiento y Compresión de Imágenes con Pillow.
Garantiza validación estricta de tipos MIME, tamaño máximo y compresión óptima antes de guardar.
"""

import io
import os
from PIL import Image, ImageOps
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile


MAX_IMAGE_DIMENSION = 1920  # Límite superior para optimizar almacenamiento y velocidad en móvil
JPEG_QUALITY = 82           # Relación compresión/calidad óptima recomendada
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB máximo


def validate_image_file(file_obj):
    """
    Valida el tamaño y formato de la imagen cargada.
    Lanza ValidationError si no cumple las especificaciones de seguridad.
    """
    if file_obj.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"El archivo excede el tamaño máximo permitido de 10 MB (Tamaño: {file_obj.size / (1024*1024):.1f} MB).")

    try:
        # Abrir con Pillow para validar integridad de bytes
        img = Image.open(file_obj)
        img.verify()
        file_obj.seek(0)
    except Exception as exc:
        raise ValidationError("El archivo proporcionado no es una imagen válida o está dañado.") from exc

    ext = os.path.splitext(file_obj.name)[1].lower()
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    if ext not in allowed_extensions:
        raise ValidationError(f"Extensión no permitida: {ext}. Formatos aceptados: JPG, PNG, WebP.")


def compress_image(image_file, max_dimension=MAX_IMAGE_DIMENSION, quality=JPEG_QUALITY):
    """
    Comprime y redimensiona una imagen con Pillow manteniendo la orientación EXIF correcta.
    Retorna un nuevo InMemoryUploadedFile listo para guardar en el ImageField.
    """
    image_file.seek(0)
    img = Image.open(image_file)

    # Corregir orientación según metadata EXIF (clave para fotos tomadas con móvil en campo)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # Convertir a RGB si viene en RGBA o P
    if img.mode in ('RGBA', 'P', 'LA'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')

    # Redimensionar si excede el tamaño máximo manteniendo aspect ratio
    width, height = img.size
    if width > max_dimension or height > max_dimension:
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Guardar en buffer en memoria como JPEG optimizado
    output_io = io.BytesIO()
    img.save(output_io, format='JPEG', quality=quality, optimize=True)
    output_io.seek(0)

    # Generar nombre normalizado
    base_name = os.path.splitext(image_file.name)[0]
    new_filename = f"{base_name}_compressed.jpg"

    return InMemoryUploadedFile(
        file=output_io,
        field_name='image',
        name=new_filename,
        content_type='image/jpeg',
        size=output_io.getbuffer().nbytes,
        charset=None
    )
