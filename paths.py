import os
import sys

def get_app_directory():
    """
    Obtiene el directorio base de la aplicación.
    Funciona tanto en desarrollo como cuando está compilado a .exe
    """
    if getattr(sys, 'frozen', False):
        # Si está compilado, la ruta es donde está el ejecutable
        return os.path.dirname(sys.executable)
    else:
        # Si está en desarrollo, la ruta es donde está el script
        return os.path.dirname(os.path.abspath(__file__))

def get_tickets_directory():
    """Obtiene la ruta de la carpeta de tickets"""
    base_dir = get_app_directory()
    tickets_dir = os.path.join(base_dir, "Tickets")
    return tickets_dir

def get_backups_directory():
    """Obtiene la ruta de la carpeta de backups"""
    base_dir = get_app_directory()
    backups_dir = os.path.join(base_dir, "Backups")
    return backups_dir

def ensure_directory_exists(directory_path):
    """
    Asegura que un directorio exista.
    Si no existe, lo crea.
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"✅ Carpeta creada: {directory_path}")
    return directory_path