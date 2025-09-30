from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QComboBox, QGroupBox, QTextEdit, QTabWidget,
    QApplication, QLineEdit, QCheckBox, QWidget, QSizePolicy
)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QDate, QTimer
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from export_dialog import ExportDialog
from utils.helpers import formato_moneda_mx

class SalesHistoryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Historial y Análisis de Ventas")
        self.setGeometry(100, 50, 1200, 800)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#f8f9fa"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Filtros de fecha
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Desde:"))
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)
        
        filter_layout.addWidget(QLabel("Método:"))
        self.combo_metodo = QComboBox()
        self.combo_metodo.addItems(["Todos", "Efectivo", "Tarjeta", "Transferencia"])
        filter_layout.addWidget(self.combo_metodo)
        
        filter_layout.addWidget(QLabel("Usuario:"))
        self.combo_usuario = QComboBox()
        self.combo_usuario.addItem("Todos")
        filter_layout.addWidget(self.combo_usuario)
        
        # Boton Filtrar
        btn_filter = QPushButton("🔍 Filtrar")
        btn_filter.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_filter.setFixedHeight(30)
        btn_filter.clicked.connect(self.cargar_ventas)
        filter_layout.addWidget(btn_filter)
        
        # Boton Exportar Reporte
        btn_export = QPushButton("📊 Exportar")
        btn_export.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6; 
                color: white; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        btn_export.setFixedHeight(30)  
        btn_export.clicked.connect(self.exportar_reporte)
        filter_layout.addWidget(btn_export)

        layout.addLayout(filter_layout)
        
        # Pestañas
        self.tabs = QTabWidget()
        
        # Pestaña de ventas detalladas
        sales_tab = QWidget()
        sales_layout = QVBoxLayout()
        self.setup_sales_tab(sales_layout)
        sales_tab.setLayout(sales_layout)
        self.tabs.addTab(sales_tab, "Ventas Detalladas")
        
        # Pestaña de análisis
        analysis_tab = QWidget()
        analysis_layout = QVBoxLayout()
        self.setup_analysis_tab(analysis_layout)
        analysis_tab.setLayout(analysis_layout)
        self.tabs.addTab(analysis_tab, "Análisis")
        
        # Pestaña de productos
        products_tab = QWidget()
        products_layout = QVBoxLayout()
        self.setup_products_tab(products_layout)
        products_tab.setLayout(products_layout)
        self.tabs.addTab(products_tab, "Productos")
        
        layout.addWidget(self.tabs)
        
        # Resumen general
        summary_group = QGroupBox("Resumen General")
        summary_layout = QHBoxLayout()
        
        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("font-size: 12px; padding: 10px;")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        summary_layout.addWidget(self.summary_label)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)
        
        self.cargar_usuarios()
        self.cargar_ventas()
    
    def cargar_usuarios(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM usuarios WHERE activo = 1 ORDER BY nombre")
            usuarios = cursor.fetchall()
            
            for id_, nombre in usuarios:
                self.combo_usuario.addItem(f"{nombre} ({id_})", id_)
    
    def setup_sales_tab(self, layout):
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Fecha", "Total", "IVA", "Método", "Usuario", "Productos"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.sales_table.doubleClicked.connect(self.mostrar_detalle_venta)
        layout.addWidget(self.sales_table)
    
    def setup_analysis_tab(self, layout):
        """Configurar pestaña de análisis con layout mejorado"""
        # Gráficos - Usar un layout más flexible
        charts_layout = QHBoxLayout()
        
        # Contenedor para gráfico 1
        chart1_container = QWidget()
        chart1_layout = QVBoxLayout(chart1_container)
        
        chart1_group = QGroupBox("Ventas por Día")
        chart1_group_layout = QVBoxLayout()
        
        # CONFIGURACIÓN MEJORADA - Canvas más grande
        self.figure1 = Figure(figsize=(5, 4), dpi=100)
        self.canvas1 = FigureCanvas(self.figure1)
        self.canvas1.setMinimumSize(450, 350)
        self.canvas1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        chart1_group_layout.addWidget(self.canvas1)
        chart1_group.setLayout(chart1_group_layout)
        chart1_layout.addWidget(chart1_group)
        
        charts_layout.addWidget(chart1_container)
        
        # Contenedor para gráfico 2
        chart2_container = QWidget()
        chart2_layout = QVBoxLayout(chart2_container)
        
        chart2_group = QGroupBox("Métodos de Pago")
        chart2_group_layout = QVBoxLayout()
        
        # ✅ CONFIGURACIÓN MEJORADA
        self.figure2 = Figure(figsize=(5, 4), dpi=100)
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas2.setMinimumSize(450, 350)
        self.canvas2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        chart2_group_layout.addWidget(self.canvas2)
        chart2_group.setLayout(chart2_group_layout)
        chart2_layout.addWidget(chart2_group)
        
        charts_layout.addWidget(chart2_container)
        
        # ✅ AÑADIR ESTRECHAJE PARA MEJOR DISTRIBUCIÓN
        charts_layout.setStretch(0, 1)
        charts_layout.setStretch(1, 1)
        
        layout.addLayout(charts_layout)
    
    def setup_products_tab(self, layout):
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["Producto", "Categoría", "Vendidos", "Total", "Última Venta", "Tendencia"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.products_table)
    
    def cargar_ventas(self):
        fecha_desde = self.date_from.date().toString("yyyy-MM-dd")
        fecha_hasta = self.date_to.date().toString("yyyy-MM-dd 23:59:59")
        metodo = self.combo_metodo.currentText()
        usuario_info = self.combo_usuario.currentData()
        
        query = """
            SELECT v.id, v.fecha, v.total, v.iva, v.metodo_pago, u.nombre,
                   (SELECT COUNT(*) FROM detalle_ventas dv WHERE dv.venta_id = v.id) as num_productos
            FROM ventas v 
            JOIN usuarios u ON v.usuario_id = u.id 
            WHERE v.fecha BETWEEN ? AND ?
        """
        params = [fecha_desde, fecha_hasta]
        
        if metodo != "Todos":
            query += " AND v.metodo_pago = ?"
            params.append(metodo)
        
        if usuario_info:
            query += " AND v.usuario_id = ?"
            params.append(usuario_info)
        
        query += " ORDER BY v.fecha DESC"
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            ventas = cursor.fetchall()
            
            self.sales_table.setRowCount(len(ventas))
            for row, (id_, fecha, total, iva, metodo_pago, usuario, num_productos) in enumerate(ventas):
                self.sales_table.setItem(row, 0, QTableWidgetItem(str(id_)))
                self.sales_table.setItem(row, 1, QTableWidgetItem(fecha))

                self.sales_table.setItem(row, 2, QTableWidgetItem(formato_moneda_mx(total)))
                self.sales_table.setItem(row, 3, QTableWidgetItem(formato_moneda_mx(iva)))

                self.sales_table.setItem(row, 4, QTableWidgetItem(metodo_pago))
                self.sales_table.setItem(row, 5, QTableWidgetItem(usuario))
                self.sales_table.setItem(row, 6, QTableWidgetItem(str(num_productos)))
            
            # Calcular resumen
            cursor.execute("SELECT SUM(total), SUM(iva), COUNT(*) FROM ventas WHERE fecha BETWEEN ? AND ?", 
                          (fecha_desde, fecha_hasta))
            total_ventas, total_iva, num_ventas = cursor.fetchone()
            total_ventas = total_ventas or 0
            total_iva = total_iva or 0
            num_ventas = num_ventas or 0
            
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, SUM(total), COUNT(*) 
                FROM ventas 
                WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
            """, (fecha_desde, fecha_hasta))
            
            metodos_text = ""
            for metodo, total, count in cursor.fetchall():
                metodos_text += f"{metodo}: {formato_moneda_mx(total)} ({count} ventas)\n"
            
            self.summary_label.setText(
                f"📊 PERIODO: {fecha_desde} a {fecha_hasta.split()[0]}\n"
                f"💰 TOTAL VENTAS: {formato_moneda_mx(total_ventas)}\n"
                f"📈 TOTAL IVA: {formato_moneda_mx(total_iva)}\n"
                f"🛒 N° VENTAS: {num_ventas}\n"
                f"💳 MÉTODOS DE PAGO:\n{metodos_text}"
            )
            
            self.generar_graficos(fecha_desde, fecha_hasta)
            self.cargar_productos_vendidos(fecha_desde, fecha_hasta)
            self.generar_graficos(fecha_desde, fecha_hasta)
    
    def generar_graficos(self, fecha_desde, fecha_hasta):
        """Genera gráficas - VERSIÓN DEFINITIVA CORREGIDA"""
        try:
            print(f"📊 Generando gráficas para {fecha_desde} a {fecha_hasta}")
            
            # GRÁFICO 1: Ventas por día
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DATE(fecha), COALESCE(SUM(total), 0), COUNT(*)
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                    GROUP BY DATE(fecha)
                    ORDER BY DATE(fecha)
                """, (fecha_desde, fecha_hasta))
                
                datos = cursor.fetchall()
                fechas = [d[0] for d in datos]
                totales = [d[1] for d in datos]
        
            # CONFIGURACIÓN ROBUSTA GRÁFICO 1
            self.figure1.clear()
            self.figure1.set_size_inches(6, 4)
            self.figure1.subplots_adjust(left=0.15, right=0.95, top=0.90, bottom=0.25)
            
            ax1 = self.figure1.add_subplot(111)
            
            if datos and any(totales):
                # Simplificar fechas para mejor visualización
                fechas_simplificadas = []
                for fecha in fechas:
                    if isinstance(fecha, str) and len(fecha) > 10:
                        fechas_simplificadas.append(fecha[5:10])  # MM-DD
                    else:
                        fechas_simplificadas.append(str(fecha))
                
                # Crear gráfico de barras
                bars = ax1.bar(range(len(fechas)), totales, color='#3498db', alpha=0.7, width=0.6)
                ax1.set_title('Ventas por Día', fontsize=12, fontweight='bold', pad=15)
                ax1.set_xlabel('Fecha', fontsize=10, labelpad=10)
                ax1.set_ylabel('Total Ventas ($)', fontsize=10, labelpad=10)
                
                # Configurar eje X
                ax1.set_xticks(range(len(fechas)))
                ax1.set_xticklabels(fechas_simplificadas, rotation=45, ha='right', fontsize=8)
                
                # Ajustar límites
                max_val = max(totales) if totales else 1
                ax1.set_ylim(0, max_val * 1.15)
                ax1.grid(True, alpha=0.2, axis='y')
                
                # Agregar valores en las barras
                for i, bar in enumerate(bars):
                    height = bar.get_height()
                    if height > 0:
                        ax1.text(bar.get_x() + bar.get_width()/2., height + max_val*0.01,
                                formato_moneda_mx(height).replace('$', ''), 
                                ha='center', va='bottom', fontsize=8)
            else:
                # ✅ MENSAJE MEJORADO cuando no hay datos
                ax1.text(0.5, 0.5, 'No hay ventas registradas\npara el período seleccionado', 
                        ha='center', va='center', transform=ax1.transAxes, fontsize=12,
                        style='italic', color='gray')
                ax1.set_title('Ventas por Día', fontsize=12, fontweight='bold')
                ax1.set_xticks([])
                ax1.set_yticks([])
            
            # ACTUALIZAR CANVAS 1
            self.canvas1.draw()
            
            # GRÁFICO 2: Métodos de pago
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT metodo_pago, COALESCE(SUM(total), 0), COUNT(*)
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                    GROUP BY metodo_pago
                """, (fecha_desde, fecha_hasta))
                
                metodos_data = cursor.fetchall()
        
            # CONFIGURACIÓN ROBUSTA GRÁFICO 2
            self.figure2.clear()
            self.figure2.set_size_inches(6, 4)
            self.figure2.subplots_adjust(left=0.05, right=0.85, top=0.90, bottom=0.1)
            
            ax2 = self.figure2.add_subplot(111)
            
            if metodos_data and any(d[1] > 0 for d in metodos_data):
                metodos = [d[0] for d in metodos_data]
                totals = [d[1] for d in metodos_data]
                colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12']
                
                # Gráfico de pastel
                wedges, texts, autotexts = ax2.pie(
                    totals, 
                    labels=metodos, 
                    autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
                    colors=colors[:len(totals)],
                    startangle=90,
                    textprops={'fontsize': 9}
                )
                
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
                    autotext.set_fontsize(9)
                
                ax2.axis('equal')
                ax2.set_title('Métodos de Pago', fontsize=12, fontweight='bold', pad=15)
                
            else:
                # MENSAJE MEJORADO cuando no hay datos
                ax2.text(0.5, 0.5, 'No hay ventas registradas\npara el período seleccionado', 
                        ha='center', va='center', transform=ax2.transAxes, fontsize=12,
                        style='italic', color='gray')
                ax2.set_title('Métodos de Pago', fontsize=12, fontweight='bold')
            
            # ✅ ACTUALIZAR CANVAS 2
            self.canvas2.draw()
            
            print("✅ Gráficas generadas exitosamente")
            
        except Exception as e:
            print(f"❌ Error generando gráficos: {e}")
            # MOSTRAR ERROR EN LAS GRÁFICAS
            self.mostrar_error_graficas(str(e))

    def mostrar_error_graficas(self, mensaje_error):
        """Muestra mensaje de error en las gráficas"""
        try:
            self.figure1.clear()
            ax1 = self.figure1.add_subplot(111)
            ax1.text(0.5, 0.5, f'Error cargando gráficas:\n{mensaje_error}', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=10,
                    color='red')
            self.canvas1.draw()
            
            self.figure2.clear()
            ax2 = self.figure2.add_subplot(111)
            ax2.text(0.5, 0.5, f'Error cargando gráficas:\n{mensaje_error}', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=10,
                    color='red')
            self.canvas2.draw()
        except:
            pass

    def mostrarEvent(self, event):
        """Se ejecuta cuando la pestaña se muestra"""
        super().showEvent(event)
        # FORZAR REDIBUJADO CUANDO SE MUESTRA LA PESTAÑA
        if hasattr(self, 'canvas1') and hasattr(self, 'canvas2'):
            self.canvas1.update()
            self.canvas2.update()
            QTimer.singleShot(100, self.actualizar_graficos)

    def actualizar_graficos(self):
        """Forzar actualización de gráficos"""
        if hasattr(self, 'canvas1'):
            self.canvas1.draw()
        if hasattr(self, 'canvas2'):
            self.canvas2.draw()
    
    def cargar_productos_vendidos(self, fecha_desde, fecha_hasta):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nombre, c.nombre, SUM(dv.cantidad), SUM(dv.subtotal), MAX(v.fecha),
                       (SELECT SUM(dv2.cantidad) FROM detalle_ventas dv2 
                        JOIN ventas v2 ON dv2.venta_id = v2.id 
                        WHERE dv2.producto_id = p.id AND v2.fecha BETWEEN ? AND DATE(?, '-7 days'))
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                JOIN categorias c ON p.categoria_id = c.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE v.fecha BETWEEN ? AND ?
                GROUP BY p.id
                ORDER BY SUM(dv.subtotal) DESC
            """, (fecha_desde, fecha_hasta, fecha_desde, fecha_hasta))
            
            productos = cursor.fetchall()
            
            self.products_table.setRowCount(len(productos))
            for row, (nombre, categoria, cantidad, total, ultima_venta, venta_anterior) in enumerate(productos):
                self.products_table.setItem(row, 0, QTableWidgetItem(nombre))
                self.products_table.setItem(row, 1, QTableWidgetItem(categoria))
                self.products_table.setItem(row, 2, QTableWidgetItem(str(int(cantidad))))

                self.products_table.setItem(row, 3, QTableWidgetItem(formato_moneda_mx(total)))
                self.products_table.setItem(row, 4, QTableWidgetItem(ultima_venta.split()[0]))
                
                # Calcular tendencia
                if venta_anterior and cantidad:
                    tendencia = (cantidad - venta_anterior) / venta_anterior * 100
                    tendencia_text = f"{tendencia:+.1f}%"
                    self.products_table.setItem(row, 5, QTableWidgetItem(tendencia_text))
                else:
                    self.products_table.setItem(row, 5, QTableWidgetItem("N/A"))
    
    def mostrar_detalle_venta(self, index):
        venta_id = self.sales_table.item(index.row(), 0).text()
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.nombre, dv.cantidad, dv.precio_unitario, dv.subtotal
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id
                WHERE dv.venta_id = ?
            """, (venta_id,))
            
            detalle = cursor.fetchall()
            
            detalle_text = f"Detalle de Venta #{venta_id}:\n\n"
            for nombre, cantidad, precio, subtotal in detalle:
                detalle_text += f"{nombre} x{cantidad} - {formato_moneda_mx(precio)} = {formato_moneda_mx(subtotal)}\n"
            
            QMessageBox.information(self, "Detalle de Venta", detalle_text)
    
    # Exportar reporte
    def exportar_reporte(self):
        """Abre el diálogo de exportación para ventas - VERSIÓN CORREGIDA"""
        date_range = {
            'desde': self.date_from.date().toString("yyyy-MM-dd"),
            'hasta': self.date_to.date().toString("yyyy-MM-dd")
        }
        
        # Pasar db_manager como primer parámetro
        dialog = ExportDialog(self.db_manager, 'ventas', date_range, self)
        dialog.exec()