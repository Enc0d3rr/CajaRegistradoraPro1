import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QMessageBox, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox, QLineEdit, QGridLayout, QGroupBox, QTextEdit, QDialog
)
from PyQt6.QtGui import QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime

from database import DatabaseManager
from auth_manager import LoginDialog
from ticket_generator import generar_ticket
from user_manager import UserManagerDialog
from inventory_manager import InventoryManagerDialog
from cash_close_manager import CashCloseManagerDialog
from backup_manager import BackupManagerDialog
from category_manager import CategoryManagerDialog
from sales_history import SalesHistoryDialog
from password_dialog import PasswordDialog
from config_panel import ConfigPanelDialog
from config_manager import config_manager

class CajaGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        
        # Cargar configuración usando ConfigManager
        self.config = config_manager.load_config()
        if not self.config:
            QMessageBox.critical(None, "Error", "No se pudo cargar la configuración del sistema")
            sys.exit()
        
        # Autenticación
        self.show_login()
        
        if not hasattr(self, 'current_user'):
            sys.exit()
        
        self.init_ui()
    
    def show_login(self):
        login_dialog = LoginDialog(self.db_manager)
        if login_dialog.exec() == QDialog.DialogCode.Accepted:
            self.current_user = login_dialog.user_data
        else:
            QMessageBox.warning(None, "Error", "Debe iniciar sesión para usar el sistema")
            sys.exit()

    def gestionar_inventario(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar inventario")
            return
    
        dialog = InventoryManagerDialog(self.db_manager, self)
        dialog.exec()
        self.cargar_productos()  # Recargar productos después de cerrar el diálogo

    def gestionar_categorias(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar categorías")
            return
    
        dialog = CategoryManagerDialog(self.db_manager, self)
        dialog.exec()

    def gestionar_cierres(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar cierres de caja")
            return
    
        dialog = CashCloseManagerDialog(self.db_manager, self.current_user, self)
        dialog.exec()

    def gestionar_backups(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar backups")
            return
    
        dialog = BackupManagerDialog(self.db_manager, self)
        dialog.exec()

    def ver_historial_ventas(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden ver el historial de ventas")
            return
    
        dialog = SalesHistoryDialog(self.db_manager, self)
        dialog.exec()

    def abrir_panel_configuracion(self):
        """Abrir panel de configuración completo"""
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden acceder a la configuración")
            return
    
        from config_panel import ConfigPanelDialog
        dialog = ConfigPanelDialog(self.db_manager, self.config, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Actualizar configuración y reiniciar interfaz
            self.config = dialog.get_updated_config()
            QMessageBox.information(self, "Éxito", "Configuración guardada. Reiniciando interfaz...")
            self.reiniciar_interfaz()

    def reiniciar_interfaz(self):
        """Reiniciar la interfaz con nueva configuración"""
        self.close()
        # Pequeña pausa para asegurar que la ventana se cierra
        import time
        time.sleep(0.5)
        # Reabrir la aplicación
        self.__init__()
        self.show()
    
    def init_ui(self):
        # === Configuración ya cargada en __init__ con ConfigManager ===
        
        self.carrito = []
        self.metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]
        
        # === Configurar ventana principal ===
        self.setWindowTitle(f"{self.config.get('nombre_negocio', 'Caja Registradora')} - Usuario: {self.current_user['nombre']}")
        self.setGeometry(100, 50, 1000, 800)

        # Aplicar color de fondo
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.config["color_primario"]))
        self.setPalette(palette)

        main_layout = QVBoxLayout()

        # === Header ===
        header_layout = QHBoxLayout()
        
        # Logo o nombre del negocio - CORREGIDO
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumSize(100, 100)
        logo_label.setMaximumSize(100, 100)

        # DEBUG: Ver qué hay en la configuración
        print(f"🔍 Config: {self.config}")

        logo_path = self.config.get("logo_path", "")
        nombre_negocio = self.config.get("nombre_negocio", "").strip()

        print(f"📁 Logo path: {logo_path}")
        print(f"🏪 Nombre negocio: {nombre_negocio}")

        # Si hay logo intentar cargarlo
        if logo_path:
            try:
                logo_full_path = os.path.join("data", logo_path)
                print(f"📂 Intentando cargar: {logo_full_path}")
                print(f"📂 Existe archivo: {os.path.exists(logo_full_path)}")
        
                if os.path.exists(logo_full_path):
                    pixmap = QPixmap(logo_full_path)
                    if not pixmap.isNull():
                        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        print("✅ Logo cargado exitosamente")
                        logo_label.setStyleSheet("border: 2px solid #ffffff; border-radius: 5px;")
                    else:
                        print("❌ El archivo de logo no es una imagen válida")
                        logo_label.setText(nombre_negocio or "Caja\nRegistradora")
                        logo_label.setStyleSheet("""
                            font-size: 14px; 
                            font-weight: bold; 
                            color: white;
                            background-color: rgba(0,0,0,0.3);
                            padding: 5px;
                            border-radius: 5px;
                            border: 1px solid #ffffff;
                        """)
                else:
                    print("❌ El archivo de logo no existe")
                    logo_label.setText(nombre_negocio or "Caja\nRegistradora")
                    logo_label.setStyleSheet("""
                        font-size: 14px; 
                        font-weight: bold; 
                        color: white;
                        background-color: rgba(0,0,0,0.3);
                        padding: 5px;
                        border-radius: 5px;
                    """)
            except Exception as e:
                print(f"❌ Error cargando logo: {e}")
                logo_label.setText(nombre_negocio or "Caja\nRegistradora")
                logo_label.setStyleSheet("""
                    font-size: 14px; 
                    font-weight: bold; 
                    color: white;
                    background-color: rgba(0,0,0,0.3);
                    padding: 5px;
                    border-radius: 5px;
                """)
        else:
            print("ℹ️ No hay logo configurado")
            logo_label.setText(nombre_negocio or "Caja\nRegistradora")
            logo_label.setStyleSheet("""
                font-size: 14px; 
                font-weight: bold; 
                color: white;
                background-color: rgba(0,0,0,0.3);
                padding: 5px;
                border-radius: 5px;
            """)

        # ✅ AGREGAR LOGO AL LAYOUT
        header_layout.addWidget(logo_label)
        print("✅ Logo label agregado al layout")

        # ✅ ESPACIO FLEXIBLE
        header_layout.addStretch(1)

        # Info usuario y hora
        user_info = QLabel(f"Usuario: {self.current_user['nombre']}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        user_info.setStyleSheet("""
            color: white; 
            font-size: 12px; 
            background-color: rgba(0,0,0,0.3); 
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #ffffff;
        """)
        header_layout.addWidget(user_info)

        # ✅ ESPACIO FLEXIBLE
        header_layout.addStretch(1)

        # Panel de configuración (solo admin) - ✅ CORREGIDO
        if self.current_user['rol'] == 'admin':
            btn_config = QPushButton("⚙️ Panel Configuración")
            btn_config.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6; 
                    color: white; 
                    font-weight: bold; 
                    padding: 10px;
                    border: 2px solid #ffffff;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
                QPushButton:pressed {
                    background-color: #6c3483;
                }
            """)
            btn_config.clicked.connect(self.abrir_panel_configuracion)
            header_layout.addWidget(btn_config)
            print("✅ Botón de configuración agregado (admin)")
        
        # Actualizar hora cada segundo
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: user_info.setText(
            f"Usuario: {self.current_user['nombre']}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ))
        self.timer.start(1000)
        
        main_layout.addLayout(header_layout)

        # === Sistema de pestañas ===
        self.tabs = QTabWidget()
        
        # Pestaña de ventas
        ventas_tab = QWidget()
        ventas_layout = QVBoxLayout()
        self.setup_ventas_tab(ventas_layout)
        ventas_tab.setLayout(ventas_layout)
        self.tabs.addTab(ventas_tab, "Ventas")
        
        # Pestaña de inventario (solo admin)
        if self.current_user['rol'] == 'admin':
            inventario_tab = QWidget()
            inventario_layout = QVBoxLayout()
            self.setup_inventario_tab(inventario_layout)
            inventario_tab.setLayout(inventario_layout)
            self.tabs.addTab(inventario_tab, "Inventario")
            
            # Pestaña de reportes
            reportes_tab = QWidget()
            reportes_layout = QVBoxLayout()
            self.setup_reportes_tab(reportes_layout)
            reportes_tab.setLayout(reportes_layout)
            self.tabs.addTab(reportes_tab, "Reportes")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        
        self.cargar_productos()

    def setup_ventas_tab(self, layout):
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
        
        btn_agregar = QPushButton("Agregar producto")
        btn_agregar.setStyleSheet(f"background-color: {self.config['color_secundario']}; color: white; font-weight: bold;")
        btn_agregar.clicked.connect(self.agregar_producto)
        botones_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar producto")
        btn_eliminar.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_eliminar.clicked.connect(self.eliminar_producto)
        botones_layout.addWidget(btn_eliminar)

        btn_finalizar = QPushButton("Finalizar venta")
        btn_finalizar.setStyleSheet(f"background-color: {self.config['color_secundario']}; color: white; font-weight: bold;")
        btn_finalizar.clicked.connect(self.finalizar_venta)
        botones_layout.addWidget(btn_finalizar)

        btn_cancelar = QPushButton("Cancelar venta")
        btn_cancelar.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_cancelar.clicked.connect(self.cancelar_venta)
        botones_layout.addWidget(btn_cancelar)

        layout.addLayout(botones_layout)

        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Código", "Producto", "Precio", "Cantidad", "Subtotal"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_carrito)

        # Total y método de pago
        footer_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: $ 0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        footer_layout.addWidget(self.total_label)
        
        footer_layout.addWidget(QLabel("Método de pago:"))
        self.metodo_pago_combo = QComboBox()
        self.metodo_pago_combo.addItems(self.metodos_pago)
        footer_layout.addWidget(self.metodo_pago_combo)
        
        layout.addLayout(footer_layout)

    def setup_inventario_tab(self, layout):
        # Layout de botones superiores
        top_buttons = QHBoxLayout()
    
        btn_abrir_inventario = QPushButton("📦 Gestor de Inventario")
        btn_abrir_inventario.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        btn_abrir_inventario.clicked.connect(self.gestionar_inventario)
        top_buttons.addWidget(btn_abrir_inventario)
    
        btn_categorias = QPushButton("🏷️ Gestor de Categorías")
        btn_categorias.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        btn_categorias.clicked.connect(self.gestionar_categorias)
        top_buttons.addWidget(btn_categorias)

        layout.addLayout(top_buttons)
    
    # Información de resumen
        summary_group = QGroupBox("Resumen de Inventario")
        summary_layout = QVBoxLayout()
    
        self.inventory_summary = QLabel("Cargando información...")
        self.inventory_summary.setStyleSheet("font-size: 12px;")
        summary_layout.addWidget(self.inventory_summary)
    
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
    
        self.actualizar_resumen_inventario()

    def actualizar_resumen_inventario(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Productos con stock bajo
            cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo AND activo = 1")
            stock_bajo = cursor.fetchone()[0]
        
            # Total de productos
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()[0]
        
            # Productos sin stock
            cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0 AND activo = 1")
            sin_stock = cursor.fetchone()[0]
    
        summary_text = f"""
        📊 Resumen de Inventario:
        • Productos activos: {total_productos}
        • Productos con stock bajo: {stock_bajo}
        • Productos sin stock: {sin_stock}
    
        ⚠️ Atención: {stock_bajo} productos necesitan reposición
    """
    
        self.inventory_summary.setText(summary_text)

    def setup_reportes_tab(self, layout):
        # Layout de botones superiores
        top_buttons = QHBoxLayout()
    
        btn_abrir_reportes = QPushButton("📊 Cierres de Caja")
        btn_abrir_reportes.setStyleSheet("background-color: #16a085; color: white; font-weight: bold;")
        btn_abrir_reportes.clicked.connect(self.gestionar_cierres)
        top_buttons.addWidget(btn_abrir_reportes)
    
        btn_backups = QPushButton("💾 Sistema de Backup")
        btn_backups.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        btn_backups.clicked.connect(self.gestionar_backups)
        top_buttons.addWidget(btn_backups)

        btn_historial = QPushButton("📈 Historial de Ventas")
        btn_historial.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        btn_historial.clicked.connect(self.ver_historial_ventas)
        top_buttons.addWidget(btn_historial)
    
        layout.addLayout(top_buttons)
    
        # Información de resumen de ventas
        sales_group = QGroupBox("Resumen de Ventas Hoy")
        sales_layout = QVBoxLayout()
    
        self.sales_today_summary = QLabel("Cargando información...")
        self.sales_today_summary.setStyleSheet("font-size: 12px;")
        sales_layout.addWidget(self.sales_today_summary)

        sales_group.setLayout(sales_layout)
        layout.addWidget(sales_group)
    
        self.actualizar_resumen_ventas_hoy()

    def actualizar_resumen_ventas_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Ventas de hoy
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
            count, total = cursor.fetchone()
            count = count or 0
            total = total or 0
        
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, SUM(total) 
                FROM ventas 
                WHERE DATE(fecha) = ?
                GROUP BY metodo_pago
            """, (hoy,))
        
            metodos_pago = {}
            for metodo, total_metodo in cursor.fetchall():
                metodos_pago[metodo] = total_metodo or 0
    
        summary_text = f"""
        📊 VENTAS HOY ({hoy})
        • Total ventas: ${total:.2f}
        • N° de ventas: {count}
        • Efectivo: ${metodos_pago.get('Efectivo', 0):.2f}
        • Tarjeta: ${metodos_pago.get('Tarjeta', 0):.2f}
        • Transferencia: ${metodos_pago.get('Transferencia', 0):.2f}
        """
    
        self.sales_today_summary.setText(summary_text)

    def cargar_productos(self):
        self.lista.clear()
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE activo = 1 ORDER BY nombre")
            productos = cursor.fetchall()
            
            for codigo, nombre, precio, stock in productos:
                item_text = f"{codigo} - {nombre} - $ {precio:.2f} - Stock: {stock}"
                self.lista.addItem(item_text)

    def buscar_producto(self):
        if hasattr(self, 'search_input') and self.search_input:
            texto = self.search_input.text().lower()
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            if texto and texto in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def agregar_producto(self):
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un producto de la lista.")
            return

        codigo = item.text().split(" - ")[0]
        
        # Verificar stock
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

        cantidad, ok = QInputDialog.getInt(
            self, "Cantidad", f"Ingrese cantidad (Stock disponible: {stock}):", 
            1, 1, stock
        )
        if not ok:
            return

        # Verificar si ya está en el carrito
        for item in self.carrito:
            if item['codigo'] == codigo:
                item['cantidad'] += cantidad
                self.actualizar_tabla()
                return

        # Agregar nuevo producto
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
            QMessageBox.warning(self, "Eliminar producto", "Seleccione un producto del carrito para eliminar.")

    def calcular_total(self):
        return sum(item['precio'] * item['cantidad'] for item in self.carrito)

    def actualizar_tabla(self):
        self.tabla_carrito.setRowCount(0)
        for item in self.carrito:
            row = self.tabla_carrito.rowCount()
            self.tabla_carrito.insertRow(row)
            self.tabla_carrito.setItem(row, 0, QTableWidgetItem(item['codigo']))
            self.tabla_carrito.setItem(row, 1, QTableWidgetItem(item['nombre']))
            self.tabla_carrito.setItem(row, 2, QTableWidgetItem(f"$ {item['precio']:.2f}"))
            self.tabla_carrito.setItem(row, 3, QTableWidgetItem(str(item['cantidad'])))
            subtotal = item['precio'] * item['cantidad']
            self.tabla_carrito.setItem(row, 4, QTableWidgetItem(f"$ {subtotal:.2f}"))

        iva = self.config.get("iva", 0.18)
        total = self.calcular_total() * (1 + iva)
        self.total_label.setText(f"Total: $ {total:.2f}")

    def cancelar_venta(self):
        self.carrito = []
        self.actualizar_tabla()
        QMessageBox.information(self, "Venta cancelada", "🛑 Carrito vacío.")

    def finalizar_venta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Atención", "⚠️ No hay productos en el carrito.")
            return
        
        iva = self.config.get("iva", 0.18)
        total = self.calcular_total() * (1 + iva)
        metodo_pago = self.metodo_pago_combo.currentText()
        
        # Guardar venta en base de datos
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insertar venta
            cursor.execute(
                "INSERT INTO ventas (total, iva, metodo_pago, usuario_id) VALUES (?, ?, ?, ?)",
                (total, iva, metodo_pago, self.current_user['id'])
            )
            venta_id = cursor.lastrowid
            
            # Insertar detalles de venta y actualizar stock
            for item in self.carrito:
                # Obtener ID del producto
                cursor.execute("SELECT id FROM productos WHERE codigo = ?", (item['codigo'],))
                producto_id = cursor.fetchone()[0]
                
                cursor.execute(
                    "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (venta_id, producto_id, item['cantidad'], item['precio'], item['precio'] * item['cantidad'])
                )
                
                # Actualizar stock
                cursor.execute(
                    "UPDATE productos SET stock = stock - ? WHERE codigo = ?",
                    (item['cantidad'], item['codigo'])
                )
            
            conn.commit()
        
        # Generar ticket
        ticket_path = generar_ticket(
            self.carrito, 
            iva, 
            total,
            metodo_pago,
            self.config.get("nombre_negocio", ""),
            venta_id
        )
        
        self.carrito = []
        self.actualizar_tabla()
        self.cargar_productos()  # Actualizar lista de productos
        
        QMessageBox.information(
            self, 
            "Venta finalizada", 
            f"🧾 Total a pagar: $ {total:.2f}\nMétodo: {metodo_pago}\n\nTicket guardado en:\n{ticket_path}"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CajaGUI()
    window.show()
    sys.exit(app.exec())