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
        """Deriva una clave segura usando PBKDF2"""
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
        datos_ordenados = {k: datos[k] for k in sorted(datos.keys())}
        cadena = ''.join(str(v) for v in datos_ordenados.values())
        return hmac.new(self.master_key, cadena.encode(), hashlib.sha512).hexdigest()
    
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
        self.planes = {
            "perpetua": {"duracion": 36500, "precio": 2800, "nombre": "Licencia Perpetua"},
            "anual": {"duracion": 365, "precio": 1500, "nombre": "Suscripción Anual"}, 
            "empresarial": {"duracion": 36500, "precio": 6000, "nombre": "Plan Empresarial"}
        }

    def generar_licencia_avanzada(self, codigo_licencia, duracion_dias=30, id_cliente="", tipo="premium", equipo_id=None):
        """Genera una licencia válida con seguridad avanzada"""
        try:
            # Usar equipo_id proporcionado o generar uno local
            if equipo_id is None:
                equipo_id = self.generar_id_instalacion_unico()
            
            licencia = {
                "codigo": codigo_licencia,
                "fecha_activacion": datetime.now().isoformat(),
                "duracion_dias": duracion_dias,
                "id_cliente": id_cliente or f"CLI_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "tipo": tipo,
                "version": "2.1",
                "fecha_generacion": datetime.now().isoformat(),
                "equipo_id": equipo_id
            }
            
            # 🔐 CAPA 1: Hash HMAC-SHA512
            licencia["hash_seguro"] = self.security.generar_hash_seguro(licencia)
            
            # 🔐 CAPA 2: Datos sensibles encriptados
            datos_sensibles = {
                'codigo': licencia['codigo'],
                'id_cliente': licencia['id_cliente'],
                'fecha_activacion': licencia['fecha_activacion'],
                'equipo_id': licencia['equipo_id']
            }
            licencia["datos_encriptados"] = self.security.encriptar_datos(datos_sensibles)
            
            # 🔐 CAPA 3: Checksum de integridad
            licencia["checksum"] = self.generar_checksum_integridad(licencia)
            
            print(f"✅ Licencia generada para: {id_cliente}")
            print(f"🖥️  Equipo: {equipo_id}")
            print(f"📅 Duración: {duracion_dias} días")
            return licencia
            
        except Exception as e:
            print(f"❌ Error generando licencia: {e}")
            return None
    
    def generar_id_instalacion_unico(self):
        """Genera ID único COMPATIBLE con el validador"""
        try:
            import socket
            import platform
            
            # BASE COMPATIBLE Y ESTABLE
            hostname = socket.gethostname().lower().strip()
            sistema = platform.system().lower()
            arquitectura = platform.machine().lower()
            
            id_base = f"{hostname}_{sistema}_{arquitectura}"
            return hashlib.sha3_512(id_base.encode()).hexdigest()[:32]
            
        except Exception as e:
            print(f"❌ Error generando ID: {e}")
            import socket
            fallback_base = f"fallback_{socket.gethostname()}"
            return hashlib.sha3_512(fallback_base.encode()).hexdigest()[:32]
    
    def generar_checksum_integridad(self, licencia):
        """Genera checksum para verificar integridad"""
        datos_integridad = {
            'codigo': licencia['codigo'],
            'hash_seguro': licencia['hash_seguro'],
            'fecha_generacion': licencia['fecha_generacion'],
            'version': licencia.get('version', '2.0')
        }
        datos_ordenados = {k: datos_integridad[k] for k in sorted(datos_integridad.keys())}
        cadena = ''.join(str(v) for v in datos_ordenados.values())
        return hashlib.sha3_512(cadena.encode()).hexdigest()
        
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
            
            with open(archivo_salida, 'w', encoding='utf-8') as f:
                json.dump(licencia, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Licencia guardada en: {archivo_salida}")
            return True
            
        except Exception as e:
            print(f"❌ Error guardando licencia: {e}")
            return False
    
    def generar_licencia_plan(self, codigo, plan, id_cliente="", equipo_id=None):
        """Genera licencia según el plan contratado"""
        if plan not in self.planes:
            print(f"❌ Plan no válido: {plan}")
            return None, None
        
        config = self.planes[plan]
        print(f"🎯 Generando {config['nombre']} - ${config['precio']} MXN")
        
        licencia = self.generar_licencia_avanzada(
            codigo, config['duracion'], id_cliente, plan, equipo_id
        )
        
        if not licencia:
            return None, None
        
        archivo_salida = f"licencia_{plan}_{id_cliente}_{datetime.now().strftime('%Y%m%d')}.json"
        
        if self.guardar_licencia(licencia, archivo_salida):
            return licencia, archivo_salida
        else:
            return licencia, None
    
    def generar_licencia_personalizada(self, codigo, duracion_dias, id_cliente="", equipo_id=None):
        """Genera licencia con duración personalizada"""
        licencia = self.generar_licencia_avanzada(
            codigo, duracion_dias, id_cliente, "personalizada", equipo_id
        )
        
        if not licencia:
            return None, None
        
        archivo_salida = f"licencia_personalizada_{id_cliente}.json"
        
        if self.guardar_licencia(licencia, archivo_salida):
            return licencia, archivo_salida
        else:
            return licencia, None
    
    def mostrar_info_licencia(self, licencia):
        """Muestra información detallada de la licencia"""
        if not licencia:
            print("❌ Licencia inválida")
            return
        
        fecha_activacion = datetime.fromisoformat(licencia['fecha_activacion'])
        fecha_expiracion = fecha_activacion + timedelta(days=licencia['duracion_dias'])
        dias_restantes = (fecha_expiracion - datetime.now()).days
        
        print(f"\n📋 INFORMACIÓN DE LA LICENCIA")
        print("=" * 50)
        print(f"🔑 Código: {licencia['codigo']}")
        print(f"👤 Cliente: {licencia['id_cliente']}")
        print(f"📅 Fecha activación: {fecha_activacion.strftime('%d/%m/%Y %H:%M')}")
        print(f"⏰ Duración: {licencia['duracion_dias']} días")
        print(f"📅 Expira: {fecha_expiracion.strftime('%d/%m/%Y')}")
        print(f"📊 Días restantes: {dias_restantes}")
        print(f"🎯 Tipo: {licencia['tipo']}")
        print(f"🆔 Equipo: {licencia.get('equipo_id', 'N/A')[:16]}...")
    
    def validar_licencia_avanzada(self, archivo_licencia):
        """Valida manualmente una licencia existente"""
        try:
            if not os.path.exists(archivo_licencia):
                print("❌ Archivo de licencia no encontrado")
                return False
            
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia = json.load(f)
            
            # 1. Verificar checksum
            checksum_calculado = self.generar_checksum_integridad(licencia)
            if not hmac.compare_digest(licencia['checksum'], checksum_calculado):
                print("❌ Checksum inválido")
                return False
            
            # 2. Verificar hash
            datos_verificacion = {k: v for k, v in licencia.items() 
                                if k not in ['hash_seguro', 'datos_encriptados', 'checksum']}
            
            hash_calculado = self.security.generar_hash_seguro(datos_verificacion)
            if not hmac.compare_digest(licencia['hash_seguro'], hash_calculado):
                print("❌ Hash de seguridad inválido")
                return False
            
            # 3. Verificar datos encriptados
            try:
                datos_desencriptados = self.security.desencriptar_datos(licencia['datos_encriptados'])
                if (datos_desencriptados['codigo'] != licencia['codigo']):
                    print("❌ Datos encriptados no coinciden")
                    return False
            except Exception as e:
                print(f"❌ Error desencriptando: {e}")
                return False
            
            # 4. Verificar expiración
            fecha_activacion = datetime.fromisoformat(licencia['fecha_activacion'])
            fecha_expiracion = fecha_activacion + timedelta(days=licencia['duracion_dias'])
            
            if datetime.now() > fecha_expiracion:
                print("❌ Licencia expirada")
                return False
            else:
                dias_restantes = (fecha_expiracion - datetime.now()).days
                print(f"✅ Licencia válida - {dias_restantes} días restantes")
                return True
                
        except Exception as e:
            print(f"❌ Error validando licencia: {e}")
            return False

# FUNCIONES PRINCIPALES
def generar_licencia_rapida():
    """Función simple que genera y guarda licencia de prueba"""
    generador = GeneradorLicencias()
    
    codigo = "TEST-" + datetime.now().strftime("%H%M%S")
    id_cliente = "TEST"
    archivo = "licencia_test.json"
    
    print("⚡ GENERANDO LICENCIA DE PRUEBA...")
    
    licencia, archivo_guardado = generador.generar_licencia_personalizada(
        codigo, 7, id_cliente
    )
    
    if licencia and archivo_guardado:
        print(f"🎉 ¡ÉXITO! Licencia guardada en: {archivo_guardado}")
        generador.mostrar_info_licencia(licencia)
    else:
        print("❌ Error generando la licencia")

def menu_principal():
    """Menú principal del generador de licencias"""
    generador = GeneradorLicencias()
    
    while True:
        print("\n" + "="*60)
        print("🎫 GENERADOR DE LICENCIAS PROFESIONAL")
        print("="*60)
        print("1. 🏷️  Generar licencia por PLAN")
        print("2. ⚙️  Generar licencia PERSONALIZADA") 
        print("3. 🧪 Generar licencia de PRUEBA")
        print("4. 🔍 Validar licencia existente")
        print("5. 📊 Mostrar planes disponibles")
        print("6. 🚪 Salir")
        
        opcion = input("\nSeleccione opción: ").strip()
        
        if opcion == "1":
            print("\n" + "🏷️  GENERAR LICENCIA POR PLAN")
            print("-" * 30)
            print("Planes disponibles:")
            for plan_id, plan_info in generador.planes.items():
                print(f"   • {plan_id}: {plan_info['nombre']} - ${plan_info['precio']} MXN")
            
            plan = input("\nSeleccione plan (perpetua/anual/empresarial): ").strip().lower()
            if plan not in generador.planes:
                print("❌ Plan no válido")
                continue
                
            codigo = input("Código de licencia: ").strip() or f"{plan.upper()}-{datetime.now().strftime('%Y%m%d')}"
            id_cliente = input("Nombre del cliente: ").strip() or "Cliente"
            equipo_id = input("Equipo ID del cliente [auto]: ").strip() or None
            
            licencia, archivo = generador.generar_licencia_plan(codigo, plan, id_cliente, equipo_id)
            if licencia and archivo:
                print(f"✅ Licencia guardada en: {archivo}")
                generador.mostrar_info_licencia(licencia)
            else:
                print("❌ Error generando licencia")
                
        elif opcion == "2":
            print("\n" + "⚙️  LICENCIA PERSONALIZADA")
            codigo = input("Código: ").strip() or "CUSTOM-001"
            duracion = input("Días de duración: ").strip() or "30"
            id_cliente = input("Cliente: ").strip() or "ClientePersonalizado"
            equipo_id = input("Equipo ID [auto]: ").strip() or None
            
            try:
                licencia, archivo = generador.generar_licencia_personalizada(
                    codigo, int(duracion), id_cliente, equipo_id
                )
                if licencia and archivo:
                    print(f"✅ Licencia guardada en: {archivo}")
                    generador.mostrar_info_licencia(licencia)
                else:
                    print("❌ Error generando licencia")
            except ValueError:
                print("❌ Los días deben ser un número")
                
        elif opcion == "3":
            print("\n" + "🧪 GENERANDO LICENCIA DE PRUEBA...")
            generar_licencia_rapida()
            
        elif opcion == "4":
            archivo = input("Ruta del archivo de licencia: ").strip()
            if archivo:
                if os.path.exists(archivo):
                    generador.validar_licencia_avanzada(archivo)
                else:
                    print("❌ Archivo no encontrado")
                    
        elif opcion == "5":
            print("\n" + "📊 PLANES DISPONIBLES")
            print("-" * 40)
            for plan_id, plan_info in generador.planes.items():
                print(f"🎯 {plan_info['nombre']}:")
                print(f"   • Precio: ${plan_info['precio']} MXN")
                print(f"   • Duración: {plan_info['duracion']} días")
                print(f"   • ID: {plan_id}")
                print()
                
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    print("🔒 GENERADOR DE LICENCIAS - SISTEMA PROFESIONAL")
    print("💼 Planes: Perpetua ($2,800) | Anual ($1,500) | Empresarial ($6,000)")
    menu_principal()