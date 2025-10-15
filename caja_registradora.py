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
from email_system.email_sender import EmailSender

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
    except Exception:
        pass

class CajaGUI(QWidget):
    def __init__(self):
        super().__init__()

        # INICIALIZAR CONFIGURACIÓN
        self.inicializar_configuracion_por_defecto()
        self.cargar_configuracion()
        self.config = config_manager.load_config()

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

        # PRIMERO: Crear inventory_manager
        self.inventory_manager = InventoryManagerDialog(self.db_manager, self)

        # Conectar señales de actualización de productos
        self.inventory_manager.productos_actualizados.connect(self.actualizar_interfaz_productos)

        # Registrar guardado al cerrar
        atexit.register(self.guardar_configuracion_al_cerrar)

        # AUTENTICAR USUARIO
        self.autenticar_usuario()
        
        # VERIFICACIÓN FINAL
        if not hasattr(self, 'current_user') or self.current_user is None:
            print("❌ No se pudo autenticar usuario - Cerrando aplicación")
            sys.exit(1)
            
        # Inicializar interfaz
        self.init_ui()
        self.aplicar_tema()

        # Actualizar resumen de ventas por dia
        self.actualizar_resumen_ventas_hoy()

        # Configuracion del icono de la aplicacion
        self.configurar_icono_aplicacion()

        # AGREGAR SISTEMA DE EMAIL
        self.email_sender = EmailSender()

    def configurar_icono_aplicacion(self):
        """Configurar el icono de la aplicación para Windows - VERSIÓN MEJORADA"""
        try:
            # Ruta al icono - busca en varias ubicaciones posibles
            posibles_iconos = [
                'icono.ico',
                'data/icono.ico', 
                'data/icono.png',
                'icono.png',
                os.path.join(os.path.dirname(__file__), 'icono.ico'),
                os.path.join(os.path.dirname(__file__), 'data', 'icono.ico')
            ]
            
            icono_encontrado = False
            for icon_path in posibles_iconos:
                if os.path.exists(icon_path):
                    from PyQt6.QtGui import QIcon
                    icono = QIcon(icon_path)
                    self.setWindowIcon(icono)
                    
                    # CONFIGURACIÓN ESPECÍFICA PARA WINDOWS
                    if es_windows():
                        try:
                            import ctypes
                            # Usar un AppUserModelID único
                            app_id = 'cajaregistradora.pro.1.0'
                            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
                            print(f"✅ AppUserModelID configurado para Windows: {app_id}")
                        except Exception as win_error:
                            print(f"⚠️ No se pudo configurar AppUserModelID: {win_error}")
                    
                    print(f"✅ Icono cargado: {icon_path}")
                    icono_encontrado = True
                    break
                    
            if not icono_encontrado:
                print("⚠️ No se encontró archivo de icono en ninguna ubicación:")
                for path in posibles_iconos:
                    print(f"   • {path} - {'EXISTE' if os.path.exists(path) else 'NO EXISTE'}")
                
        except Exception as e:
            print(f"❌ Error configurando icono: {e}")

    def inicializar_configuracion_por_defecto(self):
        """Crea configuración por defecto si no existe"""
        try:
            # Crear directorio data si no existe
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
            
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
            
            # Verificar si existe config_demo.json
            config_demo_path = os.path.join(data_dir, "config_demo.json")
            if not os.path.exists(config_demo_path):
                config_demo_por_defecto = {"ventas_realizadas": 0}
                with open(config_demo_path, 'w', encoding='utf-8') as f:
                    json.dump(config_demo_por_defecto, f, indent=4)
                
            return True
            
        except Exception as e:
            print(f"❌ Error creando configuración por defecto: {e}")
            return False

    def cargar_configuracion(self):
        """Cargar configuración desde archivo"""
        try:
            self.config = config_manager.load_config()
            
            # Garantizar claves mínimas necesarias
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
            
            if config_actualizada:
                config_manager.update_config(self.config)
                
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

    def guardar_configuracion_actualizada(self):
        """Asegurar que la configuración tenga todas las claves necesarias"""
        try:
            if 'tema' not in self.config:
                self.config['tema'] = 'claro'
            config_manager.update_config(self.config)
        except Exception as e:
            print(f"❌ Error actualizando configuración: {e}")

    def autenticar_usuario(self):
        """Autenticar usuario con manejo seguro de cierre"""
        try:
            login_dialog = LoginDialog(self.db_manager)
            login_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
            
            result = login_dialog.exec()
            
            if result == QDialog.DialogCode.Rejected:
                print("❌ Usuario canceló el login")
                QMessageBox.information(None, "Información", "La aplicación se cerrará.")
                QApplication.quit()
                sys.exit(0)
                
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
            raise
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            QMessageBox.critical(None, "Error", f"Error de autenticación: {str(e)}")
            QApplication.quit()
            sys.exit(1)

    def guardar_configuracion_al_cerrar(self):
        """Guardar configuración al cerrar la aplicación"""
        try:
            config_actual = config_manager.load_config()
            
            if hasattr(self, 'config') and 'tema' in self.config:
                config_actual['tema'] = self.config['tema']
            
            config_manager.update_config(config_actual)
        except Exception as e:
            print(f"❌ Error guardando configuración al cerrar: {e}")

    def closeEvent(self, event):
        """Se ejecuta cuando la ventana se cierra - VERSIÓN SIMPLE"""
        try:
            self.guardar_configuracion_al_cerrar()
            event.accept()
        except Exception as e:
            print(f"❌ Error en closeEvent: {e}")
            self.guardar_configuracion_al_cerrar()
            event.accept()

    def verificar_licencia(self):
        """Verificar licencia - PERMITE USAR DEMO SIN ACTIVAR INMEDIATAMENTE"""
        try:
            # ✅ PRIMERO verificar si ya tiene licencia válida
            if self.license_manager.validar_licencia():
                info = self.license_manager.obtener_info_licencia()
                print(f"✅ Licencia verificada - Tipo: {info['tipo']} - Plan: {info.get('plan', 'premium')}")
                return True
            
            # ✅ SI NO TIENE LICENCIA, verificar si puede usar demo
            info_demo = self.license_manager.obtener_info_licencia()
            if info_demo['tipo'] == 'demo' and info_demo['estado'] == 'activa':
                print(f"🔬 Modo demo activo - Ventas restantes: {info_demo['dias_restantes']}")
                return True  # ✅ PERMITIR USAR DEMO
            
            # ✅ SOLO si la demo está expirada, mostrar diálogo de activación
            print("❌ Licencia no válida y demo expirada, mostrando opciones...")
            
            from licenses.dialogo_activacion import DialogoActivacion
            
            tema_actual = self.config.get('tema', 'claro')
            activacion_dialog = DialogoActivacion(self.license_manager, self, tema_actual)
            activacion_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowCloseButtonHint)
            
            result = activacion_dialog.exec()
            
            if result == QDialog.DialogCode.Rejected:
                # Usuario cerró el diálogo, preguntar si quiere usar demo
                respuesta = QMessageBox.question(
                    self, 
                    "Versión Demo",
                    "¿Desea usar la versión DEMO con 50 ventas de prueba?\n\n"
                    "Puede activar una licencia premium después desde el menú.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    print("✅ Usuario eligió usar versión demo")
                    return True
                else:
                    QMessageBox.information(self, "Información", "La aplicación se cerrará.")
                    return False
                    
            # Si activó licencia, verificar nuevamente
            if self.license_manager.validar_licencia():
                info = self.license_manager.obtener_info_licencia()
                print(f"✅ Licencia activada - Plan: {info.get('plan', 'premium')}")
                return True
            else:
                # Si falló la activación, ofrecer demo
                respuesta = QMessageBox.question(
                    self,
                    "Activación Fallida", 
                    "No se pudo activar la licencia.\n\n"
                    "¿Desea usar la versión DEMO con 50 ventas de prueba?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                return respuesta == QMessageBox.StandardButton.Yes
                    
        except Exception as e:
            print(f"❌ Error verificando licencia: {e}")
            # En caso de error, permitir demo
            QMessageBox.warning(self, "Error", f"Error al verificar licencia: {str(e)}\n\nSe iniciará en modo demo.")
            return True

    def aplicar_tema(self):
        """Aplicar tema desde archivo themes.py"""
        tema = self.config.get('tema', 'claro')
        
        try:
            estilo = obtener_tema(tema)
            self.setStyleSheet(estilo)
            
            widgets_principales = [
                self.tabs,
                self.findChild(QGroupBox),
            ]
            
            for widget in widgets_principales:
                if widget:
                    widget.setStyleSheet(estilo)
            
            QTimer.singleShot(50, self.forzar_actualizacion_ui)
            
        except Exception as e:
            print(f"❌ Error aplicando tema: {e}")

    def forzar_actualizacion_ui(self):
        """Forzar actualización de la UI"""
        self.update()
        self.repaint()
        QApplication.processEvents()

    def abrir_panel_configuracion(self):
        """Abrir panel de configuración"""
        try:
            dialog = ConfigPanelDialog(self.db_manager, self.config, self)
            dialog.config_changed.connect(self.aplicar_cambios_configuracion)
            dialog.exec()  
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir configuración: {str(e)}")

    def aplicar_cambios_configuracion(self, nuevo_config):
        """Aplica los cambios de configuración en tiempo real - VERSIÓN CORREGIDA"""
        try:
            self.config.update(nuevo_config)
            self.aplicar_tema()
            
            if 'nombre_negocio' in nuevo_config:
                nuevo_nombre = nuevo_config['nombre_negocio']
                self.setWindowTitle(f"{nuevo_nombre} - Usuario: {self.current_user['nombre']}")
                # ✅ ACTUALIZAR LOGO TAMBIÉN (porque el logo muestra el nombre)
                self.actualizar_logo_en_tiempo_real()
            
            if 'logo_path' in nuevo_config:
                # ✅ ACTUALIZAR LOGO INMEDIATAMENTE
                self.actualizar_logo_en_tiempo_real()
            
            QTimer.singleShot(200, self.guardar_configuracion_fondo)
            
        except Exception as e:
            print(f"❌ Error aplicando cambios: {e}")

    def guardar_configuracion_fondo(self):
        """Guardar configuración en segundo plano"""
        try:
            config_manager.update_config(self.config)
        except Exception as e:
            print(f"❌ Error guardando configuración: {e}")
            
    def actualizar_logo_en_tiempo_real(self):
        """Actualiza el logo en tiempo real - VERSIÓN MEJORADA"""
        try:
            # BUSCAR MÁS EFICIENTEMENTE EL LOGO LABEL
            logo_label = None
            
            # Buscar en el header layout
            header_layout = self.findChild(QHBoxLayout)
            if header_layout:
                for i in range(header_layout.count()):
                    widget = header_layout.itemAt(i).widget()
                    if isinstance(widget, QLabel) and widget.pixmap() is not None:
                        logo_label = widget
                        break
                    elif isinstance(widget, QLabel) and widget.text():  
                        # También considerar labels con texto (cuando no hay logo)
                        logo_label = widget
                        break
            
            # SI NO ENCUENTRA, BUSCAR EN TODOS LOS WIDGETS
            if not logo_label:
                for widget in self.findChildren(QLabel):
                    if widget.pixmap() is not None or (widget.text() and len(widget.text()) > 0):
                        # Verificar si es el logo por tamaño o posición
                        if widget.size().width() == 100 and widget.size().height() == 100:
                            logo_label = widget
                            break
            
            # ACTUALIZAR EL LOGO ENCONTRADO
            if logo_label:
                self.cargar_logo(logo_label)
                print("✅ Logo actualizado en tiempo real")
            else:
                print("⚠️ No se encontró el widget del logo para actualizar")
                        
        except Exception as e:
            print(f"❌ Error actualizando logo: {e}")

    # ===== MÉTODOS DE GESTIÓN =====
    def gestionar_inventario(self):
        """Abre el gestor de inventario - VERSIÓN SIMPLIFICADA"""
        try:
            # SOLO abrir el diálogo sin reconectar señales (ya están conectadas en __init__)
            self.inventory_manager.exec()
            
        except Exception as e:
            print(f"❌ Error abriendo gestor de inventario: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo abrir el gestor de inventario: {str(e)}")

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
        """Cargar logo del negocio - VERSIÓN MEJORADA"""
        try:
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setFixedSize(100, 100)
            
            logo_path = self.config.get("logo_path", "")
            nombre_negocio = self.config.get("nombre_negocio", "").strip()

            if logo_path and os.path.exists(os.path.join("data", logo_path)):
                try:
                    pixmap = QPixmap(os.path.join("data", logo_path))
                    if not pixmap.isNull():
                        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        logo_label.setText("")  # Limpiar texto
                        return
                except Exception as e:
                    print(f"❌ Error cargando imagen del logo: {e}")
            
            # ✅ SI NO HAY LOGO, MOSTRAR NOMBRE DEL NEGOCIO
            display_text = nombre_negocio if nombre_negocio else "Logo"
            if len(display_text) > 15:
                display_text = display_text[:15] + "..."
            
            logo_label.setText(display_text)
            logo_label.setPixmap(QPixmap())  # Limpiar pixmap anterior
            logo_label.setStyleSheet("""
                border: 1px solid #cccccc; 
                border-radius: 5px; 
                padding: 5px;
                background-color: #f8f9fa;
                color: #333333;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            """)
            
        except Exception as e:
            print(f"❌ Error en cargar_logo: {e}")

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

        # Espacio elástico
        footer_layout.addStretch(1)

        # Método de pago
        metodo_pago_layout = QHBoxLayout()
        metodo_pago_layout.addWidget(QLabel("Método de pago:"))
        self.metodo_pago_combo = QComboBox()
        self.metodo_pago_combo.addItems(self.metodos_pago)
        metodo_pago_layout.addWidget(self.metodo_pago_combo)
        metodo_pago_layout.setSpacing(5)

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

    # ===== MÉTODOS DE NEGOCIO =====
    def cargar_productos(self):
        self.lista.clear()
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT codigo, nombre, precio, stock 
                FROM productos 
                WHERE activo = 1 
                ORDER BY nombre
            """)
            for codigo, nombre, precio, stock in cursor.fetchall():
                precio_formateado = formato_moneda_mx(precio)
                self.lista.addItem(f"{codigo} - {nombre} - {precio_formateado} - Stock: {stock}")

    def actualizar_interfaz_productos(self):
        """Actualiza la interfaz cuando cambian los productos"""
        self.cargar_productos()
        self.actualizar_resumen_inventario()

        # Limpiar búsqueda para ver todos los productos actualizados
        self.search_input.clear()
        self.buscar_producto()

    def buscar_producto(self):
        texto = self.search_input.text().lower().strip()
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            if not texto:
                item.setHidden(False)
            else:
                item.setHidden(texto not in item.text().lower())

    def agregar_producto(self):
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un producto de la lista.")
            return

        codigo = item.text().split(" - ")[0]
        
        # Obtener datos ACTUALIZADOS de la base de datos
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, precio, stock FROM productos WHERE codigo = ? AND activo = 1", (codigo,))
            producto = cursor.fetchone()
            
        if not producto:
            QMessageBox.warning(self, "Error", "Producto no encontrado o desactivado.")
            return
            
        nombre, precio, stock = producto
        
        if stock <= 0:
            QMessageBox.warning(self, "Error", "Producto sin stock disponible.")
            return

        cantidad, ok = QInputDialog.getInt(self, "Cantidad", f"Ingrese cantidad (Stock: {stock}):", 1, 1, stock)
        if not ok:
            return

        # VERIFICAR SI EL PRODUCTO YA ESTÁ EN EL CARRITO Y ACTUALIZARLO
        for item_carrito in self.carrito:
            if item_carrito['codigo'] == codigo:
                # Si el producto ya está en el carrito, actualizar con datos frescos
                nueva_cantidad_total = item_carrito['cantidad'] + cantidad
                
                if nueva_cantidad_total > stock:
                    QMessageBox.warning(self, "Error", 
                                    f"Stock insuficiente. Stock disponible: {stock}\n"
                                    f"Ya en carrito: {item_carrito['cantidad']}\n"
                                    f"Solicitado adicional: {cantidad}")
                    return
                
                # ACTUALIZAR con datos actualizados de la BD
                item_carrito['nombre'] = nombre
                item_carrito['precio'] = precio
                item_carrito['cantidad'] = nueva_cantidad_total
                self.actualizar_tabla()
                return

        # AGREGAR NUEVO PRODUCTO CON DATOS ACTUALIZADOS
        self.carrito.append({
            'codigo': codigo, 
            'nombre': nombre, 
            'precio': precio, 
            'cantidad': cantidad
        })
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
        total_formateado = formato_moneda_mx(total)
        self.total_label.setText(f"Total: {total_formateado}")

    def cancelar_venta(self):
        self.carrito = []
        self.actualizar_tabla()
        QMessageBox.information(self, "Venta cancelada", "Carrito vacío.")

    def enviar_ticket_por_email(self, ticket_path, venta_id, total):
        """Ofrece enviar ticket por email usando QThreadPool - VERSIÓN DEFINITIVA"""
        try:
            print("📧 Iniciando proceso de envío de email...")
            
            # Verificar si el email está configurado
            if not self.email_sender.config.get("habilitado", False):
                print("❌ Email no configurado, saliendo...")
                return
            
            respuesta = QMessageBox.question(
                self,
                "📧 Envío de Ticket",
                "¿Desea enviar el ticket por correo electrónico al cliente?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                email_cliente, ok = QInputDialog.getText(
                    self, 
                    "Email del Cliente",
                    "Ingrese el email del cliente:",
                    text=""
                )
                
                if ok and email_cliente.strip():
                    print(f"📧 Email del cliente: {email_cliente.strip()}")
                    
                    self.mostrar_progreso_email()
                    
                    try:
                        print("🔄 Creando worker de email...")
                        email_worker = self.email_sender.enviar_ticket_async(
                            ticket_path, 
                            email_cliente.strip(),
                            venta_id,
                            total,
                            self.config.get("nombre_negocio", "")
                        )
                        
                        print(f"✅ Worker obtenido: {email_worker}")
                        
                        if hasattr(email_worker, 'signals'):
                            # Es un worker de QThreadPool - conectar señales
                            print("✅ Conectando señales del worker...")
                            email_worker.signals.email_enviado.connect(self.procesar_resultado_email)
                            email_worker.signals.progreso.connect(self.actualizar_progreso_email)
                            
                            print("✅ Iniciando worker en ThreadPool...")
                            from PyQt6.QtCore import QThreadPool
                            QThreadPool.globalInstance().start(email_worker)
                            print("✅ Worker iniciado correctamente en ThreadPool")
                        else:
                            # Fallback al método sincrónico
                            print("⚠️ Usando método sincrónico como fallback")
                            resultado, mensaje = email_worker
                            self.ocultar_progreso_email()
                            QMessageBox.information(self, "Envío de Ticket", mensaje)
                            
                    except Exception as e:
                        print(f"❌ Error iniciando worker de email: {e}")
                        import traceback
                        traceback.print_exc()
                        self.ocultar_progreso_email()
                        QMessageBox.warning(self, "Error", f"No se pudo iniciar el envío: {str(e)}")
                        
        except Exception as e:
            print(f"❌ Error en envío de email: {e}")
            import traceback
            traceback.print_exc()
            self.ocultar_progreso_email()

    def mostrar_progreso_email(self):
        """Versión simplificada - solo mostrar en consola"""
        print("📧 Iniciando envío de email...")

    def actualizar_progreso_email(self, mensaje):
        """Solo mostrar en consola"""
        print(f"📧 {mensaje}")

    def ocultar_progreso_email(self):
        """No hacer nada en versión simplificada"""
        print("✅ Envío de email completado")

    def procesar_resultado_email(self, exito, mensaje):
        """Procesar resultado del envío de email - VERSIÓN SIMPLIFICADA"""
        print(f"📧 Resultado: {mensaje}")
        self.ocultar_progreso_email()
        QMessageBox.information(self, "Envío de Ticket", mensaje)

    def finalizar_venta(self):
        # VERIFICAR LICENCIA DEMO (código existente)
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
        
        # NUEVA VALIDACIÓN: VERIFICAR PRODUCTOS ACTUALIZADOS
        productos_problema = []
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            for item in self.carrito:
                cursor.execute("""
                    SELECT nombre, precio, stock, activo 
                    FROM productos 
                    WHERE codigo = ? AND activo = 1
                """, (item['codigo'],))
                resultado = cursor.fetchone()
                
                if not resultado:
                    productos_problema.append(f"{item['codigo']} - Producto no encontrado o desactivado")
                else:
                    nombre_actual, precio_actual, stock_actual, activo = resultado
                    # ACTUALIZAR DATOS EN TIEMPO REAL
                    if nombre_actual != item['nombre']:
                        productos_problema.append(f"{item['codigo']} - Producto actualizado: {item['nombre']} → {nombre_actual}")
                        item['nombre'] = nombre_actual  # Actualizar en carrito
                    
                    if precio_actual != item['precio']:
                        item['precio'] = precio_actual  # Actualizar precio
                    
                    if stock_actual < item['cantidad']:
                        productos_problema.append(f"{item['codigo']} - Stock insuficiente: {stock_actual} disponible, {item['cantidad']} solicitado")
        
        if productos_problema:
            QMessageBox.warning(self, "Productos Actualizados", 
                            "Se actualizaron algunos productos:\n\n" + 
                            "\n".join(productos_problema) +
                            "\n\n¿Desea continuar con la venta?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
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
                cursor.execute("SELECT id, stock FROM productos WHERE codigo = ? AND activo = 1", (item['codigo'],))
                resultado = cursor.fetchone()
                
                if not resultado:
                    QMessageBox.critical(self, "Error", f"Producto {item['codigo']} no encontrado")
                    conn.rollback()
                    return
                
                producto_id, stock_actual = resultado
                
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
        
        # REGISTRAR VENTA EN CONTADOR DEMO
        self.license_manager.registrar_venta()
        self.actualizar_resumen_ventas_hoy()
        
        # VERIFICAR LICENCIA
        if not self.license_manager.validar_licencia():
            if self.mostrar_opciones_licencia_expirada():
                print("✅ Licencia activada")
            else:
                QMessageBox.information(self, "Información", "La aplicación se cerrará.")
                self.close()
                return
            
        # OFRECER ENVÍO POR EMAIL
        self.enviar_ticket_por_email(ticket_path, venta_id, total)

    def actualizar_resumen_ventas_hoy(self):
        """Actualiza el resumen de ventas del día actual - VERSIÓN CORREGIDA"""
        try:
            # ✅ OBTENER FECHA ACTUAL en formato YYYY-MM-DD
            hoy = datetime.now().strftime("%Y-%m-%d")
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # ✅ CONSULTA CORREGIDA: Usar DATE() para comparar solo la fecha
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_ventas,
                        COALESCE(SUM(total), 0) as total_importe
                    FROM ventas 
                    WHERE DATE(fecha) = DATE(?)
                    AND estado = 'completada'
                """, (hoy,))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    count = resultado[0] or 0
                    total = resultado[1] or 0
                else:
                    count = 0
                    total = 0
                
                print(f"🔍 Resumen ventas hoy {hoy}: {count} ventas, ${total}")  # Para debug
            
            # ✅ ACTUALIZAR LA INTERFAZ
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
                    
        except Exception as e:
            print(f"❌ Error actualizando resumen ventas hoy: {e}")
            if hasattr(self, 'sales_today_summary') and self.sales_today_summary:
                self.sales_today_summary.setText(f"❌ Error cargando ventas: {str(e)}")
                
    def actualizar_resumen_inventario(self):
        """Actualiza el resumen de inventario"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo AND activo = 1")
                stock_bajo = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
                total_productos = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0 AND activo = 1")
                sin_stock = cursor.fetchone()[0] or 0
        
            if hasattr(self, 'inventory_summary') and self.inventory_summary:
                if total_productos > 0:
                    texto = f"""📊 RESUMEN DE INVENTARIO:
                    
    • 📦 Productos activos: {total_productos}
    • ⚠️  Productos con stock bajo: {stock_bajo}
    • 🔴 Productos sin stock: {sin_stock}

    """
                    if stock_bajo > 0 or sin_stock > 0:
                        texto += f"🔔 ALERTA: {stock_bajo + sin_stock} productos necesitan reposición"
                    else:
                        texto += "✅ Todo en orden - Inventario saludable"
                else:
                    texto = "📦 No hay productos en el inventario\n\n💡 Agregue productos desde 'Gestor de Inventario'"
                
                self.inventory_summary.setText(texto)
                    
        except Exception as e:
            if hasattr(self, 'inventory_summary') and self.inventory_summary:
                self.inventory_summary.setText("❌ Error cargando información de inventario")

    # ==== SISTEMA DE LICENCIAS MEJORADO ====

    def mostrar_estado_licencia(self):
        """Muestra estado de licencia"""
        try:
            from PyQt6.QtWidgets import QMessageBox, QPushButton
    
            info = self.license_manager.obtener_info_licencia()
            tipo_licencia = self.license_manager.tipo_licencia
        
            if info['estado'] == 'activa':
                if tipo_licencia == 'premium':
                    plan = info.get('plan', 'premium')
                    mensaje = f"💎 LICENCIA {plan.upper()} ACTIVA\n\n"
                    if plan == "perpetua":
                        mensaje += "• Licencia perpetua - Sin expiración\n"
                    elif plan == "anual":
                        mensaje += f"• Suscripción anual - {info['dias_restantes']} días restantes\n"
                    else:
                        mensaje += f"• {info['dias_restantes']} días restantes\n"
                    mensaje += "• Todas las funciones desbloqueadas\n• Soporte incluído"
                else:
                    mensaje = f"🔬 VERSIÓN DEMO ACTIVA\n\nVentas restantes: {info['dias_restantes']}\nLímite total: {self.license_manager.limite_ventas_demo} ventas"
            else:
                mensaje = "❌ LICENCIA EXPIRADA O NO VÁLIDA"
    
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Estado de Licencia")
            msg_box.setText(mensaje)
    
            btn_activar = QPushButton("🎫 Activar Licencia")
            btn_cerrar = QPushButton("Cerrar")
    
            msg_box.addButton(btn_activar, QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(btn_cerrar, QMessageBox.ButtonRole.RejectRole)
    
            msg_box.exec()
    
            boton_presionado = msg_box.clickedButton()
    
            if boton_presionado == btn_activar:
                self.mostrar_activacion()
        
        except Exception as e:
            QMessageBox.information(self, "Licencia", "Estado: Activada")

    def mostrar_activacion(self):
        """Muestra diálogo de activación"""
        try:
            from licenses.dialogo_activacion import DialogoActivacion
        
            tema_actual = self.config.get('tema', 'claro')
            dialogo = DialogoActivacion(self.license_manager, self, tema_actual)
        
            resultado = dialogo.exec()
        
            if resultado == QDialog.DialogCode.Accepted:
                if self.license_manager.validar_licencia():
                    info = self.license_manager.obtener_info_licencia()
                    QMessageBox.information(
                        self, 
                        "✅ Activación Exitosa",
                        f"Licencia {info.get('plan', 'premium')} activada correctamente!\n\n"
                        f"Válida por: {info['dias_restantes']} días\n"
                        f"Expira: {info['expiracion']}"
                    )
                else:
                    QMessageBox.warning(self, "Error", "La activación no fue exitosa")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", "No se pudo abrir el diálogo de activación")

    def mostrar_opciones_licencia_expirada(self):
        """Muestra opciones cuando la licencia demo expira"""
        from PyQt6.QtWidgets import QMessageBox, QPushButton
    
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Límite Demo Alcanzado")
        msg_box.setIcon(QMessageBox.Icon.Warning)
    
        mensaje = f"""
        ⚠️ HA ALCANZADO EL LÍMITE DE {self.license_manager.limite_ventas_demo} VENTAS
    
        La versión demo ha expirado. Para continuar usando el software:
    
        💎 **Opciones disponibles:**
        • Activar una licencia premium (uso ilimitado)
        • Contactar para adquirir una licencia
    
        📞 **Contacto:**
        📧 ventas@cajaregistradora.com
        📱 +52 55 1234 5678
        """
    
        msg_box.setText(mensaje)
    
        btn_activar = QPushButton("🎫 Activar Licencia Premium")
        btn_contacto = QPushButton("📞 Ver Información de Contacto")
        btn_cerrar = QPushButton("❌ Cerrar Aplicación")
    
        msg_box.addButton(btn_activar, QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(btn_contacto, QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(btn_cerrar, QMessageBox.ButtonRole.RejectRole)
    
        msg_box.exec()
    
        boton_presionado = msg_box.clickedButton()
    
        if boton_presionado == btn_activar:
            if self.mostrar_activacion():
                if self.license_manager.validar_licencia():
                    return True
                else:
                    return False
            else:
                return False
            
        elif boton_presionado == btn_contacto:
            self.mostrar_informacion_contacto()
            return self.mostrar_opciones_licencia_expirada()
        
        else:
            return False
        
    def mostrar_informacion_contacto(self):
        """Muestra información de contacto"""
        mensaje = """
        💎 **INFORMACIÓN DE CONTACTO - LICENCIAS PREMIUM**
    
        Para adquirir una licencia premium y desbloquear todas las funciones:
    
        📧 **Email:** ventas@cajaregistradora.com
        📱 **Teléfono:** +52 55 1234 5678
        🌐 **Sitio web:** www.cajaregistradora.com
    
        💰 **Planes disponibles:**
        • Licencia Perpetua: $2,800 MXN
        • Suscripción Anual: $1,500 MXN/año  
        • Plan Empresarial: $6,000 MXN
    
        ⏰ **Horario de atención:**
        Lunes a Viernes: 8:00 AM - 5:00 PM
        """
    
        QMessageBox.information(self, "Información de Contacto", mensaje)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CajaGUI()
    ventana.show()
    sys.exit(app.exec())