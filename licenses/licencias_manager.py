import json
import os
import hashlib
from datetime import datetime, timedelta

class LicenseManager:
    def __init__(self):
        # 📁 RUTAS ABSOLUTAS CORREGIDAS
        self.base_dir = self.obtener_directorio_base()
        self.archivo_licencia = os.path.join(self.base_dir, "data", "licencia.json")
        self.archivo_config = os.path.join(self.base_dir, "data", "config_demo.json")
        
        self.licencia_valida = False
        self.tipo_licencia = None
        self.datos_licencia = {}
        self.limite_ventas_demo = 5
        
        # 🔐 CLAVE SECRETA
        self.clave_secreta = "CAJA_REGISTRADORA_PRO_2024_SECRET_KEY_¡NO_COMPARTIR!"
        
        self.ensure_data_directory()
        self.cargar_configuracion_demo()
        self.verificar_licencia()
    
    def obtener_directorio_base(self):
        """Obtiene la ruta base del proyecto"""
        try:
            # Intentar encontrar el directorio base
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Si estamos en licenses/, subir un nivel
            if os.path.basename(current_dir) == 'licenses':
                base_dir = os.path.dirname(current_dir)
            else:
                # Si no, asumir que estamos en el directorio base
                base_dir = current_dir
            
            print(f"📁 Directorio base detectado: {base_dir}")
            return base_dir
            
        except Exception as e:
            print(f"❌ Error detectando directorio base: {e}")
            # Fallback: directorio actual
            return os.getcwd()
    
    def ensure_data_directory(self):
        """Asegura que el directorio data existe"""
        try:
            data_dir = os.path.dirname(self.archivo_licencia)
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"✅ Directorio data creado: {data_dir}")
            
            # Verificar permisos de escritura
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
            "id_instalacion": self.generar_id_instalacion()
        }
        
        try:
            # 🔥 VERIFICAR que el archivo existe antes de cargar
            if os.path.exists(self.archivo_config):
                with open(self.archivo_config, 'r', encoding='utf-8') as f:
                    self.config_demo = json.load(f)
                print(f"✅ Configuración demo cargada: {self.archivo_config}")
            else:
                self.config_demo = config_default
                # 🔥 GUARDAR INMEDIATAMENTE la configuración por defecto
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
            # 🔥 VERIFICAR que el directorio existe
            directorio = os.path.dirname(self.archivo_config)
            if not os.path.exists(directorio):
                os.makedirs(directorio, exist_ok=True)
            
            # 🔥 VERIFICAR permisos de escritura
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
        """Verifica si hay licencia premium, sino activa demo - CORREGIDO"""
        try:
            # 🔥 VERIFICAR EXISTENCIA DEL ARCHIVO con ruta absoluta
            print(f"🔍 Buscando licencia en: {self.archivo_licencia}")
            
            if os.path.exists(self.archivo_licencia):
                try:
                    with open(self.archivo_licencia, 'r', encoding='utf-8') as f:
                        datos = json.load(f)
                    
                    if self.validar_licencia_premium(datos):
                        self.licencia_valida = True
                        self.tipo_licencia = "premium"
                        self.datos_licencia = datos
                        print("✅ Licencia premium válida detectada")
                        return True
                    else:
                        print("❌ Licencia premium no válida")
                        
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
    
    def validar_licencia_premium(self, datos_licencia):
        """Valida licencia premium con todos los checks de seguridad"""
        try:
            # 1. Verificar estructura básica
            campos_requeridos = ["codigo", "fecha_activacion", "duracion_dias", "hash", "id_cliente", "tipo"]
            for campo in campos_requeridos:
                if campo not in datos_licencia:
                    print(f"❌ Licencia sin campo requerido: {campo}")
                    return False
            
            # 2. Verificar hash de seguridad
            if not self.verificar_hash_licencia(datos_licencia):
                print("❌ Hash de licencia inválido")
                return False
            
            # 3. Verificar fecha de expiración
            fecha_activacion = datetime.fromisoformat(datos_licencia["fecha_activacion"])
            fecha_expiracion = fecha_activacion + timedelta(days=datos_licencia["duracion_dias"])
            
            if datetime.now() > fecha_expiracion:
                print("❌ Licencia expirada")
                return False
            
            # 4. Verificar que no esté revocada
            if self.licencia_revocada(datos_licencia["codigo"]):
                print("❌ Licencia revocada")
                return False
            
            dias_restantes = (fecha_expiracion - datetime.now()).days
            print(f"✅ Licencia válida. Días restantes: {dias_restantes}")
            return True
            
        except Exception as e:
            print(f"❌ Error validando licencia: {e}")
            return False
    
    def verificar_hash_licencia(self, datos_licencia):
        """Verifica el hash de seguridad de la licencia"""
        try:
            # Datos que se usaron para generar el hash
            datos_verificacion = {
                'codigo': datos_licencia['codigo'],
                'fecha_activacion': datos_licencia['fecha_activacion'],
                'duracion_dias': datos_licencia['duracion_dias'],
                'id_cliente': datos_licencia['id_cliente'],
                'tipo': datos_licencia['tipo']
            }
            
            # Generar hash esperado
            cadena_verificacion = ''.join(str(v) for v in datos_verificacion.values()) + self.clave_secreta
            hash_esperado = hashlib.sha256(cadena_verificacion.encode()).hexdigest()
            
            return datos_licencia['hash'] == hash_esperado
            
        except Exception as e:
            print(f"❌ Error verificando hash: {e}")
            return False
    
    def licencia_revocada(self, codigo_licencia):
        """Verifica si la licencia está en lista negra"""
        # Por ahora vacía - podrías cargar desde servidor
        lista_negra = []
        return codigo_licencia in lista_negra
    
    def activar_licencia(self, codigo_licencia):
        """Activa una licencia premium - CORREGIDO"""
        try:
            # Verificar formato básico del código
            if not codigo_licencia or len(codigo_licencia) < 10:
                return False, "Código de licencia inválido"
            
            # Generar datos de licencia
            licencia_generada = self.generar_licencia_local(codigo_licencia)
            
            if licencia_generada:
                # 🔥 GUARDAR LICENCIA CON VERIFICACIÓN
                if self.guardar_licencia_premium(licencia_generada):
                    # Recargar verificación
                    self.verificar_licencia()
                    return True, "Licencia activada correctamente"
                else:
                    return False, "Error guardando archivo de licencia"
            else:
                return False, "No se pudo generar la licencia"
                
        except Exception as e:
            print(f"❌ Error activando licencia: {e}")
            return False, f"Error al activar licencia: {str(e)}"
    
    def guardar_licencia_premium(self, licencia):
        """Guarda la licencia premium - CORREGIDO"""
        try:
            # 🔥 VERIFICAR directorio y permisos
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
    
    def generar_licencia_local(self, codigo_licencia):
        """Genera una licencia localmente"""
        try:
            licencia = {
                "codigo": codigo_licencia,
                "fecha_activacion": datetime.now().isoformat(),
                "duracion_dias": 30,  # 30 días de prueba
                "id_cliente": f"CLI_{datetime.now().strftime('%Y%m%d')}",
                "tipo": "premium",
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
    
    def registrar_venta(self):
        """Registra una venta en el contador demo - CORREGIDO"""
        if self.tipo_licencia == "demo":
            self.config_demo["ventas_realizadas"] += 1
            # 🔥 GUARDAR INMEDIATAMENTE después de registrar
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
                'codigo': self.datos_licencia['codigo'][:8] + '...'
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
                'codigo': 'DEMO'
            }
    
    def validar_licencia(self):
        """Método compatible con tu código existente"""
        return self.licencia_valida
    
    def obtener_tipo_licencia(self):
        return self.tipo_licencia
    
    def generar_id_instalacion(self):
        """Genera un ID único para esta instalación"""
        import socket
        import uuid
        
        try:
            hostname = socket.gethostname()
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0,2*6,2)][::-1])
            id_base = f"{hostname}_{mac}"
            return hashlib.sha256(id_base.encode()).hexdigest()[:16]
        except:
            return hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]
    
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
            'config_existe': os.path.exists(self.archivo_config)
        }