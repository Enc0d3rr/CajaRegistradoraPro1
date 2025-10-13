# ===== SEGURIDAD AVANZADA =====
# ===== SEGURIDAD AVANZADA =====
import json
import os
import uuid
import hashlib
import hmac
import platform
import subprocess
import socket
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityManager:
    def __init__(self):
        # 🔐 CLAVE MAESTRA 
        self.master_key = self.derive_key("CAJA_REGISTRADORA_PRO_2024_SECRET_KEY_¡NO_COMPARTIR!")
        self.fernet = Fernet(self.master_key)
    
    def derive_key(self, password: str) -> bytes:
        """MISMA clave que tu generador - PARA COMPATIBILIDAD"""
        salt = b'caja_registradora_salt_2024_secure_v2'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def generar_hash_seguro(self, datos: dict) -> str:
        """MISMO hash HMAC-SHA512 que tu generador"""
        datos_ordenados = {k: datos[k] for k in sorted(datos.keys())}
        cadena = ''.join(str(v) for v in datos_ordenados.values())
        
        return hmac.new(
            self.master_key, 
            cadena.encode(), 
            hashlib.sha512
        ).hexdigest()
    
    def encriptar_datos(self, datos: dict) -> str:
        """MISMA encriptación que tu generador"""
        datos_str = json.dumps(datos, sort_keys=True)
        return self.fernet.encrypt(datos_str.encode()).decode()
    
    def desencriptar_datos(self, datos_encriptados: str) -> dict:
        """MISMA desencriptación que tu generador"""
        try:
            datos_bytes = self.fernet.decrypt(datos_encriptados.encode())
            return json.loads(datos_bytes.decode())
        except Exception as e:
            raise ValueError(f"Error desencriptando datos: {e}")

class LicenseManager:
    def __init__(self):
        self.licencia_path = "data/licencia.json"  
        self.config_demo_path = "data/config_demo.json"
        self.tipo_licencia = "demo"
        self.limite_ventas_demo = 50
        self.config_demo = {"ventas_realizadas": 0}
        
        # 🔐 SISTEMA DE SEGURIDAD COMPATIBLE
        self.security = SecurityManager()
        
        # ID ÚNICO DEL EQUIPO 
        self.equipo_id = self._generar_id_equipo()
        
        self.cargar_configuracion()
    
    def _generar_id_equipo(self):
        """Genera ID COMPATIBLE entre Linux y Windows - VERSIÓN PROFESIONAL"""
        try:
            import socket
            import platform
            
            # BASE COMPATIBLE Y ESTABLE
            hostname = socket.gethostname().lower().strip()
            sistema = platform.system().lower()
            arquitectura = platform.machine().lower()
            
            id_base = f"{hostname}_{sistema}_{arquitectura}"
            
            equipo_id = hashlib.sha3_512(id_base.encode()).hexdigest()[:32]
            
            return equipo_id
            
        except Exception as e:
            print(f"❌ Error generando ID: {e}")
            import socket
            fallback_base = f"fallback_{socket.gethostname()}"
            return hashlib.sha3_512(fallback_base.encode()).hexdigest()[:32]
    
    def cargar_configuracion(self):
        """Cargar configuración - COMPATIBLE con tu generador"""
        try:
            # CONFIG DEMO
            if os.path.exists(self.config_demo_path):
                with open(self.config_demo_path, 'r') as f:
                    self.config_demo = json.load(f)
            else:
                self.config_demo = {"ventas_realizadas": 0}
                self._guardar_config_demo()
            
            # LICENCIA PREMIUM
            if os.path.exists(self.licencia_path):
                with open(self.licencia_path, 'r', encoding='utf-8') as f:
                    licencia_data = json.load(f)
                
                if self._validar_licencia_generador(licencia_data):
                    self.tipo_licencia = "premium"
                    print("✅ Licencia premium válida y activa")
                else:
                    print("❌ Licencia inválida o expirada")
                    self.tipo_licencia = "demo"
            else:
                self.tipo_licencia = "demo"
                print("🔓 Modo demo activado")
                
        except Exception as e:
            print(f"❌ Error cargando licencia: {e}")
            self.tipo_licencia = "demo"
    
    def _validar_licencia_generador(self, licencia_data):
        """Validar licencia en formato de TU GENERADOR"""
        try:
            # ✅ VERIFICAR ESTRUCTURA BÁSICA
            if not isinstance(licencia_data, dict):
                return False
            
            campos_requeridos = ['codigo', 'hash_seguro', 'datos_encriptados', 'checksum']
            for campo in campos_requeridos:
                if campo not in licencia_data:
                    return False
            
            # ✅ VERIFICAR CHECKSUM
            checksum_calculado = self._generar_checksum_compatible(licencia_data)
            if not hmac.compare_digest(licencia_data['checksum'], checksum_calculado):
                return False
            
            # ✅ VERIFICAR HASH HMAC-SHA512
            datos_verificacion = {k: v for k, v in licencia_data.items() 
                                if k not in ['hash_seguro', 'datos_encriptados', 'checksum']}
            
            hash_calculado = self.security.generar_hash_seguro(datos_verificacion)
            if not hmac.compare_digest(licencia_data['hash_seguro'], hash_calculado):
                return False
            
            # ✅ VERIFICAR DATOS ENCRIPTADOS
            try:
                datos_desencriptados = self.security.desencriptar_datos(licencia_data['datos_encriptados'])
                
                # ✅ VERIFICAR EQUIPO_ID
                if 'equipo_id' in datos_desencriptados:
                    equipo_id_licencia = datos_desencriptados['equipo_id']
                    if equipo_id_licencia != self.equipo_id:
                        return False
                
            except Exception as e:
                return False
            
            # ✅ VERIFICAR EXPIRACIÓN
            try:
                fecha_activacion = datetime.fromisoformat(licencia_data['fecha_activacion'])
                fecha_expiracion = fecha_activacion + timedelta(days=licencia_data['duracion_dias'])
                
                if datetime.now() > fecha_expiracion:
                    return False
                    
            except Exception as e:
                return False
            
            return True
                
        except Exception as e:
            return False
    
    def _generar_checksum_compatible(self, licencia_data):
        """Generar checksum compatible con tu generador"""
        datos_integridad = {
            'codigo': licencia_data['codigo'],
            'hash_seguro': licencia_data['hash_seguro'],
            'fecha_generacion': licencia_data['fecha_generacion'],
            'version': licencia_data.get('version', '2.0')
        }
        datos_ordenados = {k: datos_integridad[k] for k in sorted(datos_integridad.keys())}
        cadena = ''.join(str(v) for v in datos_ordenados.values())
        return hashlib.sha3_512(cadena.encode()).hexdigest()
    
    def activar_licencia(self, archivo_licencia):
        """Activar licencia desde archivo"""
        try:
            if not os.path.exists(archivo_licencia):
                return False, "Archivo de licencia no encontrado"
            
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia_generador = json.load(f)
            
            if not self._validar_licencia_generador(licencia_generador):
                return False, "Licencia inválida o no compatible con este equipo"
            
            # ✅ COPIAR LICENCIA A DATA/
            os.makedirs(os.path.dirname(self.licencia_path), exist_ok=True)
            with open(self.licencia_path, 'w', encoding='utf-8') as f:
                json.dump(licencia_generador, f, indent=4, ensure_ascii=False)
            
            self.tipo_licencia = "premium"
            return True, "Licencia activada exitosamente"
            
        except Exception as e:
            return False, f"Error activando licencia: {str(e)}"
        
    def validar_licencia(self):
        """Validar licencia actual"""
        if self.tipo_licencia == "premium":
            if os.path.exists(self.licencia_path):
                with open(self.licencia_path, 'r', encoding='utf-8') as f:
                    licencia_data = json.load(f)
                return self._validar_licencia_generador(licencia_data)
        
        if self.tipo_licencia == "demo":
            if self.config_demo["ventas_realizadas"] >= self.limite_ventas_demo:
                return False
        
        return self.tipo_licencia == "premium"
    
    def obtener_info_licencia(self):
        """Obtiene información de la licencia actual"""
        try:
            if self.tipo_licencia == "premium" and os.path.exists(self.licencia_path):
                with open(self.licencia_path, 'r', encoding='utf-8') as f:
                    licencia_data = json.load(f)
                
                fecha_activacion = datetime.fromisoformat(licencia_data['fecha_activacion'])
                fecha_expiracion = fecha_activacion + timedelta(days=licencia_data['duracion_dias'])
                dias_restantes = (fecha_expiracion - datetime.now()).days
                
                # Determinar tipo de plan
                tipo_plan = licencia_data.get('tipo', 'premium')
                if licencia_data['duracion_dias'] >= 36500:
                    tipo_plan = "perpetua"
                elif licencia_data['duracion_dias'] == 365:
                    tipo_plan = "anual"
                
                return {
                    'tipo': 'premium',
                    'plan': tipo_plan,
                    'estado': 'activa',
                    'dias_restantes': dias_restantes,
                    'expiracion': fecha_expiracion.strftime('%d/%m/%Y'),
                    'codigo': licencia_data['codigo'],
                    'seguridad': 'avanzada'
                }
            else:
                # Modo demo
                ventas_restantes = max(0, self.limite_ventas_demo - self.config_demo["ventas_realizadas"])
                estado = 'activa' if ventas_restantes > 0 else 'expirada'
                
                return {
                    'tipo': 'demo',
                    'plan': 'demo',
                    'estado': estado,
                    'dias_restantes': ventas_restantes,
                    'expiracion': 'N/A',
                    'codigo': 'DEMO',
                    'mensaje': f'Ventas restantes: {ventas_restantes}/{self.limite_ventas_demo}',
                    'seguridad': 'básica'
                }
                
        except Exception as e:
            return {
                'tipo': 'error',
                'estado': 'error',
                'dias_restantes': 0,
                'expiracion': 'N/A',
                'codigo': 'ERROR'
            }
    
    def registrar_venta(self):
        """Registrar venta en contador demo"""
        if self.tipo_licencia == "demo":
            self.config_demo["ventas_realizadas"] += 1
            self._guardar_config_demo()
    
    def _guardar_config_demo(self):
        """Guardar configuración demo"""
        try:
            os.makedirs(os.path.dirname(self.config_demo_path), exist_ok=True)
            with open(self.config_demo_path, 'w') as f:
                json.dump(self.config_demo, f, indent=4)
        except Exception as e:
            print(f"❌ Error guardando config demo: {e}")

    def obtener_equipo_id(self):
        """Obtener ID del equipo para generar licencias"""
        return self.equipo_id