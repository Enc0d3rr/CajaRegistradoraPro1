import sys
import os
import atexit
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QMessageBox, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox, QLineEdit, QGroupBox, QDialog
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QTimer

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
from licencias_manager import LicenseManager

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

        # INICIALIZAR GESTOR DE LICENCIAS
        self.license_manager = LicenseManager()

        # VERIFICAR LICENCIA AL INICIAR 
        if not self.verificar_licencia():
            # Si la licencia no es válida, cerrar aplicación
            sys.exit(1)

        self.db_manager = DatabaseManager()
        self.carrito = []
        self.metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]

        # Registrar guardado al cerrar
        atexit.register(self.guardar_configuracion_al_cerrar)
        
        # Cargar y verificar configuración
        self.cargar_configuracion()
        self.guardar_configuracion_actualizada()

        # Autenticar usuario
        self.autenticar_usuario()
        
        if not hasattr(self, 'current_user'):
            print("❌ No se pudo autenticar usuario")
            sys.exit()

        print(f"✅ Usuario autenticado: {self.current_user['nombre']}")
            
        # Inicializar interfaz
        self.init_ui()
        self.aplicar_tema()

    def guardar_configuracion_actualizada(self):
        """Asegurar que la configuración tenga todas las claves necesarias"""
        try:
            if 'tema' not in self.config:
                self.config['tema'] = 'claro'
            config_manager.update_config(self.config)
            print("✅ Configuración actualizada guardada al iniciar")
        except Exception as e:
            print(f"❌ Error actualizando configuración: {e}")

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

    def autenticar_usuario(self):
        """Autenticar usuario usando LoginDialog"""
        try:
            print("🔐 Iniciando autenticación...")
            login_dialog = LoginDialog(self.db_manager)
            
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                self.current_user = {
                    "id": login_dialog.user_data['id'],
                    "username": login_dialog.user_data['nombre'],  
                    "nombre": login_dialog.user_data['nombre'],
                    "rol": login_dialog.user_data['rol']
                }
                print(f"✅ Login exitoso: {self.current_user['nombre']} ({self.current_user['rol']})")
            else:
                print("❌ Login cancelado")
                self.current_user = None
                self._login_emergencia()
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            self._login_emergencia()

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
        """Aplicar tema desde archivo themes.py"""
        tema = self.config.get('tema', 'claro')
        print(f"🎨 Aplicando tema: {tema}")
    
        try:
            estilo = obtener_tema(tema)
            self.setStyleSheet(estilo)
            self.update()
            self.repaint()
            print(f"✅ Tema {tema} aplicado correctamente")
        except Exception as e:
            print(f"❌ Error aplicando tema: {e}")

    def cargar_configuracion(self):
        """Cargar configuración desde archivo"""
        try:
            self.config = config_manager.load_config()
            if 'tema' not in self.config:
                self.config['tema'] = 'claro'
                config_manager.update_config(self.config)
                print("✅ Tema agregado por defecto")
            print(f"🎯 Tema configurado: {self.config['tema']}")
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            self.config = {"tema": "claro"}

    def abrir_panel_configuracion(self):
        """Abrir panel de configuración"""
        try:
            dialog = ConfigPanelDialog(self.db_manager, self.config, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                nuevo_config = dialog.get_updated_config()
                if nuevo_config:
                    self.config = nuevo_config
                    self.aplicar_tema()
                    QMessageBox.information(self, "Listo", "Cambios aplicados localmente")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir configuración: {str(e)}")

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
        self.inventory_summary = QLabel("Cargando información...")
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

                precio_formateado = formato_moneda_mx(item['precio'])

                cursor.execute("SELECT id FROM productos WHERE codigo = ?", (item['codigo'],))
                producto_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                              (venta_id, producto_id, item['cantidad'], item['precio'], item['precio'] * item['cantidad']))
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE codigo = ?", (item['cantidad'], item['codigo']))
            
            conn.commit()
        
        # Generar ticket
        ticket_path = generar_ticket(self.carrito, iva, total, metodo_pago, self.config.get("nombre_negocio", ""), venta_id)
        
        self.carrito = []
        self.actualizar_tabla()
        self.cargar_productos()
        
        total_formateado = formato_moneda_mx(total)
        QMessageBox.information(self, "Venta finalizada", 
                                f"Total: {total_formateado}\nMétodo: {metodo_pago}\nTicket: {ticket_path}")

    def actualizar_resumen_inventario(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo AND activo = 1")
            stock_bajo = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0 AND activo = 1")
            sin_stock = cursor.fetchone()[0]
    
        self.inventory_summary.setText(f"""📊 Resumen de Inventario:
• Productos activos: {total_productos}
• Productos con stock bajo: {stock_bajo}
• Productos sin stock: {sin_stock}

⚠️ Atención: {stock_bajo} productos necesitan reposición""")

    def actualizar_resumen_ventas_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
            count, total = cursor.fetchone()
            count = count or 0
            total = total or 0
        
        self.sales_today_summary.setText(f"""📊 VENTAS HOY ({hoy})
• Total ventas: {formato_moneda_mx(total)}
• N° de ventas: {count}""")

# ==== SECCION DE LICENSIA ===
    # caja_registradora.py - CORREGIR ESTE MÉTODO

    def verificar_licencia(self):
        """Verifica licencia premium - NO PRUEBAS AUTOMÁTICAS"""
        try:
            from PyQt6.QtWidgets import QDialog, QMessageBox
        
            print("🔍 Verificando licencia premium...")
        
            # Validar licencia (NO activará pruebas automáticas)
            if not self.license_manager.validar_licencia():
                print("❌ Licencia premium no válida o no activada.")
            
                # Mostrar diálogo de activación
                resultado = self.license_manager.mostrar_dialogo_activacion()
            
                # Si el usuario no activó la licencia, cerrar aplicación
                if resultado != QDialog.DialogCode.Accepted:
                    QMessageBox.warning(
                        self,
                        "Licencia Premium Requerida", 
                        "💎 Para usar el software necesitas una licencia premium válida.\n\n"
                        "📞 Contáctanos para adquirir tu licencia:\n"
                        "📧 ventas@cajaregistradora.com\n"
                        "📱 +52 55 1234 5678\n\n"
                        "La aplicación se cerrará."
                    )
                    return False
            
                # Verificar nuevamente después de la activación
                if not self.license_manager.validar_licencia():
                    QMessageBox.warning(self, "Error", "No se pudo activar la licencia.")
                    return False
        
            print("✅ Licencia premium válida.")
            info = self.license_manager.obtener_info_licencia()
            print(f"📊 Información de licencia: {info}")
        
            return True
        
        except Exception as e:
            print(f"❌ Error crítico en verificar_licencia: {e}")
            QMessageBox.critical(
                self,
                "Error del Sistema",
                f"Error al verificar la licencia:\n{str(e)}\n\n"
                "La aplicación se cerrará."
            )
            return False

    def mostrar_estado_licencia(self):
        """Muestra estado de licencia - VERSIÓN CORREGIDA"""
        try:
            from PyQt6.QtWidgets import QMessageBox, QPushButton
        
            info = self.license_manager.obtener_info_licencia()
            print(f"📊 Info licencia: {info}")
        
            # Crear mensaje según el tipo de licencia
            if info['estado'] == 'activa':
                if info['tipo'] == 'prueba':
                    mensaje = f"✅ LICENCIA DE PRUEBA ACTIVA\n\nDías restantes: {info['dias_restantes']}"
                elif info['tipo'] == 'paga':
                    mensaje = f"💎 LICENCIA PREMIUM ACTIVA\n\nDías restantes: {info['dias_restantes']}"
                else:
                    mensaje = f"📄 LICENCIA ACTIVA\n\nTipo: {info['tipo']}\nDías: {info['dias_restantes']}"
            else:
                mensaje = "❌ LICENCIA EXPIRADA O NO VÁLIDA"
        
            # CREAR MessageBox PERSONALIZADO
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Estado de Licencia")
            msg_box.setText(mensaje)
        
            # AÑADIR BOTONES PERSONALIZADOS
            btn_activar = QPushButton("🎫 Activar Licencia")
            btn_validar = QPushButton("🔄 Validar")
            btn_cerrar = QPushButton("Cerrar")
        
            msg_box.addButton(btn_activar, QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(btn_validar, QMessageBox.ButtonRole.ActionRole)
            msg_box.addButton(btn_cerrar, QMessageBox.ButtonRole.RejectRole)
        
            # EJECUTAR Y CAPTURAR RESPUESTA
            msg_box.exec()
        
            # VER QUÉ BOTÓN SE PRESIONÓ
            boton_presionado = msg_box.clickedButton()
        
            if boton_presionado == btn_activar:
                print("🎫 Usuario eligió: Activar Licencia")
                self.mostrar_activacion()
            elif boton_presionado == btn_validar:
                print("🔄 Usuario eligió: Validar")
                self.validar_licencia()
            else:
                print("❌ Usuario cerró el diálogo")
            
        except Exception as e:
            print(f"❌ Error en mostrar_estado_licencia: {e}")
            # FALLBACK SIMPLE
            QMessageBox.information(self, "Licencia", "Estado: Activada")

    def mostrar_activacion(self):
        """Muestra diálogo de activación - VERSIÓN CORREGIDA"""
        try:
            from dialogo_activacion import DialogoActivacion
            print("🎫 Abriendo diálogo de activación...")
        
            # PASAR SOLO LOS PARÁMETROS NECESARIOS
            dialogo = DialogoActivacion(self.license_manager, self)
            resultado = dialogo.exec()
        
            print(f"📝 Diálogo de activación cerrado. Resultado: {resultado}")
        
            # ACTUALIZAR ESTADO DESPUÉS DE LA ACTIVACIÓN
            if resultado == 1:  # Accepted
                info = self.license_manager.obtener_info_licencia()
                print(f"🎉 Licencia activada: {info}")
                QMessageBox.information(self, "✅ Éxito", "Licencia activada correctamente!")
            
        except Exception as e:
            print(f"❌ Error en mostrar_activacion: {e}")
            QMessageBox.warning(self, "Error", "No se pudo abrir el diálogo de activación")

    def validar_licencia(self):
        """Valida la licencia - VERSIÓN SIMPLE"""
        try:
            if self.license_manager.validar_licencia():
                QMessageBox.information(self, "✅ Válida", "La licencia es válida y activa.")
            else:
                QMessageBox.warning(self, "❌ Inválida", "La licencia no es válida.")
        except Exception as e:
            print(f"Error en validar_licencia: {e}")
            QMessageBox.warning(self, "Error", "Error al validar la licencia")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = CajaGUI()
    ventana.show()
    sys.exit(app.exec())