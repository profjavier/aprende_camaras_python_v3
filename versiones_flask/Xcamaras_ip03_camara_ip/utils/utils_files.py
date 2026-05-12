import os
import uuid

from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename):
    """ Verifica si el archivo tiene una extensión permitida """
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    """Guarda la imagen y crea una versión optimizada"""
    if file and allowed_file(file.filename):
        # Generar nombre único para la imagen
        original_filename = secure_filename(file.filename)
        ext = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        # Crear carpetas si no existes
        upload_folder_images= "static/" + current_app.config['UPLOAD_FOLDER_IMAGES']
        os.makedirs(upload_folder_images, exist_ok=True)
        upload_folder_thumbnails= "static/" + current_app.config['UPLOAD_FOLDER_IMAGES_THUMBNAILS']
        os.makedirs(upload_folder_thumbnails, exist_ok=True)

        # Ruta completa del archivo
        filepath_images = os.path.join(upload_folder_images, unique_filename)

        # Guardar y optimizar imagen
        img = Image.open(file)

        # Convertir a RGB si es necesario (para PNG con transparencia)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # Redimensionar manteniendo aspecto
        img.thumbnail(current_app.config['IMAGE_SIZE'], Image.Resampling.LANCZOS)

        # Guardar con calidad optimizada
        img.save(filepath_images, quality=85, optimize=True)

        # Crear thumbnail
        thumbnail_filename = f"thumb_{unique_filename}"
        thumbnail_path =  os.path.join(upload_folder_thumbnails, thumbnail_filename)
        img.thumbnail(current_app.config['THUMBNAIL_SIZE'], Image.Resampling.LANCZOS)
        img.save(thumbnail_path, quality=85, optimize=True)

        return unique_filename, thumbnail_filename

    return None, None