import json
import hashlib
import os
from datetime import datetime, timedelta

class GeneradorLicencias:
    def __init__(self):
        # 🔐 CLAVE MAESTRA - ¡MANTÉN ESTA SEGURA Y NO LA COMPARTAS!
        self.clave_secreta = "CAJA_REGISTRADORA_PRO_2024_SECRET_KEY_¡NO_COMPARTIR!"
    
    def generar_licencia(self, codigo_licencia, duracion_dias=30, id_cliente="", tipo="premium"):
        """Genera una licencia válida para un cliente"""
        try:
            licencia = {
                "codigo": codigo_licencia,
                "fecha_activacion": datetime.now().isoformat(),
                "duracion_dias": duracion_dias,
                "id_cliente": id_cliente or f"CLI_{datetime.now().strftime('%Y%m%d%H%M')}",
                "tipo": tipo,
                "version": "1.0",
                "fecha_generacion": datetime.now().isoformat()
            }
            
            # Generar hash de seguridad
            datos_hash = {
                'codigo': licencia['codigo'],
                'fecha_activacion': licencia['fecha_activacion'],
                'duracion_dias': licencia['duracion_dias'],
                'id_cliente': licencia['id_cliente'],
                'tipo': licencia['tipo']
            }
            
            cadena_hash = ''.join(str(v) for v in datos_hash.values()) + self.clave_secreta
            licencia["hash"] = hashlib.sha256(cadena_hash.encode()).hexdigest()
            
            print(f"✅ Licencia generada para código: {codigo_licencia}")
            return licencia
            
        except Exception as e:
            print(f"❌ Error generando licencia: {e}")
            return None
    
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
    
    def generar_y_guardar_automatico(self, codigo, duracion_dias=30, id_cliente="", archivo_salida=None):
        """Genera y guarda automáticamente - ESTE SÍ FUNCIONA"""
        try:
            # 1. Generar la licencia
            licencia = self.generar_licencia(codigo, duracion_dias, id_cliente)
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
        
        print(f"\n📋 INFORMACIÓN DE LA LICENCIA")
        print("=" * 50)
        print(f"🔑 Código: {licencia['codigo']}")
        print(f"👤 Cliente: {licencia['id_cliente']}")
        print(f"📅 Fecha activación: {fecha_activacion.strftime('%d/%m/%Y %H:%M')}")
        print(f"⏰ Duración: {licencia['duracion_dias']} días")
        print(f"📅 Expira: {fecha_expiracion.strftime('%d/%m/%Y')}")
        print(f"📊 Días restantes: {dias_restantes}")
        print(f"🎯 Tipo: {licencia['tipo']}")
        print(f"🔐 Hash: {licencia['hash'][:16]}...")
    
    def validar_licencia_manual(self, archivo_licencia):
        """Valida manualmente una licencia existente"""
        try:
            if not os.path.exists(archivo_licencia):
                print("❌ Archivo de licencia no encontrado")
                return False
            
            with open(archivo_licencia, 'r', encoding='utf-8') as f:
                licencia = json.load(f)
            
            # Verificar hash
            datos_hash = {
                'codigo': licencia['codigo'],
                'fecha_activacion': licencia['fecha_activacion'],
                'duracion_dias': licencia['duracion_dias'],
                'id_cliente': licencia['id_cliente'],
                'tipo': licencia['tipo']
            }
            
            cadena_hash = ''.join(str(v) for v in datos_hash.values()) + self.clave_secreta
            hash_calculado = hashlib.sha256(cadena_hash.encode()).hexdigest()
            
            if licencia['hash'] == hash_calculado:
                print("✅ Licencia válida - Hash correcto")
                
                # Verificar expiración
                fecha_activacion = datetime.fromisoformat(licencia['fecha_activacion'])
                fecha_expiracion = fecha_activacion + timedelta(days=licencia['duracion_dias'])
                
                if datetime.now() > fecha_expiracion:
                    print("❌ Licencia expirada")
                    return False
                else:
                    dias_restantes = (fecha_expiracion - datetime.now()).days
                    print(f"✅ Licencia activa - {dias_restantes} días restantes")
                    return True
            else:
                print("❌ Licencia inválida - Hash incorrecto")
                return False
                
        except Exception as e:
            print(f"❌ Error validando licencia: {e}")
            return False

# FUNCIONES PRINCIPALES SIMPLIFICADAS
def generar_licencia_rapida():
    """Función simple que SÍ genera y guarda"""
    generador = GeneradorLicencias()
    
    codigo = "TEST-001"
    duracion = 7
    id_cliente = "TEST"
    archivo = "licencia_test.json"
    
    print("⚡ GENERANDO LICENCIA RÁPIDA...")
    
    # Usar el método que SÍ funciona
    licencia, archivo_guardado = generador.generar_y_guardar_automatico(
        codigo, duracion, id_cliente, archivo
    )
    
    if licencia and archivo_guardado:
        print(f"🎉 ¡ÉXITO! Licencia guardada en: {archivo_guardado}")
        generador.mostrar_info_licencia(licencia)
        
        # Verificar que el archivo existe físicamente
        if os.path.exists(archivo_guardado):
            print(f"📁 Verificación: Archivo EXISTE en el sistema")
            print(f"📏 Tamaño: {os.path.getsize(archivo_guardado)} bytes")
        else:
            print("❌ ERROR: El archivo no se creó físicamente")
    else:
        print("❌ Error generando la licencia")

def menu_simple():
    """Menú simple y funcional"""
    generador = GeneradorLicencias()
    
    while True:
        print("\n" + "="*50)
        print("🎫 GENERADOR DE LICENCIAS - VERSIÓN SIMPLE")
        print("="*50)
        print("1. 🔥 Generar licencia TEST (RÁPIDO)")
        print("2. 📝 Generar licencia personalizada")
        print("3. 🔍 Validar licencia existente")
        print("4. 🚪 Salir")
        
        opcion = input("\nSeleccione opción: ").strip()
        
        if opcion == "1":
            print("\n" + "🔥 GENERANDO LICENCIA TEST...")
            codigo = "TEST-" + datetime.now().strftime("%H%M%S")
            archivo = f"licencia_{codigo}.json"
            
            licencia, archivo_guardado = generador.generar_y_guardar_automatico(
                codigo, 7, "TEST", archivo
            )
            
            if licencia and archivo_guardado:
                print(f"✅ ¡ÉXITO! Archivo: {archivo_guardado}")
                if os.path.exists(archivo_guardado):
                    print("📁 Archivo físico creado correctamente")
            else:
                print("❌ Error")
                
        elif opcion == "2":
            print("\n" + "📝 LICENCIA PERSONALIZADA")
            codigo = input("Código: ").strip() or "CUSTOM-001"
            duracion = input("Días [30]: ").strip() or "30"
            id_cliente = input("Cliente [TEST]: ").strip() or "TEST"
            archivo = input("Archivo [auto]: ").strip() or None
            
            try:
                licencia, archivo_guardado = generador.generar_y_guardar_automatico(
                    codigo, int(duracion), id_cliente, archivo
                )
                
                if licencia and archivo_guardado:
                    print(f"✅ Guardado en: {archivo_guardado}")
                    generador.mostrar_info_licencia(licencia)
                else:
                    print("❌ Error")
            except ValueError:
                print("❌ Los días deben ser un número")
                
        elif opcion == "3":
            archivo = input("Ruta del archivo: ").strip()
            if archivo:
                generador.validar_licencia_manual(archivo)
                
        elif opcion == "4":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    # Ejecutar la versión simple y funcional
    menu_simple()