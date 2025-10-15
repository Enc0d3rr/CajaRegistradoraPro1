import hashlib
import os
import platform

def verificar_archivos_criticos():
    """Verifica integridad de archivos sin afectar licencias"""
    try:
        # Solo verificar que archivos esenciales existen
        archivos_esenciales = [
            'data/config.json',
            'licenses/licencias_manager.py',
            'utils/helpers.py'
        ]
        
        for archivo in archivos_esenciales:
            if not os.path.exists(archivo):
                return False
                
        return True
        
    except Exception:
        return True  # Si falla, no bloquear el software

def generar_hash_unico():
    """Genera un hash único para esta instalación"""
    try:
        # Combinar información del sistema
        info_sistema = {
            'nodo': platform.node(),
            'maquina': platform.machine(),
            'procesador': platform.processor()
        }
        
        hash_unico = hashlib.sha256(
            str(info_sistema).encode()
        ).hexdigest()[:16]
        
        return hash_unico
        
    except Exception:
        return "default_hash"