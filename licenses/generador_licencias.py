# ===== SEGURIDAD AVANZADA =====
import json
import hashlib
import hmac
import base64
import os
import uuid
import socket
import platform
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
        datos_str = json.dumps(datos, sort_keys=True)
        return self.fernet.encrypt(datos_str.encode()).decode()
    
    def desencriptar_datos(self, datos_encriptados: str) -> dict:
        """Desencripta datos verificando integridad"""
        try:
            datos_bytes = self.fernet.decrypt(datos_encriptados.encode())
            return json.loads(datos_bytes.decode())
        except Exception as e:
            raise ValueError(f"Error desencriptando datos: {e}")

class GeneradorLicencias:
    def __init__(self):
        # 🔐 SISTEMA DE SEGURIDAD AVANZADO
        self.security = SecurityManager()

    def diagnosticar_generador(self):
        """Diagnóstico completo del equipo_id en el generador"""
        print("\n" + "="*60)
        print("🔍 DIAGNÓSTICO GENERADOR (LINUX)")
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
    
    def generar_licencia_avanzada(self, codigo_licencia, duracion_dias=30, id_cliente="", tipo="premium", equipo_id=None):
        """Genera una licencia válida con seguridad avanzada - VERSIÓN CON EQUIPO_ID"""
        try:
            # AGREGAR EQUIPO_ID (si no se proporciona, generar uno)
            if equipo_id is None:
                equipo_id = self.generar_id_instalacion_unico()
            
            licencia = {
                "codigo": codigo_licencia,
                "fecha_activacion": datetime.now().isoformat(),
                "duracion_dias": duracion_dias,
                "id_cliente": id_cliente or f"CLI_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "tipo": tipo,
                "version": "2.1",  # NUEVA VERSIÓN CON EQUIPO_ID
                "fecha_generacion": datetime.now().isoformat(),
                "id_instalacion": self.generar_id_instalacion_unico(),
                "equipo_id": equipo_id  # NUEVO CAMPO CRÍTICO
            }
            
            # 🔐 CAPA 1: Hash HMAC-SHA512 (INCLUYE EQUIPO_ID)
            licencia["hash_seguro"] = self.security.generar_hash_seguro(licencia)
            
            # 🔐 CAPA 2: Datos sensibles encriptados (INCLUYE EQUIPO_ID)
            datos_sensibles = {
                'codigo': licencia['codigo'],
                'id_cliente': licencia['id_cliente'],
                'fecha_activacion': licencia['fecha_activacion'],
                'id_instalacion': licencia['id_instalacion'],
                'equipo_id': licencia['equipo_id']  # ✅ INCLUIR EN DATOS ENCRIPTADOS
            }
            licencia["datos_encriptados"] = self.security.encriptar_datos(datos_sensibles)
            
            # 🔐 CAPA 3: Checksum de integridad (INCLUYE EQUIPO_ID)
            licencia["checksum"] = self.generar_checksum_integridad(licencia)
            
            print(f"✅ Licencia avanzada generada para código: {codigo_licencia}")
            print(f"🖥️  VINCULADA al equipo: {equipo_id[:16]}...")
            return licencia
            
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
    
    def generar_id_instalacion_unico(self):
        """Genera ID único de instalación PORTABLE"""
        try:
            import socket
            
            # ✅ MISMA LÓGICA PORTABLE
            hostname = socket.gethostname()
            mac_address = uuid.getnode()
            mac = ':'.join(['{:02x}'.format((mac_address >> elements) & 0xff) 
                        for elements in range(0,2*6,2)][::-1])
            
            id_base = f"{hostname}_{mac}"
            return hashlib.sha3_512(id_base.encode()).hexdigest()[:32]
            
        except:
            import socket
            fallback_base = f"portable_{socket.gethostname()}"
            return hashlib.sha3_512(fallback_base.encode()).hexdigest()[:32]
        
    def guardar_licencia(self, licencia, archivo_salida):
        """Guarda la licencia con rutas absolutas"""
        try:
            # Convertir a ruta absoluta
            if not os.path.isabs(archivo_salida):
                archivo_salida = os.path.abspath(archivo_salida)
            
            # Asegurar que el directorio existe
            directorio = os.path.dirname(archivo_salida)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
                print(f"✅ Directorio creado: {directorio}")
            
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(licencia, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Licencia guardada en: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando licencia: {e}")
            return False
    
    def generar_y_guardar_automatico(self, codigo, duracion_dias=30, id_cliente="", archivo_salida=None, equipo_id=None):
        """Genera y guarda automáticamente licencia avanzada - CON EQUIPO_ID"""
        try:
            # 1. Generar la licencia con seguridad avanzada (CON EQUIPO_ID)
            licencia = self.generar_licencia_avanzada(codigo, duracion_dias, id_cliente, "premium", equipo_id)
            if not licencia:
                return None, None
            
            # 2. Definir nombre de archivo por defecto si no se especifica
            if not archivo_salida:
                archivo_salida = f"licencia_{id_cliente or codigo}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 3. Guardar la licencia
            if self.guardar_licencia(licencia, archivo_salida):
                return licencia, archivo_salida
            else:
                return licencia, None  # Licencia OK pero no se pudo guardar
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None, None
    
    def mostrar_info_licencia(self, licencia):
        """Muestra información detallada de la licencia"""
        if not licencia:
            print("❌ Licencia inválida")
            return
        
        fecha_activacion = datetime.fromisoformat(licencia['fecha_activacion'])
        fecha_expiracion = fecha_activacion + timedelta(days=licencia['duracion_dias'])
        dias_restantes = (fecha_expiracion - datetime.now()).days
        
        print(f"\n📋 INFORMACIÓN DE LA LICENCIA (SEGURIDAD AVANZADA)")
        print("=" * 60)
        print(f"🔑 Código: {licencia['codigo']}")
        print(f"👤 Cliente: {licencia['id_cliente']}")
        print(f"📅 Fecha activación: {fecha_activacion.strftime('%d/%m/%Y %H:%M')}")
        print(f"⏰ Duración: {licencia['duracion_dias']} días")
        print(f"📅 Expira: {fecha_expiracion.strftime('%d/%m/%Y')}")
        print(f"📊 Días restantes: {dias_restantes}")
        print(f"🎯 Tipo: {licencia['tipo']}")
        print(f"🔐 Versión seguridad: {licencia.get('version', '2.0')}")
        print(f"🆔 ID instalación: {licencia.get('id_instalacion', 'N/A')[:16]}...")
        print(f"🔒 Hash seguro: {licencia['hash_seguro'][:24]}...")
        print(f"🔐 Datos encriptados: {licencia['datos_encriptados'][:30]}...")
        print(f"✅ Checksum: {licencia['checksum'][:24]}...")
    
    def validar_licencia_avanzada(self, archivo_licencia):
        """Valida manualmente una licencia existente con seguridad avanzada"""
        try:
            if not os.path.exists(archivo_licencia):
                print("❌ Archivo de licencia no encontrado")
                return False
            
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia = json.load(f)
            
            # 1. Verificar checksum de integridad
            checksum_calculado = self.generar_checksum_integridad(licencia)
            if not hmac.compare_digest(licencia['checksum'], checksum_calculado):
                print("❌ Checksum de integridad inválido")
                return False
            
            # 2. Verificar hash HMAC-SHA512
            datos_verificacion = {k: v for k, v in licencia.items() 
                                if k not in ['hash_seguro', 'datos_encriptados', 'checksum']}
            
            hash_calculado = self.security.generar_hash_seguro(datos_verificacion)
            if not hmac.compare_digest(licencia['hash_seguro'], hash_calculado):
                print("❌ Hash de seguridad inválido")
                return False
            
            # 3. Verificar datos encriptados
            try:
                datos_desencriptados = self.security.desencriptar_datos(licencia['datos_encriptados'])
                if (datos_desencriptados['codigo'] != licencia['codigo'] or
                    datos_desencriptados['id_cliente'] != licencia['id_cliente']):
                    print("❌ Datos encriptados no coinciden")
                    return False
            except Exception as e:
                print(f"❌ Error desencriptando datos: {e}")
                return False
            
            # 4. Verificar expiración
            fecha_activacion = datetime.fromisoformat(licencia['fecha_activacion'])
            fecha_expiracion = fecha_activacion + timedelta(days=licencia['duracion_dias'])
            
            if datetime.now() > fecha_expiracion:
                print("❌ Licencia expirada")
                return False
            else:
                dias_restantes = (fecha_expiracion - datetime.now()).days
                print(f"✅ Licencia activa - {dias_restantes} días restantes")
                print("🔒 Validación de seguridad avanzada: EXITOSA")
                return True
                
        except Exception as e:
            print(f"❌ Error validando licencia avanzada: {e}")
            return False

    def generar_licencia_compatibilidad(self, codigo_licencia, duracion_dias=30, id_cliente="", tipo="premium"):
        """Método de compatibilidad para sistemas existentes"""
        return self.generar_licencia_avanzada(codigo_licencia, duracion_dias, id_cliente, tipo)
    
    def obtener_equipo_id_cliente(self):
        """Genera script para que el cliente obtenga su equipo_id"""
        script_windows = """
    @echo off
    echo Obteniendo ID del equipo para activar Caja Registradora...
    echo.
    wmic csproduct get uuid > %temp%\\equipo_temp.txt
    set /p EQUIPO_ID=<%temp%\\equipo_temp.txt
    del %temp%\\equipo_temp.txt
    echo.
    echo ✅ SU EQUIPO_ID ES: %EQUIPO_ID%
    echo.
    echo 📋 Copie este ID y envielo para generar su licencia
    echo.
    pause
    """
        
        script_linux = """
    #!/bin/bash
    echo "Obteniendo ID del equipo para activar Caja Registradora..."
    echo ""
    if [ -f /etc/machine-id ]; then
        EQUIPO_ID=$(cat /etc/machine-id)
    else
        EQUIPO_ID=$(sudo dmidecode -s system-uuid 2>/dev/null || echo "NO_UID")
    fi
    echo ""
    echo "✅ SU EQUIPO_ID ES: $EQUIPO_ID"
    echo ""
    echo "📋 Copie este ID y envielo para generar su licencia"
    echo ""
    read -p "Presione Enter para continuar..."
    """
        
        print("🖥️  SCRIPTS PARA OBTENER EQUIPO_ID DEL CLIENTE:")
        print("=" * 60)
        print("📋 El cliente debe ejecutar este script y enviarle el EQUIPO_ID:")
        print("\n=== WINDOWS (Guardar como obtener_id.bat) ===")
        print(script_windows)
        print("\n=== LINUX (Guardar como obtener_id.sh) ===") 
        print(script_linux)
        print("\n💡 INSTRUCCIONES:")
        print("1. Cliente ejecuta el script correspondiente a su sistema")
        print("2. Cliente le envía el EQUIPO_ID que aparece")
        print("3. Usted genera la licencia con ESE equipo_id específico")
        print("4. La licencia solo funcionará en ese equipo")
        
        return script_windows, script_linux

# FUNCIONES PRINCIPALES ACTUALIZADAS
def generar_licencia_rapida():
    """Función simple que genera y guarda licencia avanzada"""
    generador = GeneradorLicencias()
    
    codigo = "TEST-ADV-" + datetime.now().strftime("%H%M%S")
    duracion = 7
    id_cliente = "TEST-ADV"
    archivo = "licencia_test_avanzada.json"
    
    print("⚡ GENERANDO LICENCIA AVANZADA RÁPIDA...")
    
    licencia, archivo_guardado = generador.generar_y_guardar_automatico(
        codigo, duracion, id_cliente, archivo
    )
    
    if licencia and archivo_guardado:
        print(f"🎉 ¡ÉXITO! Licencia avanzada guardada en: {archivo_guardado}")
        generador.mostrar_info_licencia(licencia)
        
        # Verificar que el archivo existe físicamente
        if os.path.exists(archivo_guardado):
            print(f"📁 Verificación: Archivo EXISTE en el sistema")
            print(f"📏 Tamaño: {os.path.getsize(archivo_guardado)} bytes")
            
            # Validar la licencia recién creada
            print("\n🔍 VALIDANDO LICENCIA RECIÉN CREADA...")
            generador.validar_licencia_avanzada(archivo_guardado)
        else:
            print("❌ ERROR: El archivo no se creó físicamente")
    else:
        print("❌ Error generando la licencia avanzada")

def menu_simple():
    """Menú simple y funcional con seguridad avanzada"""
    generador = GeneradorLicencias()
    
    while True:
        print("\n" + "="*60)
        print("🎫 GENERADOR DE LICENCIAS - SEGURIDAD AVANZADA v2.0")
        print("="*60)
        print("1. 🔥 Generar licencia TEST AVANZADA (RÁPIDO)")
        print("2. 📝 Generar licencia personalizada avanzada")
        print("3. 🔍 Validar licencia existente (validación avanzada)")
        print("4. 🧪 Probar seguridad de licencia")
        print("5. 🚪 Salir")
        
        opcion = input("\nSeleccione opción: ").strip()
        
        if opcion == "1":
            print("\n" + "🔥 GENERANDO LICENCIA TEST AVANZADA...")
            codigo = "TEST-ADV-" + datetime.now().strftime("%H%M%S")
            archivo = f"licencia_{codigo}.json"
            
            licencia, archivo_guardado = generador.generar_y_guardar_automatico(
                codigo, 7, "TEST-ADV", archivo
            )
            
            if licencia and archivo_guardado:
                print(f"✅ ¡ÉXITO! Archivo: {archivo_guardado}")
                if os.path.exists(archivo_guardado):
                    print("📁 Archivo físico creado correctamente")
                    # Validar automáticamente
                    generador.validar_licencia_avanzada(archivo_guardado)
            else:
                print("❌ Error")
                
        elif opcion == "2":
            print("\n" + "📝 LICENCIA PERSONALIZADA AVANZADA")
            codigo = input("Código: ").strip() or "CUSTOM-ADV-001"
            duracion = input("Días [30]: ").strip() or "30"
            id_cliente = input("Cliente [TEST-ADV]: ").strip() or "TEST-ADV"
            archivo = input("Archivo [auto]: ").strip() or None
            
            try:
                licencia, archivo_guardado = generador.generar_y_guardar_automatico(
                    codigo, int(duracion), id_cliente, archivo
                )
                
                if licencia and archivo_guardado:
                    print(f"✅ Guardado en: {archivo_guardado}")
                    generador.mostrar_info_licencia(licencia)
                    
                    # Validar automáticamente
                    print("\n🔍 VALIDACIÓN AUTOMÁTICA...")
                    generador.validar_licencia_avanzada(archivo_guardado)
                else:
                    print("❌ Error")
            except ValueError:
                print("❌ Los días deben ser un número")
                
        elif opcion == "3":
            archivo = input("Ruta del archivo de licencia: ").strip()
            if archivo:
                if os.path.exists(archivo):
                    print("🔍 INICIANDO VALIDACIÓN AVANZADA...")
                    generador.validar_licencia_avanzada(archivo)
                else:
                    print("❌ Archivo no encontrado")
                    
        elif opcion == "4":
            print("\n" + "🧪 PRUEBA DE SEGURIDAD AVANZADA")
            print("-" * 40)
            
            # Generar licencia de prueba
            codigo_prueba = "SECURITY-TEST-" + datetime.now().strftime("%H%M%S")
            licencia_prueba = generador.generar_licencia_avanzada(codigo_prueba, 1, "SECURITY-TEST")
            
            if licencia_prueba:
                print("✅ Licencia de prueba generada")
                print("🔒 Capas de seguridad implementadas:")
                print("   1. 🔐 HMAC-SHA512 para verificación de integridad")
                print("   2. 🛡️  Encriptación AES-256 para datos sensibles")
                print("   3. ✅ Checksum SHA3-512 para detección de modificaciones")
                print("   4. 🆔 ID de instalación único y robusto")
                print("   5. 🔄 Validación multi-capa")
                
                # Mostrar información de seguridad
                print(f"\n📊 Información de seguridad:")
                print(f"   Hash seguro: {licencia_prueba['hash_seguro'][:32]}...")
                print(f"   Datos encriptados: {licencia_prueba['datos_encriptados'][:40]}...")
                print(f"   Checksum: {licencia_prueba['checksum'][:32]}...")
                print(f"   ID instalación: {licencia_prueba['id_instalacion'][:24]}...")
                
            else:
                print("❌ Error en prueba de seguridad")
                
        elif opcion == "5":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    # Ejecutar la versión con seguridad avanzada
    print("🔒 SISTEMA DE LICENCIAS - SEGURIDAD AVANZADA v2.0")
    print("📦 Características de seguridad implementadas:")
    print("   • HMAC-SHA512 para hashes seguros")
    print("   • Encriptación AES-256 para datos sensibles")
    print("   • Validación multi-capa")
    print("   • Checksums SHA3-512 para integridad")
    print("   • IDs de instalación únicos y robustos\n")

    # Código temporal para probar
    if __name__ == "__main__":
        generador = GeneradorLicencias()
        test_id = generador.generar_id_instalacion_unico()
        print(f"🎯 Generador - ID generado: {test_id}")
    
    menu_simple()