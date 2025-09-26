import json
import os
import sys
from datetime import datetime, timedelta
import glob

# Agregar el path para importar generador_licencias
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from licenses.generador_licencias import GeneradorLicencias

class SistemaLicencias:
    def __init__(self):
        self.generador = GeneradorLicencias()
        
        # 📁 RUTAS ABSOLUTAS CORREGIDAS
        self.base_dir = self.obtener_directorio_base()
        self.archivo_clientes = os.path.join(self.base_dir, "data", "clientes_licencias.json")
        self.directorio_licencias = os.path.join(self.base_dir, "licencias")
        
        print(f"🔍 Rutas configuradas:")
        print(f"   Base: {self.base_dir}")
        print(f"   Clientes: {self.archivo_clientes}")
        print(f"   Licencias: {self.directorio_licencias}")
        
        self.cargar_clientes()
        self.ensure_directories()
    
    def obtener_directorio_base(self):
        """Obtiene la ruta base del proyecto"""
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Si estamos en licenses/, subir un nivel al directorio principal
            if os.path.basename(current_dir) == 'licenses':
                base_dir = os.path.dirname(current_dir)
            else:
                # Si no, asumir que estamos en el directorio base
                base_dir = current_dir
            
            # VERIFICAR que el directorio base es correcto
            if not os.path.exists(base_dir):
                print(f"❌ Directorio base no existe: {base_dir}")
                # Fallback: directorio actual de trabajo
                base_dir = os.getcwd()
                print(f"✅ Usando directorio actual: {base_dir}")
            
            return base_dir
            
        except Exception as e:
            print(f"❌ Error detectando directorio base: {e}")
            return os.getcwd()
    
    def ensure_directories(self):
        """Asegura que los directorios existan"""
        try:
            # CREAR DIRECTORIO licencias/ (con 'c' no 's')
            if not os.path.exists(self.directorio_licencias):
                os.makedirs(self.directorio_licencias, exist_ok=True)
                print(f"✅ Directorio de licencias creado: {self.directorio_licencias}")
            else:
                print(f"✅ Directorio de licencias ya existe: {self.directorio_licencias}")
            
            # Directorio data
            data_dir = os.path.join(self.base_dir, "data")
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"✅ Directorio data creado: {data_dir}")
            
            # VERIFICAR permisos de escritura
            if not os.access(self.directorio_licencias, os.W_OK):
                print(f"❌ Sin permisos de escritura en: {self.directorio_licencias}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Error creando directorios: {e}")
            return False
    
    def cargar_clientes(self):
        """Carga la base de datos de clientes"""
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
        """Guarda la base de datos de clientes"""
        try:
            with open(self.archivo_clientes, 'w', encoding='utf-8') as f:
                json.dump(self.clientes, f, indent=4, ensure_ascii=False)
            print("✅ Base de datos de clientes guardada")
        except Exception as e:
            print(f"❌ Error guardando clientes: {e}")
    
    def agregar_cliente(self, nombre, email, telefono, duracion_dias=30):
        """Agrega un nuevo cliente y genera su licencia"""
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
                "estado": "activo"
            }
            
            # Generar licencia
            licencia = self.generador.generar_licencia(codigo_licencia, duracion_dias, id_cliente)
            
            if not licencia:
                return None, "Error generando licencia"
            
            # DEFINIR RUTA CORRECTA PARA GUARDAR
            archivo_licencia = os.path.join(
                self.directorio_licencias,
                f"{id_cliente}_licencia.json"
            )
            
            print(f"📁 Guardando licencia en: {archivo_licencia}")
            
            # Guardar licencia
            if self.generador.guardar_licencia(licencia, archivo_licencia):
                # Agregar a base de datos
                self.clientes.append(cliente)
                self.guardar_clientes()
                
                print(f"✅ Cliente agregado: {nombre}")
                print(f"📄 Licencia guardada en: {archivo_licencia}")
                return cliente, archivo_licencia
            else:
                return None, "Error guardando archivo de licencia"
            
        except Exception as e:
            print(f"❌ Error agregando cliente: {e}")
            return None, f"Error: {str(e)}"
    
    def listar_clientes(self):
        """Lista todos los clientes"""
        print(f"\n📋 LISTA DE CLIENTES ({len(self.clientes)} registros)")
        print("=" * 80)
        
        if not self.clientes:
            print("   No hay clientes registrados")
            return
        
        for i, cliente in enumerate(self.clientes, 1):
            fecha_registro = datetime.fromisoformat(cliente['fecha_registro']).strftime('%d/%m/%Y')
            print(f"{i:2d}. {cliente['nombre']:20} | {cliente['email']:25} | {cliente['codigo_licencia']:15} | Reg: {fecha_registro}")
    
    def buscar_cliente(self, email):
        """Busca un cliente por email"""
        for cliente in self.clientes:
            if cliente['email'].lower() == email.lower():
                return cliente
        return None
    
    def buscar_cliente_por_indice(self, indice):
        """Busca cliente por índice en la lista"""
        try:
            indice = int(indice) - 1  # Convertir a base 0
            if 0 <= indice < len(self.clientes):
                return self.clientes[indice]
            else:
                return None
        except ValueError:
            return None
    
    def renovar_licencia(self, email, duracion_dias=30):
        """Renueva la licencia de un cliente"""
        try:
            cliente = self.buscar_cliente(email)
            if not cliente:
                return False, "Cliente no encontrado"
            
            print(f"🔄 Renovando licencia para: {cliente['nombre']}")
            
            # CORREGIR RUTA DE GUARDADO - usar directorio_licencias correcto
            archivo_licencia = os.path.join(
                self.directorio_licencias,
                f"{cliente['id']}_licencia_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            print(f"📁 Intentando guardar en: {archivo_licencia}")
            
            # Generar nueva licencia
            nueva_licencia = self.generador.generar_licencia(
                cliente['codigo_licencia'], 
                duracion_dias, 
                cliente['id']
            )
            
            if not nueva_licencia:
                return False, "Error generando nueva licencia"
            
            # GUARDAR EN LA RUTA CORRECTA
            if self.generador.guardar_licencia(nueva_licencia, archivo_licencia):
                print(f"✅ Licencia guardada correctamente en: {archivo_licencia}")
                
                # Actualizar cliente
                cliente['duracion_dias'] = duracion_dias
                cliente['fecha_renovacion'] = datetime.now().isoformat()
                self.guardar_clientes()
                
                return True, archivo_licencia
            else:
                return False, "Error guardando nueva licencia"
            
        except Exception as e:
            print(f"❌ Error renovando licencia: {e}")
            return False, f"Error: {str(e)}"
    
    def eliminar_cliente(self, email):
        """Elimina un cliente y sus archivos de licencia"""
        try:
            cliente = self.buscar_cliente(email)
            if not cliente:
                return False, "Cliente no encontrado"
            
            print(f"🗑️  Eliminando cliente: {cliente['nombre']} ({cliente['email']})")
            
            # 1. ELIMINAR ARCHIVOS DE LICENCIA DEL CLIENTE
            archivos_eliminados = self.eliminar_archivos_cliente(cliente['id'])
            
            # 2. ELIMINAR CLIENTE DE LA BASE DE DATOS
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
        """Elimina todos los archivos de licencia de un cliente"""
        try:
            # Buscar todos los archivos del cliente
            patron = os.path.join(self.directorio_licencias, f"{id_cliente}_licencia*.json")
            archivos = glob.glob(patron)
            
            archivos_eliminados = 0
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
        """Verifica que todos los archivos de licencia existan"""
        print(f"\n🔍 VERIFICANDO ARCHIVOS DE LICENCIAS EN: {self.directorio_licencias}")
        problemas = 0
        
        # VERIFICAR que el directorio existe
        if not os.path.exists(self.directorio_licencias):
            print(f"❌ Directorio de licencias no existe: {self.directorio_licencias}")
            crear = input("   ¿Crear directorio? (s/n): ").strip().lower()
            if crear == 's':
                os.makedirs(self.directorio_licencias, exist_ok=True)
                print(f"✅ Directorio creado: {self.directorio_licencias}")
            else:
                return
        
        for cliente in self.clientes:
            # BUSCAR ARCHIVOS EN EL DIRECTORIO CORRECTO
            patron = os.path.join(self.directorio_licencias, f"{cliente['id']}_licencia*.json")
            archivos = glob.glob(patron)
            
            if archivos:
                print(f"✅ {cliente['nombre']}: {len(archivos)} archivo(s)")
                for archivo in archivos:
                    print(f"   📄 {os.path.basename(archivo)}")
            else:
                print(f"❌ {cliente['nombre']}: SIN ARCHIVO DE LICENCIA")
                problemas += 1
                
                # Ofrecer regenerar
                regenerar = input("   ¿Regenerar licencia? (s/n): ").strip().lower()
                if regenerar == 's':
                    resultado, archivo = self.renovar_licencia(cliente['email'], cliente['duracion_dias'])
                    if resultado:
                        print(f"   ✅ Licencia regenerada: {os.path.basename(archivo)}")
                    else:
                        print(f"   ❌ Error: {archivo}")
        
        if problemas == 0:
            print("🎉 Todos los archivos de licencia están en orden!")
        else:
            print(f"⚠️ Se encontraron {problemas} problemas")

def menu_principal():
    """Menú interactivo del sistema de licencias"""
    sistema = SistemaLicencias()
    
    while True:
        print("\n🎫 SISTEMA DE GESTIÓN DE LICENCIAS")
        print("=" * 50)
        print("1. 🏢 Agregar nuevo cliente")
        print("2. 📋 Listar clientes")
        print("3. 🔄 Renovar licencia")
        print("4. 🔍 Buscar cliente por email")
        print("5. 🗑️  Eliminar cliente")
        print("6. 🔎 Verificar archivos de licencias")
        print("7. 🚪 Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == "1":
            print("\n➕ NUEVO CLIENTE")
            nombre = input("Nombre: ").strip()
            email = input("Email: ").strip()
            telefono = input("Teléfono: ").strip()
            duracion = input("Duración en días [30]: ").strip() or "30"
            
            if not nombre or not email:
                print("❌ Nombre y email son obligatorios")
                continue
                
            cliente, archivo = sistema.agregar_cliente(nombre, email, telefono, int(duracion))
            if cliente:
                print(f"✅ Cliente agregado exitosamente!")
                
                if archivo and os.path.exists(archivo):
                    print(f"📄 Licencia guardada en: {archivo}")
                    print(f"🔑 Código de activación: {cliente['codigo_licencia']}")
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
                print(f"✅ Licencia renovada exitosamente!")
                
                if archivo and os.path.exists(archivo):
                    print(f"📄 Nueva licencia: {archivo}")
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
                
                # Verificar si existe archivo de licencia
                patron = os.path.join(sistema.directorio_licencias, f"{cliente['id']}_licencia*.json")
                archivos = glob.glob(patron)
                if archivos:
                    print(f"   Archivos: {len(archivos)} encontrado(s)")
                    for archivo in archivos:
                        print(f"     📄 {os.path.basename(archivo)}")
                else:
                    print("   ⚠️ No se encontraron archivos de licencia")
            else:
                print("❌ Cliente no encontrado")
        
        elif opcion == "5":
            print("\n🗑️  ELIMINAR CLIENTE")
            print("-" * 30)
            
            # Mostrar clientes primero
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
                    
                # CONFIRMACIÓN DE SEGURIDAD
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
            print("👋 ¡Hasta luego!")
            break
            
        else:
            print("❌ Opción inválida")

if __name__ == "__main__":
    # 📁 VERIFICAR RUTAS Y CONFIGURACIÓN AL INICIAR
    print("🔍 Iniciando Sistema de Licencias...")
    sistema = SistemaLicencias()
    
    # Verificar que el generador funciona
    print("🧪 Probando generador de licencias...")
    test_licencia, test_archivo = sistema.generador.generar_y_guardar_automatico("TEST-SISTEMA", 1, "TEST-SISTEMA")
    if test_archivo and os.path.exists(test_archivo):
        print("✅ Generador de licencias funcionando correctamente")
        # Limpiar archivo de prueba
        try:
            os.remove(test_archivo)
        except:
            pass
    else:
        print("❌ Problema con el generador de licencias")
    
    menu_principal()