import os
import sys
import json
import atexit
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QMessageBox, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox, QLineEdit, QGroupBox, QDialog, QSizePolicy
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer, pyqtSignal

from database import DatabaseManager
from auth_manager import LoginDialog
from ticket_generator import generar_ticket
from user_manager import UserManagerDialog
from inventory_manager import InventoryManagerDialog
from cash_close_manager import CashCloseManagerDialog
from backup_manager import BackupManagerDialog
from category_manager import CategoryManagerDialog
from sales_history import SalesHistoryDialog
from config_panel import ConfigPanelDialog
from config_manager import config_manager
from themes import obtener_tema
from utils.helpers import formato_moneda_mx
from licenses.licencias_manager import LicenseManager
from licenses.dialogo_activacion import DialogoActivacion

# Agregar el directorio licenses al path
current_dir = os.path.dirname(os.path.abspath(__file__))
licenses_dir = os.path.join(current_dir, 'licenses')
if os.path.exists(licenses_dir):
    sys.path.append(licenses_dir)

# Detección de plataforma
def es_windows():
    return sys.platform.startswith('win')

# Configuración DPI para Windows
if es_windows():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        print("✅ Configuración DPI aplicada para Windows")
    except Exception as e:
        print(f"⚠️ No se pudo configurar DPI: {e}")

class CajaGUI(QWidget):
    def __init__(self):
        super().__init__()

        # INICIALIZAR CONFIGURACIÓN PRIMERO
        self.inicializar_configuracion_por_defecto()
        
        # Cargar y verificar configuración
        self.cargar_configuracion()

        self.config = config_manager.load_config()

        # DIAGNÓSTICO DE CONFIGURACIÓN
        print("=== DIAGNÓSTICO INICIAL CONFIGURACIÓN ===")
        print(f"📋 Configuración cargada: {self.config}")
        print(f"📁 Logo path: {self.config.get('logo_path', 'NO EXISTE')}")
        print(f"🏪 Nombre negocio: {self.config.get('nombre_negocio', 'NO EXISTE')}")
        print(f"🎨 Tema: {self.config.get('tema', 'NO EXISTE')}")

        # INICIALIZAR GESTOR DE LICENCIAS
        self.license_manager = LicenseManager()

        # Cargar y verificar configuración
        self.cargar_configuracion()

        self.config = config_manager.load_config()

        # DIAGNÓSTICO DE CONFIGURACIÓN
        print("=== DIAGNÓSTICO INICIAL CONFIGURACIÓN ===")
        print(f"📋 Configuración cargada: {self.config}")
        print(f"📁 Logo path: {self.config.get('logo_path', 'NO EXISTE')}")
        print(f"🏪 Nombre negocio: {self.config.get('nombre_negocio', 'NO EXISTE')}")
        print(f"🎨 Tema: {self.config.get('tema', 'NO EXISTE')}")

        # INICIALIZAR GESTOR DE LICENCIAS
        self.license_manager = LicenseManager()

        # VERIFICAR LICENCIA AL INICIAR 
        if not self.verificar_licencia():
            print("❌ Licencia no válida, cerrando aplicación")
            sys.exit(1)

        # Inicializar el resto de componentes
        self.db_manager = DatabaseManager()
        self.carrito = []
        self.metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]

        # Registrar guardado al cerrar
        atexit.register(self.guardar_configuracion_al_cerrar)

        # AUTENTICAR USUARIO
        self.autenticar_usuario()
        
        # VERIFICACIÓN FINAL
        if not hasattr(self, 'current_user') or self.current_user is None:
            print("❌ No se pudo autenticar usuario - Cerrando aplicación")
            sys.exit(1)

        print(f"✅ Usuario autenticado: {self.current_user['nombre']}")
            
        # Inicializar interfaz
        self.init_ui()
        self.aplicar_tema()

    def inicializar_configuracion_por_defecto(self):
        """Crea configuración por defecto si no existe"""
        try:
            # Crear directorio data si no existe
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print("✅ Directorio 'data' creado automáticamente")
            
            # Configuración por defecto
            config_por_defecto = {
                "nombre_negocio": "Mi Negocio",
                "tema": "claro",
                "iva": 0.16,
                "logo_path": "",
                "moneda": "MXN"
            }
            
            # Verificar si existe config.json, si no, crearlo
            config_path = os.path.join(data_dir, "config.json")
            if not os.path.exists(config_path):
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config_por_defecto, f, indent=4, ensure_ascii=False)
                print("✅ Archivo config.json creado con valores por defecto")
            
            # Verificar si existe config_demo.json (para el sistema de licencias)
            config_demo_path = os.path.join(data_dir, "config_demo.json")
            if not os.path.exists(config_demo_path):
                config_demo_por_defecto = {"ventas_realizadas": 0}
                with open(config_demo_path, 'w', encoding='utf-8') as f:
                    json.dump(config_demo_por_defecto, f, indent=4)
                print("✅ Archivo config_demo.json creado")
                
            # Verificar si existe la base de datos
            db_path = os.path.join(data_dir, "caja_registradora.db")
            if not os.path.exists(db_path):
                print("⚠️ Base de datos no encontrada - Se creará al iniciar")
                # La base de datos se creará automáticamente cuando se inicialice DatabaseManager
                
            return True
            
        except Exception as e:
            print(f"❌ Error creando configuración por defecto: {e}")
            return False

    def cargar_configuracion(self):
        """Cargar configuración desde archivo - CON MANEJO DE ERRORES MEJORADO"""
        try:
            self.config = config_manager.load_config()
            
            # ✅ GARANTIZAR que siempre tengamos las claves mínimas necesarias
            claves_requeridas = {
                'tema': 'claro',
                'nombre_negocio': 'Mi Negocio', 
                'iva': 0.16,
                'logo_path': '',
                'moneda': 'MXN'
            }
            
            config_actualizada = False
            for clave, valor_por_defecto in claves_requeridas.items():
                if clave not in self.config:
                    self.config[clave] = valor_por_defecto
                    config_actualizada = True
                    print(f"✅ Clave agregada: {clave} = {valor_por_defecto}")
            
            if config_actualizada:
                config_manager.update_config(self.config)
                print("✅ Configuración actualizada con valores por defecto")
                
            print(f"🎯 Configuración cargada: {len(self.config)} opciones")
            
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            # Configuración de emergencia
            self.config = {
                "tema": "claro",
                "nombre_negocio": "Mi Negocio",
                "iva": 0.16,
                "logo_path": "",
                "moneda": "MXN"
            }
            print("⚠️ Usando configuración de emergencia")

    def guardar_configuracion_actualizada(self):
        """Asegurar que la configuración tenga todas las claves necesarias"""
        try:
            if 'tema' not in self.config:
                self.config['tema'] = 'claro'
            config_manager.update_config(self.config)
            print("✅ Configuración actualizada guardada al iniciar")
        except Exception as e:
            print(f"❌ Error actualizando configuración: {e}")

    def autenticar_usuario(self):
        """Autenticar usuario con manejo seguro de cierre"""
        try:
            print("🔐 Iniciando autenticación de usuario...")
            
            # CORRECCIÓN: LoginDialog solo necesita db_manager
            login_dialog = LoginDialog(self.db_manager)
            login_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
            
            # Mostrar diálogo y esperar resultado
            result = login_dialog.exec()
            
            # MANEJAR CIERRE CON LA X
            if result == QDialog.DialogCode.Rejected:
                print("❌ Usuario canceló el login cerrando la ventana")
                QMessageBox.information(None, "Información", "La aplicación se cerrará.")
                QApplication.quit()
                sys.exit(0)
                
            # CORRECCIÓN: Usar user_data en lugar de get_authenticated_user()
            if hasattr(login_dialog, 'user_data'):
                self.current_user = {
                    "id": login_dialog.user_data['id'],
                    "username": login_dialog.user_data['nombre'],  
                    "nombre": login_dialog.user_data['nombre'],
                    "rol": login_dialog.user_data['rol']
                }
            else:
                self.current_user = None
            
            if not self.current_user:
                print("❌ No se pudo autenticar el usuario")
                QMessageBox.critical(None, "Error de Autenticación", 
                                "No se pudo autenticar el usuario. La aplicación se cerrará.")
                QApplication.quit()
                sys.exit(1)
                
            print(f"✅ Usuario autenticado: {self.current_user['nombre']}")
            return True
            
        except SystemExit:
            # Re-lanzar SystemExit para salida limpia
            raise
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            QMessageBox.critical(None, "Error", f"Error de autenticación: {str(e)}")
            QApplication.quit()
            sys.exit(1)

    def guardar_configuracion_al_cerrar(self):
        """Guardar configuración al cerrar la aplicación"""
        try:
            print("💾 Guardando configuración al cerrar...")
            config_actual = config_manager.load_config()
            
            if hasattr(self, 'config') and 'tema' in self.config:
                config_actual['tema'] = self.config['tema']
                print(f"✅ Guardando tema: {self.config['tema']}")
            else:
                config_actual['tema'] = 'claro'
                print("⚠️ Usando tema por defecto")
            
            config_manager.update_config(config_actual)
            print("✅ Configuración guardada al cerrar")
        except Exception as e:
            print(f"❌ Error guardando configuración al cerrar: {e}")

    def closeEvent(self, event):
        """Se ejecuta cuando la ventana se cierra"""
        print("🚪 Cerrando aplicación...")
        self.guardar_configuracion_al_cerrar()
        event.accept()

    def verificar_licencia(self):
        """Verificar licencia con importación corregida"""
        try:
            #print("🔍 Verificando licencia (seguridad avanzada)...")
            print("🔍 VERIFICANDO LICENCIA EN WINDOWS...")
            print(f"🖥️  Equipo ID en Windows: {self.license_manager.equipo_id}")
            print(f"📋 Tipo de licencia: {self.license_manager.tipo_licencia}")
            
            # Cambiar verificar_licencia() por validar_licencia()
            if self.license_manager.validar_licencia():
                info = self.license_manager.obtener_info_licencia()
                print(f"✅ Licencia verificada correctamente - Tipo: {info['tipo']} - Seguridad: {info.get('seguridad', 'avanzada')}")
                return True
            
            print("⚠️ Licencia no válida, mostrando diálogo de activación...")
            
            # Mostrar diálogo de activación
            from licenses.dialogo_activacion import DialogoActivacion
            
            # Pasar el tema actual para consistencia
            tema_actual = self.config.get('tema', 'claro')
            activacion_dialog = DialogoActivacion(self.license_manager, self, tema_actual)
            activacion_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
            
            result = activacion_dialog.exec()
            
            # Manejar cierre con X
            if result == QDialog.DialogCode.Rejected:
                print("❌ Usuario cerró la ventana de activación")
                QMessageBox.information(None, "Información", 
                                    "Se requiere una licencia válida. La aplicación se cerrará.")
                return False
                
            # Verificar nuevamente después del diálogo
            # También aquí cambiar por validar_licencia()
            if self.license_manager.validar_licencia():
                info = self.license_manager.obtener_info_licencia()
                print(f"✅ Licencia activada correctamente - Seguridad: {info.get('seguridad', 'avanzada')}")
                return True
            else:
                QMessageBox.critical(None, "Error de Licencia", 
                                "No se pudo activar la licencia. La aplicación se cerrará.")
                return False
                
        except Exception as e:
            print(f"❌ Error verificando licencia: {e}")
            QMessageBox.critical(None, "Error", 
                            f"Error al verificar la licencia: {str(e)}")
            return False

    def _login_emergencia(self):
        """Login de emergencia"""
        try:
            from PyQt6.QtWidgets import QInputDialog, QMessageBox
            
            usuario, ok = QInputDialog.getText(self, "Acceso al Sistema", "Usuario:")
            if not ok or not usuario:
                self.current_user = None
                return
                
            contraseña, ok = QInputDialog.getText(
                self, "Acceso al Sistema", "Contraseña:", 
                echo=QLineEdit.EchoMode.Password
            )
            
            if not ok or not contraseña:
                self.current_user = None
                return
            
            if usuario == "admin" and contraseña == "admin123":
                self.current_user = {
                    "id": 1, "username": "admin", "nombre": "Administrador", "rol": "administrador"
                }
                QMessageBox.information(self, "Acceso Concedido", "Bienvenido Administrador")
                print("✅ Login de emergencia exitoso")
            else:
                QMessageBox.warning(self, "Acceso Denegado", "Credenciales incorrectas")
                self.current_user = None
        except Exception as e:
            print(f"❌ Error en login de emergencia: {e}")
            self.current_user = {"id": 1, "username": "admin", "nombre": "Administrador", "rol": "administrador"}

    def aplicar_tema(self):
        """Aplicar tema desde archivo themes.py - VERSIÓN MEJORADA"""
        # Ahora usa el método mejorado para consistencia
        self.aplicar_tema_mejorado()

    def aplicar_tema_mejorado(self):
        """Aplicar tema mejorado - VERSIÓN OPTIMIZADA"""
        tema = self.config.get('tema', 'claro')
        print(f"🎨 Aplicando tema optimizado: {tema}")
        
        try:
            estilo = obtener_tema(tema)
            
            # OPTIMIZACIÓN: Aplicar solo a los contenedores principales
            self.setStyleSheet(estilo)
            
            # OPTIMIZACIÓN: Aplicar solo a widgets específicos en lugar de todos recursivamente
            widgets_principales = [
                self.tabs,  # El QTabWidget principal
                self.findChild(QGroupBox),  # Primer QGroupBox que encuentre
            ]
            
            for widget in widgets_principales:
                if widget:
                    widget.setStyleSheet(estilo)
            
            # OPTIMIZACIÓN: Actualización diferida
            QTimer.singleShot(50, self.forzar_actualizacion_ui)
            
            print(f"✅ Tema {tema} aplicado correctamente (optimizado)")
            
        except Exception as e:
            print(f"❌ Error aplicando tema optimizado: {e}")

    def forzar_actualizacion_ui(self):
        """Forzar actualización de la UI después de un breve delay"""
        self.update()
        self.repaint()
        QApplication.processEvents()

    def abrir_panel_configuracion(self):
        """Abrir panel de configuración con manejo de cambios en tiempo real"""
        try:
            dialog = ConfigPanelDialog(self.db_manager, self.config, self)
            
            # CONECTAR SEÑAL DE CAMBIOS (verificar que no dé error)
            dialog.config_changed.connect(self.aplicar_cambios_configuracion)
            
            dialog.exec()  
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir configuración: {str(e)}")

     # === MÉTODOS NUEVOS PARA CAMBIOS EN TIEMPO REAL ===

    def aplicar_cambios_configuracion(self, nuevo_config):
        """Aplica los cambios de configuración en tiempo real - VERSIÓN OPTIMIZADA"""
        try:
            print("🔄 Aplicando cambios de configuración (optimizado)...")
            
            # ACTUALIZAR CONFIGURACIÓN
            self.config.update(nuevo_config)
            
            # APLICAR NUEVO TEMA INMEDIATAMENTE (optimizado)
            self.aplicar_tema_mejorado()
            
            # ACTUALIZAR NOMBRE DEL NEGOCIO EN LA VENTANA
            if 'nombre_negocio' in nuevo_config:
                nuevo_nombre = nuevo_config['nombre_negocio']
                self.setWindowTitle(f"{nuevo_nombre} - Usuario: {self.current_user['nombre']}")
                print(f"✅ Nombre actualizado: {nuevo_nombre}")
            
            # ACTUALIZAR LOGO SI CAMBIÓ (optimizado)
            if 'logo_path' in nuevo_config:
                QTimer.singleShot(100, self.actualizar_logo_en_tiempo_real)
            
            # GUARDAR CONFIGURACIÓN PERSISTENTE (en segundo plano)
            QTimer.singleShot(200, self.guardar_configuracion_fondo)
            
            print("✅ Cambios de configuración aplicados (sin bloqueo)")
            
        except Exception as e:
            print(f"❌ Error aplicando cambios: {e}")

    def guardar_configuracion_fondo(self):
        """Guardar configuración en segundo plano para no bloquear la UI"""
        try:
            config_manager.update_config(self.config)
            print("💾 Configuración guardada en segundo plano")
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            
        
    def actualizar_logo_en_tiempo_real(self):
        """Actualiza el logo en tiempo real - VERSIÓN OPTIMIZADA"""
        try:
            # Buscar específicamente el logo label
            logo_label = None
            header_layout = self.findChild(QHBoxLayout)
            
            if header_layout:
                for i in range(header_layout.count()):
                    widget = header_layout.itemAt(i).widget()
                    if isinstance(widget, QLabel) and widget.pixmap():
                        logo_label = widget
                        break
            
            if logo_label:
                self.cargar_logo(logo_label)
                print("✅ Logo actualizado (optimizado)")
            else:
                print("⚠️ Logo label no encontrado")
                    
        except Exception as e:
            print(f"❌ Error actualizando logo: {e}")

    # ===== MÉTODOS DE GESTIÓN =====
    def gestionar_inventario(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo administradores pueden gestionar inventario")
            return
        dialog = InventoryManagerDialog(self.db_manager, self)
        dialog.exec()
        self.cargar_productos()

    def gestionar_categorias(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo administradores pueden gestionar categorías")
            return
        dialog = CategoryManagerDialog(self.db_manager, self)
        dialog.exec()

    def gestionar_cierres(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo administradores pueden gestionar cierres")
            return
        dialog = CashCloseManagerDialog(self.db_manager, self.current_user, self)
        dialog.exec()

    def gestionar_backups(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo administradores pueden gestionar backups")
            return
        dialog = BackupManagerDialog(self.db_manager, self)
        dialog.exec()

    def ver_historial_ventas(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo administradores pueden ver historial")
            return
        dialog = SalesHistoryDialog(self.db_manager, self)
        dialog.exec()

    # ===== INTERFAZ PRINCIPAL =====
    def init_ui(self):
        """Inicializar interfaz de usuario"""
        self.setWindowTitle(f"{self.config.get('nombre_negocio', 'Caja Registradora')} - Usuario: {self.current_user['nombre']}")
        self.setGeometry(100, 50, 1000, 800)

        main_layout = QVBoxLayout()
        self.setup_header(main_layout)
        self.setup_tabs(main_layout)
        self.setLayout(main_layout)
        self.cargar_productos()

    def setup_header(self, main_layout):
        """Configurar encabezado"""
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        self.cargar_logo(logo_label)
        header_layout.addWidget(logo_label)
        header_layout.addStretch(1)
        
        # Información de usuario
        user_info = QLabel(f"Usuario: {self.current_user['nombre']}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        user_info.setStyleSheet("color: #000000; background-color: rgba(255,255,255,0.7); padding: 8px; border-radius: 5px;")
        header_layout.addWidget(user_info)
        header_layout.addStretch(1)
        
        # Botón de configuración (solo admin)
        if self.current_user['rol'] == 'admin':
            btn_config = QPushButton("⚙️ Panel Configuración")
            btn_config.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold; padding: 10px;")
            btn_config.clicked.connect(self.abrir_panel_configuracion)
            header_layout.addWidget(btn_config)

        # Botón de licencia para todos los usuarios
        self.btn_licencia = QPushButton("🔐 Licencia")
        self.btn_licencia.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                font-weight: bold; 
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_licencia.setToolTip("Ver estado y activar licencia del sistema")
        self.btn_licencia.clicked.connect(self.mostrar_estado_licencia)
        header_layout.addWidget(self.btn_licencia)
        

        # Actualizar hora
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: user_info.setText(
            f"Usuario: {self.current_user['nombre']}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ))
        self.timer.start(1000)
        
        main_layout.addLayout(header_layout)

    def cargar_logo(self, logo_label):
        """Cargar logo del negocio"""
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setFixedSize(100, 100)
        
        logo_path = self.config.get("logo_path", "")
        nombre_negocio = self.config.get("nombre_negocio", "").strip()

        if logo_path and os.path.exists(os.path.join("data", logo_path)):
            try:
                pixmap = QPixmap(os.path.join("data", logo_path))
                logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
            except:
                logo_label.setText(nombre_negocio or "Logo")
        else:
            logo_label.setText(nombre_negocio or "Logo")
        
        logo_label.setStyleSheet("border: 1px solid #cccccc; border-radius: 5px; padding: 5px;")

    def setup_tabs(self, main_layout):
        """Configurar sistema de pestañas"""
        self.tabs = QTabWidget()
        
        # Pestaña de ventas
        ventas_tab = QWidget()
        ventas_layout = QVBoxLayout()
        self.setup_ventas_tab(ventas_layout)
        ventas_tab.setLayout(ventas_layout)
        self.tabs.addTab(ventas_tab, "Ventas")
        
        # Pestañas solo para admin
        if self.current_user['rol'] == 'admin':
            self.setup_admin_tabs()
        
        main_layout.addWidget(self.tabs)

    def setup_admin_tabs(self):
        """Configurar pestañas de administración"""
        inventario_tab = QWidget()
        inventario_layout = QVBoxLayout()
        self.setup_inventario_tab(inventario_layout)
        inventario_tab.setLayout(inventario_layout)
        self.tabs.addTab(inventario_tab, "Inventario")
        
        reportes_tab = QWidget()
        reportes_layout = QVBoxLayout()
        self.setup_reportes_tab(reportes_layout)
        reportes_tab.setLayout(reportes_layout)
        self.tabs.addTab(reportes_tab, "Reportes")

    def setup_ventas_tab(self, layout):
        """Configurar pestaña de ventas"""
        # Lista de productos
        product_group = QGroupBox("Productos Disponibles")
        product_layout = QVBoxLayout()
        
        self.lista = QListWidget()
        product_layout.addWidget(self.lista)
        
        # Buscador
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.buscar_producto)
        search_layout.addWidget(self.search_input)
        product_layout.addLayout(search_layout)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)

        # Botones de acción
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(QPushButton("Agregar producto", clicked=self.agregar_producto))
        botones_layout.addWidget(QPushButton("Eliminar producto", clicked=self.eliminar_producto))
        botones_layout.addWidget(QPushButton("Finalizar venta", clicked=self.finalizar_venta))
        botones_layout.addWidget(QPushButton("Cancelar venta", clicked=self.cancelar_venta))
        layout.addLayout(botones_layout)

        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Código", "Producto", "Precio", "Cantidad", "Subtotal"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_carrito)

        # Total y método de pago
        footer_layout = QHBoxLayout()

        # Total a la izquierda
        self.total_label = QLabel("Total: $0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        footer_layout.addWidget(self.total_label)

        # Espacio elástico que empuja el resto hacia la derecha
        footer_layout.addStretch(1)

        # Método de pago agrupado y pegado al combobox
        metodo_pago_layout = QHBoxLayout()
        metodo_pago_layout.addWidget(QLabel("Método de pago:"))
        self.metodo_pago_combo = QComboBox()
        self.metodo_pago_combo.addItems(self.metodos_pago)
        metodo_pago_layout.addWidget(self.metodo_pago_combo)
        metodo_pago_layout.setSpacing(5)  # Espacio reducido entre label y combobox

        # Añadir el grupo de método de pago al footer
        footer_layout.addLayout(metodo_pago_layout)

        layout.addLayout(footer_layout)

    def setup_inventario_tab(self, layout):
        """Configurar pestaña de inventario"""
        top_buttons = QHBoxLayout()
        top_buttons.addWidget(QPushButton("📦 Gestor de Inventario", clicked=self.gestionar_inventario))
        top_buttons.addWidget(QPushButton("🏷️ Gestor de Categorías", clicked=self.gestionar_categorias))
        layout.addLayout(top_buttons)
        
        summary_group = QGroupBox("Resumen de Inventario")
        summary_layout = QVBoxLayout()
        
        self.inventory_summary = QLabel("Cargando información del inventario...")
        self.inventory_summary.setStyleSheet("padding: 10px; font-size: 12px;")
        summary_layout.addWidget(self.inventory_summary)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Llamar al método para cargar datos iniciales
        self.actualizar_resumen_inventario()

    def setup_reportes_tab(self, layout):
        """Configurar pestaña de reportes"""
        top_buttons = QHBoxLayout()
        top_buttons.addWidget(QPushButton("📊 Cierres de Caja", clicked=self.gestionar_cierres))
        top_buttons.addWidget(QPushButton("💾 Sistema de Backup", clicked=self.gestionar_backups))
        top_buttons.addWidget(QPushButton("📈 Historial de Ventas", clicked=self.ver_historial_ventas))
        layout.addLayout(top_buttons)

        sales_group = QGroupBox("Resumen de Ventas Hoy")
        sales_layout = QVBoxLayout()
        self.sales_today_summary = QLabel("Cargando información...")
        sales_layout.addWidget(self.sales_today_summary)
        
        sales_group.setLayout(sales_layout)
        layout.addWidget(sales_group)
        self.actualizar_resumen_ventas_hoy()

        sales_group.setLayout(sales_layout)
        layout.addWidget(sales_group)
        self.actualizar_resumen_ventas_hoy()

    # ===== MÉTODOS DE NEGOCIO =====
    def cargar_productos(self):
        self.lista.clear()
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE activo = 1 ORDER BY nombre")
            for codigo, nombre, precio, stock in cursor.fetchall():
                precio_formateado = formato_moneda_mx(precio)
                self.lista.addItem(f"{codigo} - {nombre} - {precio_formateado} - Stock: {stock}")

    def buscar_producto(self):
        texto = self.search_input.text().lower().strip()
        for i in range(self.lista.count()):
            item = self.lista.item(i)
        
            if not texto:  # Texto vacío = mostrar todos los items
                item.setHidden(False)
            else:  # Hay texto = filtrar
                item.setHidden(texto not in item.text().lower())

    def agregar_producto(self):
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un producto de la lista.")
            return

        codigo = item.text().split(" - ")[0]
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
            producto = cursor.fetchone()
            
        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado.")
            return
            
        nombre, precio, stock = producto
        
        if stock <= 0:
            QMessageBox.warning(self, "Error", "Producto sin stock disponible.")
            return

        cantidad, ok = QInputDialog.getInt(self, "Cantidad", f"Ingrese cantidad (Stock: {stock}):", 1, 1, stock)
        if not ok:
            return

        # Agregar al carrito
        for item_carrito in self.carrito:
            if item_carrito['codigo'] == codigo:
                item_carrito['cantidad'] += cantidad
                self.actualizar_tabla()
                return

        self.carrito.append({'codigo': codigo, 'nombre': nombre, 'precio': precio, 'cantidad': cantidad})
        self.actualizar_tabla()

    def eliminar_producto(self):
        fila = self.tabla_carrito.currentRow()
        if fila >= 0:
            del self.carrito[fila]
            self.actualizar_tabla()
        else:
            QMessageBox.warning(self, "Error", "Seleccione un producto del carrito.")

    def calcular_total(self):
        return sum(item['precio'] * item['cantidad'] for item in self.carrito)

    def actualizar_tabla(self):
        self.tabla_carrito.setRowCount(0)
        for item in self.carrito:
            row = self.tabla_carrito.rowCount()
            self.tabla_carrito.insertRow(row)
            self.tabla_carrito.setItem(row, 0, QTableWidgetItem(item['codigo']))
            self.tabla_carrito.setItem(row, 1, QTableWidgetItem(item['nombre']))
            precio_formateado = formato_moneda_mx(item['precio'])
            self.tabla_carrito.setItem(row, 2, QTableWidgetItem(precio_formateado))
            self.tabla_carrito.setItem(row, 3, QTableWidgetItem(str(item['cantidad'])))

            subtotal = item['precio'] * item['cantidad']
            subtotal_formateado = formato_moneda_mx(subtotal)
            self.tabla_carrito.setItem(row, 4, QTableWidgetItem(subtotal_formateado))

        iva = self.config.get("iva", 0.18)
        total = self.calcular_total() * (1 + iva)
    
        # CAMBIAR TOTAL:
        total_formateado = formato_moneda_mx(total)
        self.total_label.setText(f"Total: {total_formateado}")

    def cancelar_venta(self):
        self.carrito = []
        self.actualizar_tabla()
        QMessageBox.information(self, "Venta cancelada", "Carrito vacío.")

    def finalizar_venta(self):
        # VERIFICAR LICENCIA DEMO ANTES DE VENDER
        if self.license_manager.tipo_licencia == "demo":
            ventas_realizadas = self.license_manager.config_demo["ventas_realizadas"]
            if ventas_realizadas >= self.license_manager.limite_ventas_demo:
                QMessageBox.warning(
                    self, 
                    "Límite Demo Alcanzado",
                    f"⚠️ Ha alcanzado el límite de {self.license_manager.limite_ventas_demo} ventas.\n\n"
                    "💎 Para continuar vendiendo, active una licencia premium."
                )
                return
            
        if not self.carrito:
            QMessageBox.warning(self, "Error", "No hay productos en el carrito.")
            return
        
        iva = self.config.get("iva", 0.18)
        total = self.calcular_total() * (1 + iva)
        metodo_pago = self.metodo_pago_combo.currentText()
        
        # Guardar venta en base de datos
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ventas (total, iva, metodo_pago, usuario_id) VALUES (?, ?, ?, ?)",
                        (total, iva, metodo_pago, self.current_user['id']))
            venta_id = cursor.lastrowid
            
            for item in self.carrito:
                # VERIFICAR QUE EL PRODUCTO EXISTA
                cursor.execute("SELECT id, stock FROM productos WHERE codigo = ? AND activo = 1", (item['codigo'],))
                resultado = cursor.fetchone()
                
                if not resultado:
                    QMessageBox.critical(self, "Error", f"Producto {item['codigo']} no encontrado")
                    conn.rollback()
                    return
                
                producto_id, stock_actual = resultado
                
                # VERIFICAR STOCK SUFICIENTE
                if stock_actual < item['cantidad']:
                    QMessageBox.critical(self, "Error", 
                                    f"Stock insuficiente para {item['codigo']}\nStock actual: {stock_actual}, Solicitado: {item['cantidad']}")
                    conn.rollback()
                    return
            
                cursor.execute('''
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (venta_id, producto_id, item['cantidad'], item['precio'], item['precio'] * item['cantidad']))
                
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE id = ?", 
                            (item['cantidad'], producto_id))
            
            conn.commit()
        
        ticket_path = generar_ticket(self.carrito, iva, total, metodo_pago, self.config.get("nombre_negocio", ""), venta_id)
        
        self.carrito = []
        self.actualizar_tabla()
        self.cargar_productos()
        
        total_formateado = formato_moneda_mx(total)
        QMessageBox.information(self, "Venta finalizada", 
                                f"Total: {total_formateado}\nMétodo: {metodo_pago}\nTicket: {ticket_path}")
        
        # REGISTRAR VENTA EN EL CONTADOR DEMO
        self.license_manager.registrar_venta()
        self.actualizar_barra_estado_licencia()
        self.actualizar_resumen_ventas_hoy()
        self.diagnosticar_ventas_hoy()
        
        # VERIFICAR LICENCIA
        if not self.license_manager.validar_licencia():
            if self.mostrar_opciones_licencia_expirada():
                print("✅ Licencia activada, continuando...")
            else:
                QMessageBox.information(self, "Información", "La aplicación se cerrará.")
                self.close()
                return

    def actualizar_resumen_ventas_hoy(self):
        """Actualiza el resumen de ventas del día actual"""
        try:
            print("🔄 Actualizando resumen de ventas hoy...")
            
            hoy = datetime.now().strftime("%Y-%m-%d")
            fecha_desde = f"{hoy} 00:00:00"
            fecha_hasta = f"{hoy} 23:59:59"
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_importe
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                """, (fecha_desde, fecha_hasta))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    count = resultado[0]
                    total = resultado[1]
                else:
                    count = 0
                    total = 0
                
                print(f"📊 Ventas encontradas hoy: {count}, Total: {total}")
            
            # ACTUALIZAR SIEMPRE - incluso si no hay ventas
            if hasattr(self, 'sales_today_summary') and self.sales_today_summary:
                if count > 0:
                    texto = f"""📊 VENTAS HOY ({hoy})
    • Total ventas: {formato_moneda_mx(total)}
    • N° de ventas: {count}"""
                else:
                    texto = f"""📊 VENTAS HOY ({hoy})
    • No hay ventas registradas hoy
    • Total: {formato_moneda_mx(0)}
    • N° de ventas: 0"""
                
                self.sales_today_summary.setText(texto)
                print(f"✅ Resumen ventas actualizado: {count} ventas, {formato_moneda_mx(total)}")
                    
        except Exception as e:
            print(f"❌ Error actualizando resumen de ventas: {e}")
            # ✅ MOSTRAR ERROR EN LA INTERFAZ
            if hasattr(self, 'sales_today_summary') and self.sales_today_summary:
                self.sales_today_summary.setText(f"❌ Error cargando ventas: {str(e)}")

    def diagnosticar_ventas_hoy(self):
        """Función de diagnóstico para ventas de hoy"""
        try:
            hoy = datetime.now().strftime("%Y-%m-%d")
            fecha_desde = f"{hoy} 00:00:00"
            fecha_hasta = f"{hoy} 23:59:59"
            
            print(f"=== DIAGNÓSTICO VENTAS HOY ===")
            print(f"📅 Fecha: {hoy}")
            print(f"🔍 Rango: {fecha_desde} a {fecha_hasta}")
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar todas las ventas de hoy
                cursor.execute("""
                    SELECT id, fecha, total, estado 
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ?
                    ORDER BY fecha DESC
                """, (fecha_desde, fecha_hasta))
                
                ventas_hoy = cursor.fetchall()
                print(f"📦 Ventas encontradas: {len(ventas_hoy)}")
                
                for venta in ventas_hoy:
                    print(f"   Venta #{venta[0]}: {venta[1]} - {venta[2]} - {venta[3]}")
                
                # Verificar conteo
                cursor.execute("""
                    SELECT COUNT(*), SUM(total) 
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                """, (fecha_desde, fecha_hasta))
                
                count, total = cursor.fetchone()
                print(f"📊 Resumen - Count: {count}, Total: {total}")
                
            return len(ventas_hoy)
            
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")
            return 0

    def actualizar_resumen_inventario(self):
        """Actualiza el resumen de inventario en tiempo real"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Productos con stock bajo
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM productos 
                    WHERE stock <= stock_minimo AND activo = 1
                """)
                stock_bajo = cursor.fetchone()[0] or 0
                
                # Total de productos activos
                cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
                total_productos = cursor.fetchone()[0] or 0
                
                # Productos sin stock
                cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0 AND activo = 1")
                sin_stock = cursor.fetchone()[0] or 0
                
                # Productos que necesitan atención inmediata (stock = 0)
                cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0 AND activo = 1")
                sin_stock_urgente = cursor.fetchone()[0] or 0
        
            # Actualizar la interfaz si el widget existe
            if hasattr(self, 'inventory_summary') and self.inventory_summary:
                if total_productos > 0:
                    texto = f"""📊 RESUMEN DE INVENTARIO:
                    
    • 📦 Productos activos: {total_productos}
    • ⚠️  Productos con stock bajo: {stock_bajo}
    • 🔴 Productos sin stock: {sin_stock}
    • 🚨 Necesitan atención urgente: {sin_stock_urgente}

    """
                    if stock_bajo > 0 or sin_stock > 0:
                        texto += f"🔔 ALERTA: {stock_bajo + sin_stock} productos necesitan reposición"
                    else:
                        texto += "✅ Todo en orden - Inventario saludable"
                else:
                    texto = "📦 No hay productos en el inventario\n\n💡 Agregue productos desde 'Gestor de Inventario'"
                
                self.inventory_summary.setText(texto)
                print(f"✅ Resumen inventario actualizado: {total_productos} productos")
                    
        except Exception as e:
            print(f"❌ Error actualizando resumen de inventario: {e}")
            if hasattr(self, 'inventory_summary') and self.inventory_summary:
                self.inventory_summary.setText("❌ Error cargando información de inventario")

# ==== SECCION DE LICENSIA ===

    def mostrar_opciones_licencia_expirada(self):
        """Muestra opciones cuando la licencia demo expira"""
        from PyQt6.QtWidgets import QMessageBox, QPushButton
    
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Límite Demo Alcanzado")
        msg_box.setIcon(QMessageBox.Icon.Warning)
    
        # Mensaje según el tipo de problema
        if self.license_manager.tipo_licencia == "demo":
            mensaje = f"""
            ⚠️ HA ALCANZADO EL LÍMITE DE {self.license_manager.limite_ventas_demo} VENTAS
        
            La versión demo ha expirado. Para continuar usando el software:
        
            💎 **Opciones disponibles:**
            • Activar una licencia premium (uso ilimitado)
            • Contactar para adquirir una licencia
            • Cerrar la aplicación
        
            📞 **Contacto:**
            📧 ventas@cajaregistradora.com
            📱 +52 55 1234 5678
        """
        else:
            mensaje = """
            ⚠️ LICENCIA REQUERIDA
        
            Para usar el software necesita una licencia válida.
        
            💎 **Opciones disponibles:**
            • Activar una licencia premium
            • Contactar para adquirir una licencia  
            • Cerrar la aplicación
        
            📞 **Contacto:**
            📧 ventas@cajaregistradora.com
            📱 +52 55 1234 5678
            """
    
        msg_box.setText(mensaje)
    
        # Botones personalizados
        btn_activar = QPushButton("🎫 Activar Licencia Premium")
        btn_contacto = QPushButton("📞 Ver Información de Contacto")
        btn_cerrar = QPushButton("❌ Cerrar Aplicación")
    
        msg_box.addButton(btn_activar, QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(btn_contacto, QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(btn_cerrar, QMessageBox.ButtonRole.RejectRole)
    
        msg_box.exec()
    
        boton_presionado = msg_box.clickedButton()
    
        if boton_presionado == btn_activar:
            print("🎫 Usuario eligió activar licencia")
            if self.mostrar_activacion():
                # Si la activación fue exitosa, verificar nuevamente
                if self.license_manager.validar_licencia():
                    QMessageBox.information(self, "✅ Éxito", "Licencia activada correctamente!")
                    self.actualizar_barra_estado_licencia()
                    return True
                else:
                    QMessageBox.warning(self, "Error", "No se pudo activar la licencia")
                    return False
            else:
                return False
            
        elif boton_presionado == btn_contacto:
            print("📞 Usuario eligió ver contacto")
            self.mostrar_informacion_contacto()
            # Después de ver contacto, volver a mostrar opciones
            return self.mostrar_opciones_licencia_expirada()
        
        else:  # btn_cerrar
            print("❌ Usuario eligió cerrar aplicación")
            return False
        
    def actualizar_barra_estado_licencia(self):
        """Método simplificado - Ya no muestra el cuadro de estado"""
        # ✅ Este método ahora no hace nada visible, pero se mantiene
        # para no romper otras partes del código que lo llaman
        pass

    def mostrar_estado_licencia(self):
        """Muestra estado de licencia - VERSIÓN MEJORADA CON DEMO"""
        try:
            from PyQt6.QtWidgets import QMessageBox, QPushButton
    
            info = self.license_manager.obtener_info_licencia()
            tipo_licencia = self.license_manager.tipo_licencia
        
            # Crear mensaje según el tipo de licencia
            if info['estado'] == 'activa':
                if tipo_licencia == 'premium':
                    mensaje = f"💎 LICENCIA PREMIUM ACTIVA\n\nCaracterísticas:\n• Ventas ilimitadas\n• Sin restricciones\n• Soporte prioritario"
                else:  # demo
                    mensaje = f"🔬 VERSIÓN DEMO ACTIVA\n\nVentas restantes: {info['dias_restantes']}\nLímite total: {self.license_manager.limite_ventas_demo} ventas"
            else:
                mensaje = "❌ LICENCIA EXPIRADA O NO VÁLIDA"
    
            # Crear MessageBox personalizado
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Estado de Licencia")
            msg_box.setText(mensaje)
    
            # Añadir botones personalizados
            btn_activar = QPushButton("🎫 Activar Licencia Premium")
            btn_validar = QPushButton("🔄 Validar Estado")
            btn_cerrar = QPushButton("Cerrar")
    
            msg_box.addButton(btn_activar, QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(btn_validar, QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(btn_cerrar, QMessageBox.ButtonRole.RejectRole)
    
            # Ejecutar y capturar respuesta
            msg_box.exec()
    
            # Ver qué botón se presionó
            boton_presionado = msg_box.clickedButton()
    
            if boton_presionado == btn_activar:
                print("🎫 Usuario eligió: Activar Licencia")
                self.mostrar_activacion()
            elif boton_presionado == btn_validar:
                print("🔄 Usuario eligió: Validar")
                self.validar_licencia_simple()
            else:
                print("❌ Usuario cerró el diálogo")
        
        except Exception as e:
            print(f"❌ Error en mostrar_estado_licencia: {e}")
            QMessageBox.information(self, "Licencia", "Estado: Activada")

    def mostrar_activacion(self):
        """Muestra diálogo de activación mejorado"""
        try:
            from licenses.dialogo_activacion import DialogoActivacion
        
            # PASAR EL TEMA ACTUAL AL DIÁLOGO
            tema_actual = self.config.get('tema', 'claro')
            dialogo = DialogoActivacion(self.license_manager, self, tema_actual)
        
            resultado = dialogo.exec()
        
            if resultado == QDialog.DialogCode.Accepted:
                # Verificar si la activación fue exitosa
                if self.license_manager.validar_licencia():
                    info = self.license_manager.obtener_info_licencia()
                    QMessageBox.information(
                        self, 
                        "✅ Activación Exitosa",
                        f"Licencia premium activada correctamente!\n\n"
                        f"Válida por: {info['dias_restantes']} días\n"
                        f"Expira: {info['expiracion']}"
                    )
                    self.actualizar_barra_estado_licencia()
                    return True
                else:
                    QMessageBox.warning(self, "Error", "La activación no fue exitosa")
                    return False
            return False
            
        except Exception as e:
            print(f"❌ Error en mostrar_activacion: {e}")
            QMessageBox.warning(self, "Error", "No se pudo abrir el diálogo de activación")
            return False
        
    def mostrar_informacion_contacto(self):
        """Muestra información de contacto detallada"""
        mensaje = """
        💎 **INFORMACIÓN DE CONTACTO - LICENCIAS PREMIUM**
    
        Para adquirir una licencia premium y desbloquear todas las funciones:
    
        📧 **Email:** ventas@cajaregistradora.com
        📱 **Teléfono:** +52 55 1234 5678
        🌐 **Sitio web:** www.cajaregistradora.com
    
        💰 **Beneficios de la licencia premium:**
        • Ventas ilimitadas
        • Sin restricciones de tiempo
        • Soporte técnico prioritario
        • Actualizaciones gratuitas
        • Múltiples usuarios
    
        ⏰ **Horario de atención:**
        Lunes a Viernes: 8:00 AM - 5:00 PM
    
        ¡Estamos para servirle!
        """
    
        QMessageBox.information(self, "Información de Contacto", mensaje)

    def validar_licencia_simple(self):
        """Valida la licencia - VERSIÓN SIMPLE"""
        try:
            if self.license_manager.validar_licencia():
                info = self.license_manager.obtener_info_licencia()
                if self.license_manager.tipo_licencia == "premium":
                    QMessageBox.information(self, "✅ Válida", "Licencia premium activa y válida.")
                else:
                    QMessageBox.information(self, "🔬 Demo", f"Versión demo activa. {info['mensaje']}")
            else:
                QMessageBox.warning(self, "❌ Inválida", "La licencia no es válida o ha expirado.")
        except Exception as e:
            print(f"Error en validar_licencia: {e}")
            QMessageBox.warning(self, "Error", "Error al validar la licencia")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CajaGUI()
    ventana.show()
    sys.exit(app.exec())