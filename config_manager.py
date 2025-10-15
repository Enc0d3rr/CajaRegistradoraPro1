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
                
                # ✅ LLAMAR A LA VERIFICACIÓN SEGURA
                verificar_configuracion_segura(config)  # <-- ESTA LÍNEA SE AGREGA
                
                # ✅ ASEGURAR VALORES POR DEFECTO SI FALTAN
                return self.ensure_default_values(config)
            else:
                logger.warning("Archivo de configuración no encontrado, creando uno por defecto")
                return self.create_default_config()
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            return self.create_default_config()

    def ensure_default_values(self, config):
        """Asegurar que la configuración tenga todos los valores requeridos - SIN RECURSIÓN"""
        
        # ✅ VALORES POR DEFECTO DIRECTOS (sin llamar a create_default_config)
        valores_por_defecto = {
            'nombre_negocio': 'Mi Negocio',
            'color_primario': '#3498db', 
            'color_secundario': '#2ecc71',
            'logo_path': 'logo.png',
            'moneda': 'MXN',
            'impuestos': 16.0,
            'direccion': '',
            'telefono': '', 
            'rfc': '',
            'tema': 'claro'
        }
        
        config_actualizada = config.copy()
        
        for key, default_value in valores_por_defecto.items():
            if key not in config_actualizada or config_actualizada[key] is None or config_actualizada[key] == '':
                config_actualizada[key] = default_value
                print(f"⚠️ Valor por defecto agregado: {key} = {default_value}")
        
        return config_actualizada

    def update_config(self, new_config):
        """Actualizar configuración - VERSIÓN SIMPLIFICADA Y SEGURA"""
        try:
            print(f"💾 Guardando configuración...")
            
            # 1. CARGAR CONFIGURACIÓN ACTUAL (sin procesar)
            config_actual = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config_actual = json.load(f)
            
            # 2. COMBINAR CONFIGURACIONES
            config_actualizada = {**config_actual, **new_config}
            
            # 3. APLICAR VALORES POR DEFECTO SOLO SI FALTAN
            config_final = self.ensure_default_values(config_actualizada)
            
            # 4. GUARDAR DIRECTAMENTE
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config_final, f, indent=4, ensure_ascii=False)
            
            print("✅ Configuración guardada exitosamente")
            print(f"📋 Configuración final: {config_final}")
            return True
                
        except Exception as e:
            print(f"❌ ERROR guardando configuración: {str(e)}")
            return False

    def create_default_config(self):
        """Crear configuración por defecto - SIN LLAMAR A update_config"""
        default_config = {
            "nombre_negocio": "Mi Negocio",
            "color_primario": "#3498db",
            "color_secundario": "#2ecc71", 
            "logo_path": "logo.png",
            "moneda": "MXN",
            "impuestos": 16.0,
            "direccion": "",
            "telefono": "",
            "rfc": "",
            "tema": "claro"
        }
        
        # GUARDAR DIRECTAMENTE SIN LLAMAR A update_config
        try:
            print("🔄 Creando configuración por defecto...")
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=4, ensure_ascii=False)
            
            print("✅ Configuración por defecto creada exitosamente")
            return default_config
            
        except Exception as e:
            print(f"❌ Error creando configuración por defecto: {e}")
            return default_config  # Retornar igual aunque falle el guardado

# Instancia global para importar
config_manager = ConfigManager()

# === SEGURIDAD ADICIONAL - FUERA DE LA CLASE ===
def verificar_configuracion_segura(config):
    """Verifica configuración sin romper funcionalidad - FUERA DE CLASE"""
    try:
        # Verificar campos esenciales
        campos_esenciales = ['nombre_negocio', 'tema', 'impuestos']  # Cambié 'iva' por 'impuestos'
        
        for campo in campos_esenciales:
            if campo not in config:
                print(f"⚠️  Campo esencial faltante: {campo}")
                return False
                
        return True
        
    except Exception as e:
        print(f"⚠️  Error en verificación segura: {e}")
        return True  # No bloquear si hay error