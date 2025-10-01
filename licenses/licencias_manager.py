# ===== SEGURIDAD AVANZADA =====
import json
import os
import uuid
import hashlib
import hmac
import platform
import subprocess
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class SecurityManager:
    def __init__(self):
        # 🔐 CLAVE MAESTRA COMPATIBLE CON TU GENERADOR
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

class LicenseManagerCorregido:
    def __init__(self):
        self.licencia_path = "data/licencia.json"  # ✅ MISMO FORMATO QUE GENERADOR
        self.config_demo_path = "data/config_demo.json"
        self.tipo_licencia = "demo"
        self.limite_ventas_demo = 50
        self.config_demo = {"ventas_realizadas": 0}
        
        # 🔐 SISTEMA DE SEGURIDAD COMPATIBLE
        self.security = SecurityManager()
        
        # ✅ ID ÚNICO DEL EQUIPO (COMPATIBLE)
        self.equipo_id = self._generar_id_equipo()
        print(f"🖥️ ID del equipo: {self.equipo_id}")
        
        self.cargar_configuracion()
    
    def _generar_id_equipo(self):
        """Genera ID compatible con tu generador"""
        try:
            if platform.system() == "Windows":
                result = subprocess.check_output('wmic csproduct get uuid', shell=True)
                hardware_id = result.decode().split('\n')[1].strip()
            else:
                with open('/etc/machine-id', 'r') as f:
                    hardware_id = f.read().strip()
            
            if not hardware_id:
                hardware_id = str(uuid.getnode())
            
            # ✅ MISMO HASH QUE TU GENERADOR
            salt = "CajaRegistradoraPro2024"
            return hashlib.sha256((hardware_id + salt).encode()).hexdigest()
            
        except Exception as e:
            print(f"⚠️ No se pudo obtener ID hardware: {e}")
            return hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
    
    def cargar_configuracion(self):
        """Cargar configuración - COMPATIBLE con tu generador"""
        try:
            # ✅ CONFIG DEMO
            if os.path.exists(self.config_demo_path):
                with open(self.config_demo_path, 'r') as f:
                    self.config_demo = json.load(f)
            else:
                self.config_demo = {"ventas_realizadas": 0}
                self._guardar_config_demo()
            
            # ✅ LICENCIA (FORMATO DE TU GENERADOR)
            if os.path.exists(self.licencia_path):
                with open(self.licencia_path, 'r', encoding='utf-8') as f:
                    licencia_data = json.load(f)
                
                if self._validar_licencia_generador(licencia_data):
                    self.tipo_licencia = "premium"
                    print("✅ Licencia premium VÁLIDA (formato generador)")
                else:
                    print("❌ Licencia inválida o de otro equipo")
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
                    print(f"❌ Falta campo: {campo}")
                    return False
            
            # ✅ VERIFICAR CHECKSUM (SHA3-512 como tu generador)
            checksum_calculado = self._generar_checksum_compatible(licencia_data)
            if not hmac.compare_digest(licencia_data['checksum'], checksum_calculado):
                print("❌ Checksum inválido")
                return False
            
            # ✅ VERIFICAR HASH HMAC-SHA512 (como tu generador)
            datos_verificacion = {k: v for k, v in licencia_data.items() 
                                if k not in ['hash_seguro', 'datos_encriptados', 'checksum']}
            
            hash_calculado = self.security.generar_hash_seguro(datos_verificacion)
            if not hmac.compare_digest(licencia_data['hash_seguro'], hash_calculado):
                print("❌ Hash de seguridad inválido")
                return False
            
            # ✅ VERIFICAR DATOS ENCRIPTADOS
            try:
                datos_desencriptados = self.security.desencriptar_datos(licencia_data['datos_encriptados'])
                
                # ✅ VERIFICAR EQUIPO_ID EN DATOS ENCRIPTADOS
                if 'equipo_id' in datos_desencriptados:
                    if datos_desencriptados['equipo_id'] != self.equipo_id:
                        print(f"❌ Licencia para equipo diferente: {datos_desencriptados['equipo_id']} != {self.equipo_id}")
                        return False
                else:
                    print("⚠️ Licencia antigua (sin equipo_id)")
                    # Permitir licencias antiguas por compatibilidad
                
            except Exception as e:
                print(f"❌ Error desencriptando datos: {e}")
                return False
            
            # ✅ VERIFICAR EXPIRACIÓN
            fecha_activacion = datetime.fromisoformat(licencia_data['fecha_activacion'])
            fecha_expiracion = fecha_activacion + datetime.timedelta(days=licencia_data['duracion_dias'])
            
            if datetime.now() > fecha_expiracion:
                print("❌ Licencia expirada")
                return False
            
            print("✅ Licencia válida y compatible")
            return True
                
        except Exception as e:
            print(f"❌ Error validando licencia: {e}")
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
        """Activar licencia desde archivo de tu generador"""
        try:
            if not os.path.exists(archivo_licencia):
                return False, "Archivo de licencia no encontrado"
            
            # ✅ CARGAR LICENCIA DE TU GENERADOR
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia_generador = json.load(f)
            
            # ✅ VALIDAR LICENCIA
            if not self._validar_licencia_generador(licencia_generador):
                return False, "Licencia inválida o no compatible con este equipo"
            
            # ✅ COPIAR LICENCIA A DATA/
            os.makedirs(os.path.dirname(self.licencia_path), exist_ok=True)
            with open(self.licencia_path, 'w', encoding='utf-8') as f:
                json.dump(licencia_generador, f, indent=4, ensure_ascii=False)
            
            self.tipo_licencia = "premium"
            print(f"✅ Licencia premium activada desde: {archivo_licencia}")
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
    
    def registrar_venta(self):
        if self.tipo_licencia == "demo":
            self.config_demo["ventas_realizadas"] += 1
            self._guardar_config_demo()
            print(f"📊 Ventas demo: {self.config_demo['ventas_realizadas']}/{self.limite_ventas_demo}")
    
    def _guardar_config_demo(self):
        try:
            os.makedirs(os.path.dirname(self.config_demo_path), exist_ok=True)
            with open(self.config_demo_path, 'w') as f:
                json.dump(self.config_demo, f, indent=4)
        except Exception as e:
            print(f"❌ Error guardando config demo: {e}")