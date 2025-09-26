from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QDateEdit, QComboBox, QGroupBox, QTextEdit, QTabWidget,
    QApplication, QLineEdit, QCheckBox, QWidget, QSizePolicy
)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# Importar el diálogo de exportación
from export_dialog import ExportDialog

from utils.helpers import formato_moneda_mx

class SalesHistoryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Historial y Análisis de Ventas")
        self.setGeometry(100, 50, 1200, 800)

        self.date_range = {
            'desde': QDate.currentDate().addDays(-30).toString("yyyy-MM-dd"),
            'hasta': QDate.currentDate().toString("yyyy-MM-dd")
        }
        
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
        # Gráficos
        charts_layout = QHBoxLayout()
        
        # Gráfico de ventas por día
        chart1_group = QGroupBox("Ventas por Día")
        chart1_layout = QVBoxLayout()
        self.figure1 = Figure(figsize=(8, 5))  # Reducido para mejor ajuste
        self.canvas1 = FigureCanvas(self.figure1)
        
        # CONFIGURACIÓN PARA LA PRIMERA GRÁFICA
        self.canvas1.setMinimumSize(350, 300)
        self.canvas1.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        chart1_layout.addWidget(self.canvas1)
        chart1_group.setLayout(chart1_layout)
        chart1_group.setMinimumHeight(350)  # Altura mínima del grupo
        charts_layout.addWidget(chart1_group)
        
        # Gráfico de métodos de pago
        chart2_group = QGroupBox("Métodos de Pago")
        chart2_layout = QVBoxLayout()
        self.figure2 = Figure(figsize=(8, 5))  # Reducido para mejor ajuste
        self.canvas2 = FigureCanvas(self.figure2)
        
        # CONFIGURACIÓN PARA LA SEGUNDA GRÁFICA
        self.canvas2.setMinimumSize(350, 300)
        self.canvas2.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        chart2_layout.addWidget(self.canvas2)
        chart2_group.setLayout(chart2_layout)
        chart2_group.setMinimumHeight(350)  # Altura mínima del grupo
        charts_layout.addWidget(chart2_group)
        
        # CONFIGURACIÓN FINAL DEL LAYOUT
        charts_layout.setStretchFactor(chart1_group, 1)  # Ambas gráficas se expanden igual
        charts_layout.setStretchFactor(chart2_group, 1)

        # GENERAR GRÁFICOS CON FECHAS POR DEFECTO al abrir la ventana
        fecha_hasta = datetime.now().strftime('%Y-%m-%d')
        fecha_desde = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.generar_graficos(fecha_desde, fecha_hasta)
        
        layout.addLayout(charts_layout)
        layout.addStretch(1)  # Usa todo el espacio disponible
    
    def setup_products_tab(self, layout):
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["Producto", "Categoría", "Vendidos", "Total", "Última Venta", "Tendencia"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.products_table)
    
    def cargar_ventas(self):
        fecha_desde = self.date_from.date().toString("yyyy-MM-dd")
        fecha_hasta = self.date_to.date().toString("yyyy-MM-dd 23:59:59")

        self.date_range = {
            'desde': fecha_desde,
            'hasta': fecha_hasta.split()[0]  # Solo la fecha, sin la hora
        }

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
                total_formateado = formato_moneda_mx(total)
                iva_formateado = formato_moneda_mx(iva)
                self.sales_table.setItem(row, 2, QTableWidgetItem(total_formateado))
                self.sales_table.setItem(row, 3, QTableWidgetItem(iva_formateado))
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
                total_formateado = formato_moneda_mx(total)
                metodos_text += f"{metodo}: {total_formateado} ({count} ventas)\n"

                total_ventas_formateado = formato_moneda_mx(total_ventas)
                total_iva_formateado = formato_moneda_mx(total_iva)
            
            self.summary_label.setText(
                f"📊 PERIODO: {fecha_desde} a {fecha_hasta.split()[0]}\n"
                f"💰 TOTAL VENTAS: {total_ventas_formateado}\n"
                f"📈 TOTAL IVA: {total_iva_formateado}\n"
                f"🛒 N° VENTAS: {num_ventas}\n"
                f"💳 MÉTODOS DE PAGO:\n{metodos_text}"
            )
            
            self.generar_graficos(fecha_desde, fecha_hasta)
            self.cargar_productos_vendidos(fecha_desde, fecha_hasta)
    
    def generar_graficos(self, fecha_desde, fecha_hasta):
        # Gráfico 1: Ventas por día - VERSIÓN CORREGIDA
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DATE(fecha), SUM(total), COUNT(*)
                FROM ventas 
                WHERE fecha BETWEEN ? AND ?
                GROUP BY DATE(fecha)
                ORDER BY DATE(fecha)
            """, (fecha_desde, fecha_hasta))
            
            datos = cursor.fetchall()
            
        # CORRECCIÓN: Convertir fechas a strings para matplotlib
        fechas = [str(d[0]) for d in datos]  # Convertir a string
        totales = [float(d[1]) for d in datos]  # Asegurar que sean floats
        cantidades = [d[2] for d in datos]
        
        self.figure1.clear()
        ax1 = self.figure1.add_subplot(111)
        
        # VERIFICAR SI HAY DATOS
        if not datos:
            ax1.text(0.5, 0.5, 'No hay datos en el período seleccionado', 
                    ha='center', va='center', transform=ax1.transAxes, fontsize=12)
            ax1.set_title('Ventas por Día - Sin Datos')
        else:
            # USAR ÍNDICES NUMÉRICOS para las barras
            indices = range(len(fechas))
            bars = ax1.bar(indices, totales, color='skyblue', alpha=0.7, width=0.6)
            ax1.set_title('Ventas por Día')
            ax1.set_xlabel('Fecha')
            ax1.set_ylabel('Total Ventas ($)')
            
            # CONFIGURAR ETIQUETAS EN EL EJE X
            ax1.set_xticks(indices)
            ax1.set_xticklabels(fechas, rotation=45, ha='right')
            
            # AJUSTAR MÁRGENES para que quepan las etiquetas
            self.figure1.tight_layout()
            
            # AÑADIR VALORES EN LAS BARRAS
            for bar in bars:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'${height:,.0f}',
                        ha='center', va='bottom', fontsize=8)
        
        self.canvas1.draw()
        
        # Gráfico 2: Métodos de pago - TAMBIÉN MEJORADO
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT metodo_pago, SUM(total), COUNT(*)
                FROM ventas 
                WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
            """, (fecha_desde, fecha_hasta))
            
            metodos_data = cursor.fetchall()
        
        self.figure2.clear()
        ax2 = self.figure2.add_subplot(111)
        
        # VERIFICAR SI HAY DATOS
        if not metodos_data:
            ax2.text(0.5, 0.5, 'No hay datos de métodos de pago', 
                    ha='center', va='center', transform=ax2.transAxes, fontsize=12)
            ax2.set_title('Métodos de Pago - Sin Datos')
        else:
            metodos = [d[0] for d in metodos_data]
            totals = [float(d[1]) for d in metodos_data]  # Asegurar floats
            
            # MÁS COLORES PARA MÁS MÉTODOS DE PAGO
            colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0', '#ffb3e6']
            wedges, texts, autotexts = ax2.pie(totals, labels=metodos, autopct='%1.1f%%', 
                                              colors=colors[:len(metodos)], startangle=90)
            
            # MEJORAR ESTILO DEL GRÁFICO CIRCULAR
            ax2.set_title('Distribución por Método de Pago')
            
            # HACER LOS PORCENTAJES MÁS LEGIBLES
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        
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
                total_formateado = formato_moneda_mx(total)
                self.products_table.setItem(row, 2, QTableWidgetItem(total_formateado))
                self.products_table.setItem(row, 3, QTableWidgetItem(categoria))
                self.products_table.setItem(row, 4, QTableWidgetItem(ultima_venta))
                
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
                detalle_text += f"{nombre} x{cantidad} - ${precio:.2f} = ${subtotal:.2f}\n"
            
            QMessageBox.information(self, "Detalle de Venta", detalle_text)
    
    # Exportar reporte
    def exportar_reporte(self):
        """Exportar reporte de ventas - VERSIÓN CORREGIDA Y ROBUSTA"""
        try:
            # VERIFICACIÓN ROBUSTA DE date_range
            if not hasattr(self, 'date_range') or self.date_range is None:
             # Si no existe, crear uno con las fechas actuales de los date edits
                fecha_desde = self.date_from.date().toString("yyyy-MM-dd")
                fecha_hasta = self.date_to.date().toString("yyyy-MM-dd")
                self.date_range = {
                    'desde': fecha_desde,
                    'hasta': fecha_hasta
                }
                print(f"⚠️ date_range no existía, creado: {self.date_range}")
        
            print(f"📊 Exportando reporte para rango: {self.date_range}")
        
            # CORRECCIÓN DEL ORDEN DE PARÁMETROS
            dialog = ExportDialog(
                parent=self,                    # primer parámetro
                report_type='ventas',           # segundo parámetro  
                date_range=self.date_range      # tercer parámetro
            )
        
            dialog.exec()
        
        except Exception as e:
            print(f"❌ Error en exportar_reporte: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo exportar el reporte: {str(e)}")