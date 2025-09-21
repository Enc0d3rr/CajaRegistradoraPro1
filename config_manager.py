import os
import json
import sys
import platform
import logging
import shutil

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        self.is_windows = platform.system() == "Windows"
        logger.info(f"Sistema operativo detectado: {'Windows' if self.is_windows else 'Linux'}")
        
        # Ruta base compatible
        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.config_path = os.path.join(self.base_path, "data", "config.json")
        self.ensure_config_directory()
        logger.info(f"Ruta de configuración: {self.config_path}")

    def ensure_config_directory(self):
        """Asegurar que el directorio data/ existe con permisos correctos"""
        config_dir = os.path.dirname(self.config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        if self.is_windows:
            try:
                os.chmod(config_dir, 0o777)
                logger.info("Permisos de escritura configurados para Windows")
            except Exception as e:
                logger.warning(f"No se pudieron ajustar permisos en Windows: {e}")

    def load_config(self):
        """Cargar configuración existente o crear por defecto"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info("Configuración cargada exitosamente")
                
                # ✅ ASEGURAR VALORES POR DEFECTO SI FALTAN
                return self.ensure_default_values(config)
            else:
                logger.warning("Archivo de configuración no encontrado, creando uno por defecto")
                return self.create_default_config()
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self.create_default_config()

    def ensure_default_values(self, config):
        """Asegurar que la configuración tenga todos los valores requeridos"""
        default_config = self.create_default_config()
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                logger.warning(f"⚠️ Valor por defecto agregado: {key} = {value}")
        return config

    def update_config(self, new_config):
        """Actualizar configuración con validación y backup"""
        try:
            # Validar configuración básica
            required_keys = ['nombre_negocio', 'color_primario', 'color_secundario']
            for key in required_keys:
                if key not in new_config:
                    raise ValueError(f"Falta clave requerida: {key}")
            
            # ✅ CREAR BACKUP antes de guardar
            if os.path.exists(self.config_path):
                backup_path = self.config_path + ".bak"
                shutil.copy2(self.config_path, backup_path)
                logger.info(f"📦 Backup creado: {backup_path}")
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4, ensure_ascii=False)
            
            if os.path.exists(self.config_path):
                logger.info("✅ Configuración actualizada exitosamente")
                return True
            else:
                logger.error("❌ El archivo de configuración no se creó")
                return False
                
        except PermissionError:
            logger.error("❌ Error de permisos. En Windows, ejecutar como administrador")
            return False
        except Exception as e:
            logger.error(f"❌ Error actualizando configuración: {e}")
            return False

    def create_default_config(self):
        """Crear configuración por defecto"""
        default_config = {
            "nombre_negocio": "Mi Negocio",
            "color_primario": "#3498db",
            "color_secundario": "#2ecc71",
            "logo_path": "logo.png",
            "moneda": "MXN",
            "impuestos": 16.0,
            "direccion": "",
            "telefono": "",
            "rfc": ""
        }
        success = self.update_config(default_config)
        return default_config if success else None

# Instancia global para importar
config_manager = ConfigManager()