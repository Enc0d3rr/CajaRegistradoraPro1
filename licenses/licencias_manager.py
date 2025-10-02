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
        print(f"🖥️ ID del equipo: {self.equipo_id}")
        
        self.cargar_configuracion()
    
    def _generar_id_equipo(self):
        """Genera ID PORTABLE entre Linux y Windows - IDÉNTICO AL GENERADOR"""
        try:
            import socket
            
            # EXACTAMENTE LA MISMA LÓGICA QUE EL GENERADOR
            hostname = socket.gethostname()
            mac_address = uuid.getnode()
            mac = ':'.join(['{:02x}'.format((mac_address >> elements) & 0xff) 
                        for elements in range(0,2*6,2)][::-1])
            
            id_base = f"{hostname}_{mac}"
            
            print(f"🔍 Validador - Base PORTABLE: {id_base}")
            
            equipo_id = hashlib.sha3_512(id_base.encode()).hexdigest()[:32]
            print(f"✅ Validador - ID PORTABLE: {equipo_id}")
            
            return equipo_id
            
        except Exception as e:
            print(f"❌ Error generando ID portable: {e}")
            import socket
            fallback_base = f"portable_{socket.gethostname()}"
            fallback_id = hashlib.sha3_512(fallback_base.encode()).hexdigest()[:32]
            return fallback_id
    
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
            
            # LICENCIA (FORMATO DE TU GENERADOR)
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
        """Validar licencia en formato de TU GENERADOR - VERSIÓN CON DEBUG"""
        try:
            print(f"🔍 INICIANDO VALIDACIÓN DE LICENCIA...")
            
            # ✅ VERIFICAR ESTRUCTURA BÁSICA
            if not isinstance(licencia_data, dict):
                print("❌ Licencia no es un diccionario")
                return False
            
            campos_requeridos = ['codigo', 'hash_seguro', 'datos_encriptados', 'checksum']
            for campo in campos_requeridos:
                if campo not in licencia_data:
                    print(f"❌ Falta campo requerido: {campo}")
                    return False
            
            print("✅ Estructura básica OK")
            
            # ✅ VERIFICAR CHECKSUM (SHA3-512 como tu generador)
            checksum_calculado = self._generar_checksum_compatible(licencia_data)
            if not hmac.compare_digest(licencia_data['checksum'], checksum_calculado):
                print("❌ Checksum inválido")
                print(f"   Esperado: {checksum_calculado[:32]}...")
                print(f"   Recibido: {licencia_data['checksum'][:32]}...")
                return False
            
            print("✅ Checksum OK")
            
            # ✅ VERIFICAR HASH HMAC-SHA512 (como tu generador)
            datos_verificacion = {k: v for k, v in licencia_data.items() 
                                if k not in ['hash_seguro', 'datos_encriptados', 'checksum']}
            
            hash_calculado = self.security.generar_hash_seguro(datos_verificacion)
            if not hmac.compare_digest(licencia_data['hash_seguro'], hash_calculado):
                print("❌ Hash de seguridad inválido")
                print(f"   Esperado: {hash_calculado[:32]}...")
                print(f"   Recibido: {licencia_data['hash_seguro'][:32]}...")
                return False
            
            print("✅ Hash de seguridad OK")
            
            # ✅ VERIFICAR DATOS ENCRIPTADOS
            try:
                datos_desencriptados = self.security.desencriptar_datos(licencia_data['datos_encriptados'])
                print("✅ Datos desencriptados OK")
                
                # ✅ VERIFICAR EQUIPO_ID EN DATOS ENCRIPTADOS
                if 'equipo_id' in datos_desencriptados:
                    equipo_id_licencia = datos_desencriptados['equipo_id']
                    equipo_id_actual = self.equipo_id
                    
                    print(f"🔍 Comparando equipo_id:")
                    print(f"   Licencia: {equipo_id_licencia}")
                    print(f"   Actual:   {equipo_id_actual}")
                    
                    if equipo_id_licencia != equipo_id_actual:
                        print(f"❌ Licencia para equipo diferente")
                        print(f"   Licencia: {equipo_id_licencia[:32]}...")
                        print(f"   Actual:   {equipo_id_actual[:32]}...")
                        return False
                    else:
                        print("✅ Equipo_id coincide")
                else:
                    print("⚠️ Licencia antigua (sin equipo_id)")
                    # Permitir licencias antiguas por compatibilidad
                
            except Exception as e:
                print(f"❌ Error desencriptando datos: {e}")
                return False
            
            # ✅ VERIFICAR EXPIRACIÓN
            try:
                fecha_activacion = datetime.fromisoformat(licencia_data['fecha_activacion'])
                fecha_expiracion = fecha_activacion + timedelta(days=licencia_data['duracion_dias'])
                
                if datetime.now() > fecha_expiracion:
                    print("❌ Licencia expirada")
                    return False
                else:
                    dias_restantes = (fecha_expiracion - datetime.now()).days
                    print(f"✅ Licencia vigente - {dias_restantes} días restantes")
            except Exception as e:
                print(f"❌ Error verificando expiración: {e}")
                return False
            
            print("🎉 ✅ LICENCIA VÁLIDA Y COMPATIBLE")
            return True
                
        except Exception as e:
            print(f"❌ Error general validando licencia: {e}")
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
        """Activar licencia desde archivo de tu generador - VERSIÓN DEBUG"""
        try:
            print(f"🎫 Intentando activar licencia: {archivo_licencia}")
            
            if not os.path.exists(archivo_licencia):
                return False, "Archivo de licencia no encontrado"
            
            # ✅ CARGAR LICENCIA DE TU GENERADOR
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia_generador = json.load(f)
            
            # ✅ DEBUG TEMPORAL
            print("=== DEBUG ACTIVACIÓN ===")
            resultado = self.verificar_licencia_debug(archivo_licencia)
            print(f"=== RESULTADO: {resultado} ===")
            
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
    
    def obtener_info_licencia(self):
        """Obtiene información de la licencia actual"""
        try:
            if self.tipo_licencia == "premium" and os.path.exists(self.licencia_path):
                with open(self.licencia_path, 'r', encoding='utf-8') as f:
                    licencia_data = json.load(f)
                
                fecha_activacion = datetime.fromisoformat(licencia_data['fecha_activacion'])
                fecha_expiracion = fecha_activacion + timedelta(days=licencia_data['duracion_dias'])
                dias_restantes = (fecha_expiracion - datetime.now()).days
                
                return {
                    'tipo': 'premium',
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
                    'estado': estado,
                    'dias_restantes': ventas_restantes,
                    'expiracion': 'N/A',
                    'codigo': 'DEMO',
                    'mensaje': f'Ventas restantes: {ventas_restantes}/{self.limite_ventas_demo}',
                    'seguridad': 'básica'
                }
                
        except Exception as e:
            print(f"❌ Error obteniendo info licencia: {e}")
            return {
                'tipo': 'error',
                'estado': 'error',
                'dias_restantes': 0,
                'expiracion': 'N/A',
                'codigo': 'ERROR',
                'mensaje': f'Error: {str(e)}'
            }
    
    def verificar_licencia_debug(self, archivo_licencia):
        """Método temporal para debugging"""
        try:
            print(f"🔍 DEBUG: Verificando licencia {archivo_licencia}")
            
            if not os.path.exists(archivo_licencia):
                print("❌ Archivo no existe")
                return False
                
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia_data = json.load(f)
                
            print("📄 Contenido de la licencia:")
            for key, value in licencia_data.items():
                if key in ['hash_seguro', 'datos_encriptados', 'checksum']:
                    print(f"   {key}: {value[:50]}...")
                else:
                    print(f"   {key}: {value}")
                    
            return self._validar_licencia_generador(licencia_data)
            
        except Exception as e:
            print(f"❌ Error en debug: {e}")
            return False
    
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

    # Agrega esto temporalmente a licencias_manager.py
    def diagnosticar_equipo_id_completo(self):
        """Diagnóstico completo del equipo_id en ambas plataformas"""
        print("\n" + "="*60)
        print("🔍 DIAGNÓSTICO COMPLETO EQUIPO_ID")
        print("="*60)
        
        import socket
        import platform
        import subprocess
        
        # 1. Hostname
        hostname = socket.gethostname()
        print(f"📟 Hostname: {hostname}")
        
        # 2. MAC Address
        mac_address = uuid.getnode()
        print(f"📟 MAC (decimal): {mac_address}")
        mac = ':'.join(['{:02x}'.format((mac_address >> elements) & 0xff) 
                    for elements in range(0,2*6,2)][::-1])
        print(f"📟 MAC (formateada): {mac}")
        
        # 3. Sistema Operativo
        sistema = platform.system()
        version = platform.release()
        print(f"💻 Sistema: {sistema} {version}")
        
        # 4. Identificador específico de plataforma
        platform_id = ""
        if sistema == "Windows":
            try:
                result = subprocess.check_output('wmic csproduct get uuid', shell=True, text=True, stderr=subprocess.DEVNULL)
                lines = [line.strip() for line in result.split('\n') if line.strip()]
                if len(lines) > 1:
                    platform_id = lines[1]
                    print(f"🔑 Windows UUID: {platform_id}")
                else:
                    platform_id = "windows_no_uuid"
                    print("❌ No se pudo obtener UUID Windows")
            except Exception as e:
                platform_id = f"windows_error_{str(e)[:20]}"
                print(f"❌ Error UUID Windows: {e}")
        else:
            try:
                with open('/etc/machine-id', 'r') as f:
                    platform_id = f.read().strip()
                print(f"🔑 Linux Machine ID: {platform_id}")
            except Exception as e:
                platform_id = f"linux_error_{str(e)[:20]}"
                print(f"❌ Error Machine ID: {e}")
        
        # 5. Base para el ID
        id_base = f"{hostname}_{mac}_{sistema}_{platform_id}"
        print(f"📄 Base para ID: {id_base}")
        
        # 6. Hash final
        hash_completo = hashlib.sha3_512(id_base.encode()).hexdigest()
        equipo_id = hash_completo[:32]
        print(f"🔒 Hash completo: {hash_completo}")
        print(f"🎯 Equipo ID (truncado): {equipo_id}")
        print(f"📏 Longitud: {len(equipo_id)} caracteres")
        
        print("="*60)
        return equipo_id

# Metodo temporal para pruebas 
def probar_equipo_id():
    """Prueba que el equipo_id sea estable"""
    manager = LicenseManager()
    print(f"🔍 ID del equipo actual: {manager.equipo_id}")
        
    # Generar otro ID para comparar
    otro_id = manager._generar_id_equipo()
    print(f"🔍 Segundo ID generado: {otro_id}")
    print(f"✅ ¿Coinciden? {manager.equipo_id == otro_id}")

if __name__ == "__main__":
    probar_equipo_id()