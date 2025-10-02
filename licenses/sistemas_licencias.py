# ===== SEGURIDAD AVANZADA =====
import json
import os
import sys
import glob
from datetime import datetime, timedelta

# Agregar el path para importar generador_licencias
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from licenses.generador_licencias import GeneradorLicencias

class SistemaLicencias:
    def __init__(self):
        self.generador = GeneradorLicencias()
        
        self.base_dir = self.obtener_directorio_base()
        self.archivo_clientes = os.path.join(self.base_dir, "data", "clientes_licencias.json")
        self.directorio_licencias = os.path.join(self.base_dir, "licencias")
        
        print(f"🔍 Rutas configuradas (Seguridad Avanzada v2.0):")
        print(f"   Base: {self.base_dir}")
        print(f"   Clientes: {self.archivo_clientes}")
        print(f"   Licencias: {self.directorio_licencias}")
        print(f"   Seguridad: HMAC-SHA512 + AES-256 + SHA3-512")
        print(f"   🔒 NUEVO: Sistema de vinculación por equipo_id")
        
        self.cargar_clientes()
        self.ensure_directories()
    
    def obtener_directorio_base(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            if os.path.basename(current_dir) == 'licenses':
                base_dir = os.path.dirname(current_dir)
            else:
                base_dir = current_dir
            
            if not os.path.exists(base_dir):
                print(f"❌ Directorio base no existe: {base_dir}")
                base_dir = os.getcwd()
                print(f"✅ Usando directorio actual: {base_dir}")
            
            return base_dir
            
        except Exception as e:
            print(f"❌ Error detectando directorio base: {e}")
            return os.getcwd()
    
    def ensure_directories(self):
        try:
            if not os.path.exists(self.directorio_licencias):
                os.makedirs(self.directorio_licencias, exist_ok=True)
                print(f"✅ Directorio de licencias creado: {self.directorio_licencias}")
            else:
                print(f"✅ Directorio de licencias ya existe: {self.directorio_licencias}")
            
            data_dir = os.path.join(self.base_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"✅ Directorio data creado: {data_dir}")
            
            if not os.access(self.directorio_licencias, os.W_OK):
                print(f"❌ Sin permisos de escritura en: {self.directorio_licencias}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Error creando directorios: {e}")
            return False
    
    def cargar_clientes(self):
        try:
            if os.path.exists(self.archivo_clientes):
                with open(self.archivo_clientes, 'r', encoding='utf-8') as f:
                    self.clientes = json.load(f)
                print(f"✅ Clientes cargados: {len(self.clientes)} registros")
            else:
                self.clientes = []
                print("📁 Creando nueva base de datos de clientes")
        except Exception as e:
            print(f"❌ Error cargando clientes: {e}")
            self.clientes = []
    
    def guardar_clientes(self):
        try:
            with open(self.archivo_clientes, 'w', encoding='utf-8') as f:
                json.dump(self.clientes, f, indent=4, ensure_ascii=False)
            print("✅ Base de datos de clientes guardada")
        except Exception as e:
            print(f"❌ Error guardando clientes: {e}")
    
    def agregar_cliente(self, nombre, email, telefono, duracion_dias=30, equipo_id=None):
        """Agrega un nuevo cliente y genera su licencia VINCULADA al equipo_id"""
        try:
            id_cliente = f"CLI_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            codigo_licencia = f"CAJA-PRO-{id_cliente}"
            
            cliente = {
                "id": id_cliente,
                "nombre": nombre,
                "email": email,
                "telefono": telefono,
                "codigo_licencia": codigo_licencia,
                "fecha_registro": datetime.now().isoformat(),
                "duracion_dias": duracion_dias,
                "estado": "activo",
                "seguridad": "avanzada_v2.0",
                "equipo_id": equipo_id  # NUEVO: Guardar el equipo_id del cliente
            }
            
            # NUEVO: Generar licencia VINCULADA al equipo_id específico
            print(f"🔒 Generando licencia VINCULADA para equipo: {equipo_id}")
            licencia = self.generador.generar_licencia_avanzada(
                codigo_licencia, 
                duracion_dias, 
                id_cliente, 
                "premium", 
                equipo_id  # Pasar el equipo_id específico
            )
            
            if not licencia:
                return None, "Error generando licencia avanzada vinculada"
            
            archivo_licencia = os.path.join(
                self.directorio_licencias,
                f"{id_cliente}_licencia_avanzada.json"
            )
            
            print(f"📁 Guardando licencia avanzada VINCULADA en: {archivo_licencia}")
            
            if self.generador.guardar_licencia(licencia, archivo_licencia):
                self.clientes.append(cliente)
                self.guardar_clientes()
                
                print(f"✅ Cliente agregado: {nombre}")
                print(f"📄 Licencia avanzada VINCULADA guardada")
                print(f"🔒 Vinculada al equipo: {equipo_id}")
                print(f"🔐 Seguridad: HMAC-SHA512 + AES-256 + SHA3-512")
                return cliente, archivo_licencia
            else:
                return None, "Error guardando archivo de licencia"
            
        except Exception as e:
            print(f"❌ Error agregando cliente: {e}")
            return None, f"Error: {str(e)}"
    
    def listar_clientes(self):
        print(f"\n📋 LISTA DE CLIENTES ({len(self.clientes)} registros) - SEGURIDAD AVANZADA")
        print("=" * 120)
        
        if not self.clientes:
            print("   No hay clientes registrados")
            return
        
        for i, cliente in enumerate(self.clientes, 1):
            fecha_registro = datetime.fromisoformat(cliente['fecha_registro']).strftime('%d/%m/%Y')
            seguridad = cliente.get('seguridad', 'básica')
            equipo_id = cliente.get('equipo_id', 'No vinculado')
            
            print(f"{i:2d}. {cliente['nombre']:20} | {cliente['email']:25} | {cliente['codigo_licencia']:20} | "
                  f"Equipo: {equipo_id[:16]:16}... | Seg: {seguridad:15} | Reg: {fecha_registro}")
    
    def buscar_cliente(self, email):
        for cliente in self.clientes:
            if cliente['email'].lower() == email.lower():
                return cliente
        return None
    
    def buscar_cliente_por_indice(self, indice):
        try:
            indice = int(indice) - 1
            if 0 <= indice < len(self.clientes):
                return self.clientes[indice]
            else:
                return None
        except ValueError:
            return None
    
    def renovar_licencia(self, email, duracion_dias=30):
        """Renueva la licencia de un cliente manteniendo la vinculación al equipo"""
        try:
            cliente = self.buscar_cliente(email)
            if not cliente:
                return False, "Cliente no encontrado"
            
            equipo_id = cliente.get('equipo_id')
            if not equipo_id:
                return False, "Cliente no tiene equipo_id asignado. Use la opción de agregar cliente."
            
            print(f"🔄 Renovando licencia avanzada VINCULADA para: {cliente['nombre']}")
            print(f"🔒 Manteniendo vinculación al equipo: {equipo_id}")
            
            archivo_licencia = os.path.join(
                self.directorio_licencias,
                f"{cliente['id']}_licencia_avanzada_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            # NUEVO: Renovar manteniendo el mismo equipo_id
            nueva_licencia = self.generador.generar_licencia_avanzada(
                cliente['codigo_licencia'], 
                duracion_dias, 
                cliente['id'],
                "premium",
                equipo_id  # Mantener el mismo equipo_id
            )
            
            if not nueva_licencia:
                return False, "Error generando nueva licencia avanzada vinculada"
            
            if self.generador.guardar_licencia(nueva_licencia, archivo_licencia):
                print(f"✅ Licencia avanzada VINCULADA renovada correctamente")
                
                cliente['duracion_dias'] = duracion_dias
                cliente['fecha_renovacion'] = datetime.now().isoformat()
                cliente['seguridad'] = 'avanzada_v2.0'
                self.guardar_clientes()
                
                print("🔍 Validando licencia recién creada...")
                if self.generador.validar_licencia_avanzada(archivo_licencia):
                    print("✅ Licencia validada exitosamente")
                else:
                    print("⚠️ Licencia creada pero validación falló")
                
                return True, archivo_licencia
            else:
                return False, "Error guardando nueva licencia avanzada"
            
        except Exception as e:
            print(f"❌ Error renovando licencia: {e}")
            return False, f"Error: {str(e)}"

    def obtener_equipo_id_cliente(self):
        """NUEVO: Ayuda al vendedor a obtener el equipo_id del cliente"""
        print(f"\n🖥️  OBTENER EQUIPO_ID DEL CLIENTE")
        print("=" * 50)
        
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
        
        print("📋 INSTRUCCIONES PARA EL CLIENTE:")
        print("1. El cliente debe ejecutar el script correspondiente a su sistema")
        print("2. El cliente le envía el EQUIPO_ID que aparece")
        print("3. Usted genera la licencia con ESE equipo_id específico")
        print("4. La licencia solo funcionará en ese equipo específico")
        
        print("\n=== WINDOWS (Guardar como obtener_id.bat) ===")
        print(script_windows)
        print("\n=== LINUX (Guardar como obtener_id.sh) ===") 
        print(script_linux)
        
        return script_windows, script_linux

    # Los demás métodos permanecen iguales (eliminar_cliente, verificar_archivos_licencias, etc.)
    # Solo modifiqué agregar_cliente y renovar_licencia para incluir equipo_id

    def eliminar_cliente(self, email):
        try:
            cliente = self.buscar_cliente(email)
            if not cliente:
                return False, "Cliente no encontrado"
            
            print(f"🗑️  Eliminando cliente: {cliente['nombre']} ({cliente['email']})")
            
            archivos_eliminados = self.eliminar_archivos_cliente(cliente['id'])
            
            self.clientes = [c for c in self.clientes if c['email'].lower() != email.lower()]
            self.guardar_clientes()
            
            mensaje = f"✅ Cliente '{cliente['nombre']}' eliminado exitosamente"
            if archivos_eliminados > 0:
                mensaje += f"\n📄 Se eliminaron {archivos_eliminados} archivos de licencia"
            else:
                mensaje += "\nℹ️ No se encontraron archivos de licencia para eliminar"
            
            return True, mensaje
            
        except Exception as e:
            print(f"❌ Error eliminando cliente: {e}")
            return False, f"Error eliminando cliente: {str(e)}"
    
    def eliminar_archivos_cliente(self, id_cliente):
        try:
            patrones = [
                os.path.join(self.directorio_licencias, f"{id_cliente}_licencia*.json"),
                os.path.join(self.directorio_licencias, f"{id_cliente}_licencia_avanzada*.json")
            ]
            
            archivos_eliminados = 0
            for patron in patrones:
                archivos = glob.glob(patron)
                for archivo in archivos:
                    try:
                        os.remove(archivo)
                        print(f"   📄 Eliminado: {os.path.basename(archivo)}")
                        archivos_eliminados += 1
                    except Exception as e:
                        print(f"   ❌ Error eliminando {archivo}: {e}")
            
            return archivos_eliminados
            
        except Exception as e:
            print(f"❌ Error buscando archivos del cliente: {e}")
            return 0
    
    def verificar_archivos_licencias(self):
        print(f"\n🔍 VERIFICANDO ARCHIVOS DE LICENCIAS AVANZADAS EN: {self.directorio_licencias}")
        problemas = 0
        licencias_validadas = 0
        
        if not os.path.exists(self.directorio_licencias):
            print(f"❌ Directorio de licencias no existe: {self.directorio_licencias}")
            crear = input("   ¿Crear directorio? (s/n): ").strip().lower()
            if crear == 's':
                os.makedirs(self.directorio_licencias, exist_ok=True)
                print(f"✅ Directorio creado: {self.directorio_licencias}")
            else:
                return
        
        for cliente in self.clientes:
            patron = os.path.join(self.directorio_licencias, f"{cliente['id']}_licencia*.json")
            archivos = glob.glob(patron)
            
            if archivos:
                print(f"\n✅ {cliente['nombre']}: {len(archivos)} archivo(s)")
                for archivo in archivos:
                    print(f"   📄 {os.path.basename(archivo)}")
                    
                    print(f"   🔍 Validando seguridad avanzada...")
                    if self.generador.validar_licencia_avanzada(archivo):
                        print(f"   ✅ Licencia válida (seguridad avanzada)")
                        
                        # NUEVO: Mostrar información de vinculación
                        try:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                licencia_data = json.load(f)
                            if 'datos_encriptados' in licencia_data:
                                datos_desencriptados = self.generador.security.desencriptar_datos(
                                    licencia_data['datos_encriptados']
                                )
                                equipo_id_licencia = datos_desencriptados.get('equipo_id', 'No especificado')
                                print(f"   🔒 Vinculada a: {equipo_id_licencia[:16]}...")
                        except:
                            print(f"   ⚠️ No se pudo verificar vinculación")
                        
                        licencias_validadas += 1
                    else:
                        print(f"   ❌ Licencia inválida o corrupta")
                        problemas += 1
            else:
                print(f"❌ {cliente['nombre']}: SIN ARCHIVO DE LICENCIA")
                problemas += 1
                
                regenerar = input("   ¿Regenerar licencia avanzada? (s/n): ").strip().lower()
                if regenerar == 's':
                    resultado, archivo = self.renovar_licencia(cliente['email'], cliente['duracion_dias'])
                    if resultado:
                        print(f"   ✅ Licencia avanzada regenerada: {os.path.basename(archivo)}")
                    else:
                        print(f"   ❌ Error: {archivo}")
        
        print(f"\n📊 RESUMEN DE VERIFICACIÓN:")
        print(f"   ✅ Licencias validadas: {licencias_validadas}")
        print(f"   ❌ Problemas encontrados: {problemas}")
        
        if problemas == 0 and licencias_validadas > 0:
            print("🎉 ¡Todas las licencias están validadas y en orden!")
        else:
            print(f"⚠️ Se encontraron {problemas} problemas que requieren atención")

    def generar_reporte_seguridad(self):
        print(f"\n📊 REPORTE DE SEGURIDAD DEL SISTEMA")
        print("=" * 60)
        
        clientes_avanzados = sum(1 for c in self.clientes if c.get('seguridad', '').startswith('avanzada'))
        clientes_basicos = len(self.clientes) - clientes_avanzados
        
        clientes_vinculados = sum(1 for c in self.clientes if c.get('equipo_id'))
        clientes_no_vinculados = len(self.clientes) - clientes_vinculados
        
        print(f"👥 Clientes totales: {len(self.clientes)}")
        print(f"   🔒 Seguridad avanzada: {clientes_avanzados}")
        print(f"   🔓 Seguridad básica: {clientes_basicos}")
        print(f"   🔗 Vinculados a equipo: {clientes_vinculados}")
        print(f"   🔓 No vinculados: {clientes_no_vinculados}")
        
        total_archivos = 0
        archivos_avanzados = 0
        
        if os.path.exists(self.directorio_licencias):
            for archivo in glob.glob(os.path.join(self.directorio_licencias, "*.json")):
                total_archivos += 1
                try:
                    with open(archivo, 'r') as f:
                        licencia = json.load(f)
                    if licencia.get('version') == '2.0':
                        archivos_avanzados += 1
                except:
                    pass
        
        print(f"📄 Archivos de licencia: {total_archivos}")
        print(f"   🔒 Licencias avanzadas: {archivos_avanzados}")
        print(f"   🔓 Licencias básicas: {total_archivos - archivos_avanzados}")
        
        print(f"\n💡 RECOMENDACIONES DE SEGURIDAD:")
        if clientes_basicos > 0:
            print(f"   ⚠️  {clientes_basicos} clientes necesitan actualizar a seguridad avanzada")
        else:
            print(f"   ✅ Todos los clientes tienen seguridad avanzada")
            
        if clientes_no_vinculados > 0:
            print(f"   ⚠️  {clientes_no_vinculados} clientes no tienen vinculación por equipo")
        else:
            print(f"   ✅ Todos los clientes tienen licencias vinculadas")
            
        if total_archivos == 0:
            print(f"   ❌ No se encontraron archivos de licencia")
        elif archivos_avanzados < total_archivos:
            print(f"   ⚠️  {total_archivos - archivos_avanzados} licencias necesitan regenerarse con seguridad avanzada")

def menu_principal():
    sistema = SistemaLicencias()
    
    while True:
        print("\n🎫 SISTEMA DE GESTIÓN DE LICENCIAS - SEGURIDAD AVANZADA v2.0")
        print("=" * 70)
        print("1. 🏢 Agregar nuevo cliente (licencia VINCULADA)")
        print("2. 📋 Listar clientes")
        print("3. 🔄 Renovar licencia (mantener vinculación)")
        print("4. 🔍 Buscar cliente por email")
        print("5. 🗑️  Eliminar cliente")
        print("6. 🔎 Verificar archivos de licencias")
        print("7. 📊 Reporte de seguridad")
        print("8. 🆔 Obtener equipo_id del cliente")
        print("9. 🧪 Probar generador de licencias")
        print("10. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            print("\n➕ NUEVO CLIENTE (LICENCIA VINCULADA)")
            nombre = input("Nombre: ").strip()
            email = input("Email: ").strip()
            telefono = input("Teléfono: ").strip()
            duracion = input("Duración en días [30]: ").strip() or "30"
            
            # NUEVO: Solicitar equipo_id del cliente
            print("\n🔒 SISTEMA DE VINCULACIÓN POR EQUIPO")
            equipo_id = input("Equipo_ID del cliente (OBLIGATORIO): ").strip()
            
            if not equipo_id:
                print("❌ El equipo_id es OBLIGATORIO para licencias vinculadas")
                continuar = input("¿Continuar sin vinculación? (s/n): ").strip().lower()
                if continuar != 's':
                    continue
            
            if not nombre or not email:
                print("❌ Nombre y email son obligatorios")
                continue
                
            cliente, archivo = sistema.agregar_cliente(nombre, email, telefono, int(duracion), equipo_id)
            if cliente:
                print(f"✅ Cliente agregado exitosamente con licencia VINCULADA!")
                
                if archivo and os.path.exists(archivo):
                    print(f"📄 Licencia avanzada VINCULADA guardada en: {archivo}")
                    print(f"🔑 Código de activación: {cliente['codigo_licencia']}")
                    print(f"🔒 Vinculada al equipo: {equipo_id}")
                    print(f"🔐 Características de seguridad:")
                    print(f"   • VINCULACIÓN POR HARDWARE")
                    print(f"   • HMAC-SHA512 para verificación de integridad")
                    print(f"   • Encriptación AES-256 para datos sensibles")
                    print(f"   • No transferible entre equipos")
                else:
                    print("⚠️ Licencia generada pero no se pudo verificar el archivo")
            else:
                print("❌ Error agregando cliente")
            
        elif opcion == "2":
            sistema.listar_clientes()
            
        elif opcion == "3":
            email = input("Email del cliente a renovar: ").strip()
            if not email:
                print("❌ Email requerido")
                continue
                
            duracion = input("Nueva duración en días [30]: ").strip() or "30"
            
            resultado, archivo = sistema.renovar_licencia(email, int(duracion))
            if resultado:
                print(f"✅ Licencia avanzada VINCULADA renovada exitosamente!")
                
                if archivo and os.path.exists(archivo):
                    print(f"📄 Nueva licencia avanzada: {archivo}")
                    print(f"🔒 Mantiene vinculación al equipo original")
                else:
                    print("⚠️ Licencia renovada pero no se pudo verificar el archivo")
            else:
                print(f"❌ {archivo}")
                
        elif opcion == "4":
            email = input("Email a buscar: ").strip()
            cliente = sistema.buscar_cliente(email)
            if cliente:
                print(f"\n✅ Cliente encontrado:")
                print(f"   Nombre: {cliente['nombre']}")
                print(f"   Email: {cliente['email']}")
                print(f"   Teléfono: {cliente['telefono']}")
                print(f"   Código: {cliente['codigo_licencia']}")
                print(f"   ID: {cliente['id']}")
                print(f"   Seguridad: {cliente.get('seguridad', 'básica')}")
                print(f"   Equipo ID: {cliente.get('equipo_id', 'No vinculado')}")
                
                patron = os.path.join(sistema.directorio_licencias, f"{cliente['id']}_licencia*.json")
                archivos = glob.glob(patron)
                if archivos:
                    print(f"   Archivos: {len(archivos)} encontrado(s)")
                    for archivo in archivos:
                        print(f"     📄 {os.path.basename(archivo)}")
                        
                        if sistema.generador.validar_licencia_avanzada(archivo):
                            print(f"       ✅ Válida (seguridad avanzada)")
                        else:
                            print(f"       ❌ Inválida o seguridad básica")
                else:
                    print("   ⚠️ No se encontraron archivos de licencia")
            else:
                print("❌ Cliente no encontrado")
        
        elif opcion == "5":
            print("\n🗑️  ELIMINAR CLIENTE")
            print("-" * 30)
            
            if not sistema.clientes:
                print("❌ No hay clientes registrados")
                continue
                
            sistema.listar_clientes()
            
            print("\n¿Cómo desea eliminar?")
            print("1. Por email")
            print("2. Por número de lista")
            print("3. Cancelar")
            
            metodo = input("Seleccione método [1]: ").strip() or "1"
            
            if metodo == "1":
                email = input("Email del cliente a eliminar: ").strip()
                if not email:
                    print("❌ Email requerido")
                    continue
                    
                cliente = sistema.buscar_cliente(email)
                if cliente:
                    print(f"\n⚠️  ¿ESTÁ SEGURO DE ELIMINAR ESTE CLIENTE?")
                    print(f"   Nombre: {cliente['nombre']}")
                    print(f"   Email: {cliente['email']}")
                    print(f"   Se eliminarán TODOS sus archivos de licencia")
                    
                    confirmar = input("\n¿Continuar? (s/N): ").strip().lower()
                    if confirmar == 's':
                        resultado, mensaje = sistema.eliminar_cliente(email)
                        print(f"\n{mensaje}")
                    else:
                        print("❌ Eliminación cancelada")
                else:
                    print("❌ Cliente no encontrado")
                    
            elif metodo == "2":
                numero = input("Número del cliente a eliminar: ").strip()
                if not numero:
                    print("❌ Número requerido")
                    continue
                    
                cliente = sistema.buscar_cliente_por_indice(numero)
                if cliente:
                    print(f"\n⚠️  ¿ESTÁ SEGURO DE ELIMINAR ESTE CLIENTE?")
                    print(f"   Nombre: {cliente['nombre']}")
                    print(f"   Email: {cliente['email']}")
                    print(f"   Se eliminarán TODOS sus archivos de licencia")
                    
                    confirmar = input("\n¿Continuar? (s/N): ").strip().lower()
                    if confirmar == 's':
                        resultado, mensaje = sistema.eliminar_cliente(cliente['email'])
                        print(f"\n{mensaje}")
                    else:
                        print("❌ Eliminación cancelada")
                else:
                    print("❌ Número de cliente inválido")
                    
            else:
                print("✅ Operación cancelada")
                
        elif opcion == "6":
            sistema.verificar_archivos_licencias()
            
        elif opcion == "7":
            sistema.generar_reporte_seguridad()
            
        elif opcion == "8":
            sistema.obtener_equipo_id_cliente()
                
        elif opcion == "9":
            print("\n🧪 PROBANDO GENERADOR DE LICENCIAS AVANZADAS")
            print("-" * 50)
            
            from licenses.generador_licencias import generar_licencia_rapida
            generar_licencia_rapida()
                
        elif opcion == "10":
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    print("🔒 Iniciando Sistema de Licencias - Seguridad Avanzada v2.0...")
    print("📦 Características implementadas:")
    print("   • VINCULACIÓN POR EQUIPO: Licencias no transferibles")
    print("   • HMAC-SHA512 para hashes seguros")
    print("   • Encriptación AES-256 para datos sensibles") 
    print("   • Validación multi-capa")
    print("   • Checksums SHA3-512 para integridad\n")
    
    sistema = SistemaLicencias()
    
    print("🧪 Probando generador de licencias avanzadas...")
    test_licencia, test_archivo = sistema.generador.generar_y_guardar_automatico("TEST-SISTEMA-ADV", 1, "TEST-SISTEMA-ADV")
    if test_archivo and os.path.exists(test_archivo):
        print("✅ Generador de licencias avanzadas funcionando correctamente")
        
        print("🔍 Validando licencia de prueba...")
        if sistema.generador.validar_licencia_avanzada(test_archivo):
            print("✅ Licencia de prueba validada exitosamente")
        else:
            print("❌ Licencia de prueba no pudo ser validada")
            
        try:
            os.remove(test_archivo)
            print("✅ Archivo de prueba limpiado")
        except:
            print("⚠️ No se pudo limpiar archivo de prueba")
    else:
        print("❌ Problema con el generador de licencias avanzadas")
    
    menu_principal()