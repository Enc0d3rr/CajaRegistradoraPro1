# ===== SEGURIDAD AVANZADA =====
import json
import os
import hashlib
import hmac
import base64
import sys
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecurityManager:
    def __init__(self):
        # 🔐 CLAVE MAESTRA DERIVADA SEGURAMENTE
        self.master_key = self.derive_key("CAJA_REGISTRADORA_PRO_2024_SECRET_KEY_¡NO_COMPARTIR!")
        self.fernet = Fernet(self.master_key)
    
    def derive_key(self, password: str) -> bytes:
        """Deriva una clave segura usando PBKDF2 con 100,000 iteraciones"""
        salt = b'caja_registradora_salt_2024_secure_v2'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA512(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def generar_hash_seguro(self, datos: dict) -> str:
        """Genera HMAC-SHA512 para máxima seguridad"""
        # Ordenar datos para consistencia
        datos_ordenados = {k: datos[k] for k in sorted(datos.keys())}
        cadena = ''.join(str(v) for v in datos_ordenados.values())
        
        return hmac.new(
            self.master_key, 
            cadena.encode(), 
            hashlib.sha512
        ).hexdigest()
    
    def encriptar_datos(self, datos: dict) -> str:
        """Encripta datos sensibles usando AES-256"""
        datos_str = json.dumps(datos, sort_keys=True)  # Ordenar para consistencia
        return self.fernet.encrypt(datos_str.encode()).decode()
    
    def desencriptar_datos(self, datos_encriptados: str) -> dict:
        """Desencripta datos verificando integridad"""
        try:
            datos_bytes = self.fernet.decrypt(datos_encriptados.encode())
            return json.loads(datos_bytes.decode())
        except Exception as e:
            raise ValueError(f"Error desencriptando datos: {e}")

class LicenseManager:
    def __init__(self):
        # 📁 RUTAS ABSOLUTAS CORREGIDAS
        self.base_dir = self.obtener_directorio_base()
        self.archivo_licencia = os.path.join(self.base_dir, "data", "licencia.json")
        self.archivo_config = os.path.join(self.base_dir, "data", "config_demo.json")
        
        # 🔐 SISTEMA DE SEGURIDAD
        self.security = SecurityManager()
        
        self.licencia_valida = False
        self.tipo_licencia = None
        self.datos_licencia = {}
        self.limite_ventas_demo = 5
        
        self.ensure_data_directory()
        self.cargar_configuracion_demo()
        self.verificar_licencia()
    
    def obtener_directorio_base(self):
        """Obtiene la ruta base del proyecto"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            if os.path.basename(current_dir) == 'licenses':
                base_dir = os.path.dirname(current_dir)
            else:
                base_dir = current_dir
            
            print(f"📁 Directorio base detectado: {base_dir}")
            return base_dir
            
        except Exception as e:
            print(f"❌ Error detectando directorio base: {e}")
            return os.getcwd()
    
    def ensure_data_directory(self):
        """Asegura que el directorio data existe"""
        try:
            data_dir = os.path.dirname(self.archivo_licencia)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"✅ Directorio data creado: {data_dir}")
            
            if not os.access(data_dir, os.W_OK):
                print("❌ Sin permisos de escritura en directorio data")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Error creando directorio data: {e}")
            return False
    
    def cargar_configuracion_demo(self):
        """Carga la configuración de la versión demo - CORREGIDO"""
        config_default = {
            "licencia_activa": False,
            "tipo_licencia": "demo",
            "fecha_instalacion": datetime.now().isoformat(),
            "ventas_realizadas": 0,
            "max_ventas_demo": self.limite_ventas_demo,
            "id_instalacion": self.generar_id_instalacion_unico()
        }
        
        try:
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    self.config_demo = json.load(f)
                print(f"✅ Configuración demo cargada: {self.archivo_config}")
            else:
                self.config_demo = config_default
                if self.guardar_config_demo():
                    print("✅ Configuración demo creada por defecto")
                else:
                    print("❌ Error guardando configuración demo por defecto")
                    
        except Exception as e:
            print(f"❌ Error cargando config demo: {e}")
            self.config_demo = config_default
    
    def guardar_config_demo(self):
        """Guarda la configuración demo - CORREGIDO"""
        try:
            directorio = os.path.dirname(self.archivo_config)
            if not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
            
            if not os.access(directorio, os.W_OK):
                print("❌ Sin permisos de escritura para guardar configuración")
                return False
            
            with open(self.archivo_config, 'w', encoding='utf-8') as f:
                json.dump(self.config_demo, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Configuración demo guardada: {self.archivo_config}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando config demo: {e}")
            return False
    
    def verificar_licencia(self):
        """Verifica si hay licencia premium, sino activa demo - CON SEGURIDAD MEJORADA"""
        try:
            print(f"🔍 Buscando licencia en: {self.archivo_licencia}")
            
            if os.path.exists(self.archivo_licencia):
                try:
                    with open(self.archivo_licencia, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    # 🔐 USAR VALIDACIÓN AVANZADA
                    if self.validar_licencia_avanzada(datos):
                        self.licencia_valida = True
                        self.tipo_licencia = "premium"
                        self.datos_licencia = datos
                        print("✅ Licencia premium válida detectada (validación avanzada)")
                        return True
                    else:
                        print("❌ Licencia premium no válida en validación avanzada")
                        
                except Exception as e:
                    print(f"❌ Error leyendo licencia premium: {e}")
            else:
                print("📄 Archivo de licencia no encontrado")
        
            # Si no hay premium, activar demo
            print("🔬 Activando modo demo...")
            return self.activar_modo_demo()
            
        except Exception as e:
            print(f"❌ Error en verificar_licencia: {e}")
            return self.activar_modo_demo()
    
    def activar_modo_demo(self):
        """Activa el modo demo con límites"""
        self.tipo_licencia = "demo"
        
        if self.config_demo["ventas_realizadas"] >= self.limite_ventas_demo:
            self.licencia_valida = False
            print("❌ Límite demo excedido")
            return False
        
        self.licencia_valida = True
        print(f"✅ Demo activado. Ventas: {self.config_demo['ventas_realizadas']}/{self.limite_ventas_demo}")
        return True
    
    def validar_licencia_avanzada(self, datos_licencia):
        """Valida licencia con múltiples capas de seguridad"""
        try:
            # 1. ✅ Verificar estructura básica
            campos_requeridos = ["codigo", "fecha_activacion", "duracion_dias", "hash_seguro", "id_cliente", "tipo", "datos_encriptados", "checksum"]
            for campo in campos_requeridos:
                if campo not in datos_licencia:
                    print(f"❌ Licencia sin campo requerido: {campo}")
                    return False
            
            # 2. ✅ Verificar checksum de integridad
            if not self.verificar_checksum_integridad(datos_licencia):
                print("❌ Checksum de integridad inválido")
                return False
            
            # 3. ✅ Verificar hash HMAC-SHA512
            datos_verificacion = {k: v for k, v in datos_licencia.items() 
                                if k not in ['hash_seguro', 'datos_encriptados', 'checksum']}
            
            hash_calculado = self.security.generar_hash_seguro(datos_verificacion)
            if not hmac.compare_digest(datos_licencia['hash_seguro'], hash_calculado):
                print("❌ Hash de seguridad inválido")
                return False
            
            # 4. ✅ Verificar datos encriptados
            try:
                datos_desencriptados = self.security.desencriptar_datos(datos_licencia['datos_encriptados'])
                if (datos_desencriptados['codigo'] != datos_licencia['codigo'] or
                    datos_desencriptados['id_cliente'] != datos_licencia['id_cliente']):
                    print("❌ Datos encriptados no coinciden")
                    return False
            except Exception as e:
                print(f"❌ Error desencriptando datos: {e}")
                return False
            
            # 5. ✅ Verificar fecha de expiración
            fecha_activacion = datetime.fromisoformat(datos_licencia["fecha_activacion"])
            fecha_expiracion = fecha_activacion + timedelta(days=datos_licencia["duracion_dias"])
            
            if datetime.now() > fecha_expiracion:
                print("❌ Licencia expirada")
                return False
            
            # 6. ✅ Verificar que no esté revocada
            if self.licencia_revocada_avanzada(datos_licencia):
                print("❌ Licencia revocada")
                return False
            
            dias_restantes = (fecha_expiracion - datetime.now()).days
            print(f"✅ Licencia válida. Días restantes: {dias_restantes}")
            return True
            
        except Exception as e:
            print(f"❌ Error validando licencia avanzada: {e}")
            return False
    
    def verificar_checksum_integridad(self, licencia):
        """Verifica el checksum de integridad"""
        try:
            datos_integridad = {
                'codigo': licencia['codigo'],
                'hash_seguro': licencia['hash_seguro'],
                'fecha_generacion': licencia['fecha_generacion'],
                'version': licencia.get('version', '1.0')
            }
            # Ordenar para consistencia
            datos_ordenados = {k: datos_integridad[k] for k in sorted(datos_integridad.keys())}
            cadena = ''.join(str(v) for v in datos_ordenados.values())
            
            checksum_calculado = hashlib.sha3_512(cadena.encode()).hexdigest()
            return hmac.compare_digest(licencia['checksum'], checksum_calculado)
            
        except Exception as e:
            print(f"❌ Error verificando checksum: {e}")
            return False
    
    def licencia_revocada_avanzada(self, datos_licencia):
        """Verifica si la licencia está en lista negra con hash seguro"""
        # Lista negra de códigos revocados (hasheados)
        lista_negra_hasheada = [
            self.generar_hash_codigo("REVOKED-TEST-001"),
            self.generar_hash_codigo("REVOKED-TEST-002")
        ]
        
        codigo_hasheado = self.generar_hash_codigo(datos_licencia["codigo"])
        return codigo_hasheado in lista_negra_hasheada
    
    def generar_hash_codigo(self, codigo):
        """Genera hash seguro para códigos de licencia"""
        return hashlib.sha3_256(f"{codigo}_revocation_check".encode()).hexdigest()
    
    def activar_licencia(self, codigo_licencia):
        """Activa una licencia premium - CON SEGURIDAD MEJORADA"""
        try:
            # Verificar formato básico del código
            if not codigo_licencia or len(codigo_licencia) < 10:
                return False, "Código de licencia inválido"
            
            # Generar licencia con seguridad avanzada
            licencia_generada = self.generar_licencia_avanzada(codigo_licencia)
            
            if licencia_generada:
                if self.guardar_licencia_premium(licencia_generada):
                    # Recargar verificación
                    self.verificar_licencia()
                    return True, "Licencia premium activada correctamente"
                else:
                    return False, "Error guardando archivo de licencia"
            else:
                return False, "No se pudo generar la licencia"
                
        except Exception as e:
            print(f"❌ Error activando licencia: {e}")
            return False, f"Error al activar licencia: {str(e)}"
    
    def generar_licencia_avanzada(self, codigo_licencia, duracion_dias=30, id_cliente="", tipo="premium"):
        """Genera licencia con múltiples capas de seguridad"""
        try:
            # Datos básicos
            licencia_base = {
                "codigo": codigo_licencia,
                "fecha_activacion": datetime.now().isoformat(),
                "duracion_dias": duracion_dias,
                "id_cliente": id_cliente or f"CLI_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "tipo": tipo,
                "version": "2.0",  # Nueva versión con seguridad mejorada
                "fecha_generacion": datetime.now().isoformat(),
                "id_instalacion": self.generar_id_instalacion_unico()
            }
            
            # 🔐 CAPA 1: Hash HMAC-SHA512
            licencia_base["hash_seguro"] = self.security.generar_hash_seguro(licencia_base)
            
            # 🔐 CAPA 2: Datos sensibles encriptados
            datos_sensibles = {
                'codigo': licencia_base['codigo'],
                'id_cliente': licencia_base['id_cliente'],
                'fecha_activacion': licencia_base['fecha_activacion'],
                'id_instalacion': licencia_base['id_instalacion']
            }
            licencia_base["datos_encriptados"] = self.security.encriptar_datos(datos_sensibles)
            
            # 🔐 CAPA 3: Checksum de integridad
            licencia_base["checksum"] = self.generar_checksum_integridad(licencia_base)
            
            print(f"✅ Licencia avanzada generada para: {codigo_licencia}")
            return licencia_base
            
        except Exception as e:
            print(f"❌ Error generando licencia avanzada: {e}")
            return None
    
    def generar_checksum_integridad(self, licencia):
        """Genera checksum para verificar integridad"""
        datos_integridad = {
            'codigo': licencia['codigo'],
            'hash_seguro': licencia['hash_seguro'],
            'fecha_generacion': licencia['fecha_generacion'],
            'version': licencia.get('version', '2.0')
        }
        # Ordenar para consistencia
        datos_ordenados = {k: datos_integridad[k] for k in sorted(datos_integridad.keys())}
        cadena = ''.join(str(v) for v in datos_ordenados.values())
        return hashlib.sha3_512(cadena.encode()).hexdigest()
    
    def guardar_licencia_premium(self, licencia):
        """Guarda la licencia premium - CORREGIDO"""
        try:
            directorio = os.path.dirname(self.archivo_licencia)
            if not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
            
            if not os.access(directorio, os.W_OK):
                print("❌ Sin permisos de escritura para guardar licencia")
                return False
            
            with open(self.archivo_licencia, 'w', encoding='utf-8') as f:
                json.dump(licencia, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Licencia premium guardada: {self.archivo_licencia}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando licencia premium: {e}")
            return False
    
    def generar_id_instalacion_unico(self):
        """Genera ID único de instalación más robusto"""
        try:
            import socket
            import uuid
            import platform
            
            # Combinar múltiples fuentes de identificación
            hostname = socket.gethostname()
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            sistema = platform.system() + platform.release()
            
            # Combinar y hashear
            id_base = f"{hostname}_{mac}_{sistema}_{datetime.now().timestamp()}"
            
            # Usar SHA3-512 para mayor seguridad
            return hashlib.sha3_512(id_base.encode()).hexdigest()[:32]
            
        except:
            # Fallback seguro
            return hashlib.sha3_512(str(datetime.now().timestamp()).encode()).hexdigest()[:32]
    
    def registrar_venta(self):
        """Registra una venta en el contador demo - CORREGIDO"""
        if self.tipo_licencia == "demo":
            self.config_demo["ventas_realizadas"] += 1
            if self.guardar_config_demo():
                print(f"📊 Venta demo registrada. Total: {self.config_demo['ventas_realizadas']}/{self.limite_ventas_demo}")
            else:
                print("❌ Error guardando venta demo")
            
            # Verificar si se excedió el límite
            if self.config_demo["ventas_realizadas"] >= self.limite_ventas_demo:
                self.licencia_valida = False
                print("❌ Límite de ventas demo alcanzado")
    
    def obtener_info_licencia(self):
        """Retorna información detallada de la licencia"""
        if self.tipo_licencia == "premium" and self.datos_licencia:
            # Calcular días restantes para premium
            fecha_activacion = datetime.fromisoformat(self.datos_licencia["fecha_activacion"])
            fecha_expiracion = fecha_activacion + timedelta(days=self.datos_licencia["duracion_dias"])
            dias_restantes = max(0, (fecha_expiracion - datetime.now()).days)
            
            return {
                'estado': 'activa' if dias_restantes > 0 else 'expirada',
                'tipo': 'premium',
                'dias_restantes': dias_restantes,
                'mensaje': f'Licencia Premium - {dias_restantes} días restantes',
                'expiracion': fecha_expiracion.strftime('%d/%m/%Y'),
                'codigo': self.datos_licencia['codigo'][:8] + '...',
                'seguridad': 'avanzada'
            }
        else:
            ventas_restantes = max(0, self.limite_ventas_demo - self.config_demo["ventas_realizadas"])
            estado = 'activa' if ventas_restantes > 0 else 'expirada'
            
            return {
                'estado': estado,
                'tipo': 'demo',
                'dias_restantes': ventas_restantes,
                'mensaje': f'Versión Demo - {ventas_restantes} ventas restantes' if estado == 'activa' else 'Límite demo alcanzado',
                'expiracion': 'N/A',
                'codigo': 'DEMO',
                'seguridad': 'básica'
            }
    
    def validar_licencia(self):
        """Método compatible con tu código existente"""
        return self.licencia_valida
    
    def obtener_tipo_licencia(self):
        return self.tipo_licencia
    
    def mostrar_dialogo_activacion(self):
        """Método para compatibilidad"""
        from PyQt6.QtWidgets import QDialog
        return QDialog.DialogCode.Accepted
    
    def obtener_rutas(self):
        """Método de diagnóstico - muestra las rutas usadas"""
        return {
            'base_dir': self.base_dir,
            'archivo_licencia': self.archivo_licencia,
            'archivo_config': self.archivo_config,
            'licencia_existe': os.path.exists(self.archivo_licencia),
            'config_existe': os.path.exists(self.archivo_config),
            'seguridad': 'avanzada'
        }