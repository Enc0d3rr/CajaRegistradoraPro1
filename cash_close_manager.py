from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QDateEdit, QTextEdit, QGroupBox,
    QInputDialog, QTabWidget, QWidget, QGridLayout
)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QDate
from datetime import datetime, timedelta
from export_dialog import ExportDialog
from utils.helpers import formato_moneda_mx 

class CashCloseManagerDialog(QDialog):
    def __init__(self, db_manager, current_user, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = current_user
        self.setWindowTitle("Cierre de Caja y Reportes")
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
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)
        
        filter_layout.addWidget(QLabel("Hasta:"))
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)
        
        # Botón Filtrar
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
        btn_filter.clicked.connect(self.generar_reporte)
        filter_layout.addWidget(btn_filter)

        # Botón Exportar
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
        
        # Pestañas para diferentes reportes
        self.tabs = QTabWidget()
        
        # Reporte de ventas
        sales_tab = QWidget()
        sales_layout = QVBoxLayout()
        self.setup_sales_tab(sales_layout)
        sales_tab.setLayout(sales_layout)
        self.tabs.addTab(sales_tab, "Ventas")
        
        # Reporte de productos
        products_tab = QWidget()
        products_layout = QVBoxLayout()
        self.setup_products_tab(products_layout)
        products_tab.setLayout(products_layout)
        self.tabs.addTab(products_tab, "Productos")
        
        # Cierre de caja
        cash_tab = QWidget()
        cash_layout = QVBoxLayout()
        self.setup_cash_tab(cash_layout)
        cash_tab.setLayout(cash_layout)
        self.tabs.addTab(cash_tab, "Cierre Caja")
        
        layout.addWidget(self.tabs)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)
        
        # Generar reporte inicial
        self.generar_reporte()
    
    def setup_sales_tab(self, layout):
        # Tabla de ventas
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Fecha", "Total", "IVA", "Método Pago", "Usuario"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sales_table)
        
        # Resumen de ventas - CON EL MISMO ESTILO QUE HISTORIAL DE VENTAS
        summary_group = QGroupBox("Resumen de Ventas")
        summary_layout = QVBoxLayout()
        
        self.sales_summary = QTextEdit()
        self.sales_summary.setReadOnly(True)
        self.sales_summary.setMaximumHeight(180)
        summary_layout.addWidget(self.sales_summary)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
    
    def setup_products_tab(self, layout):
        # Tabla de productos vendidos
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels(["Producto", "Cantidad", "Total Vendido", "Categoría", "Última Venta"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.products_table)
    
    def setup_cash_tab(self, layout):
        # Formulario de cierre de caja
        form_layout = QGridLayout()
        
        form_layout.addWidget(QLabel("Efectivo Inicial:"), 0, 0)
        self.efectivo_inicial = QLineEdit()
        self.efectivo_inicial.setText("0.00")
        form_layout.addWidget(self.efectivo_inicial, 0, 1)
        
        form_layout.addWidget(QLabel("Efectivo en Caja Esperado:"), 1, 0)
        self.efectivo_esperado = QLineEdit()
        self.efectivo_esperado.setReadOnly(True)
        form_layout.addWidget(self.efectivo_esperado, 1, 1)
        
        # AGREGAR ESTE CAMPO QUE FALTABA
        form_layout.addWidget(QLabel("Efectivo en Caja:"), 2, 0)
        self.efectivo_caja = QLineEdit()
        self.efectivo_caja.setReadOnly(True)
        form_layout.addWidget(self.efectivo_caja, 2, 1)
        
        form_layout.addWidget(QLabel("Ventas en Efectivo:"), 3, 0)
        self.ventas_efectivo = QLineEdit()
        self.ventas_efectivo.setReadOnly(True)
        form_layout.addWidget(self.ventas_efectivo, 3, 1)
        
        form_layout.addWidget(QLabel("Ventas con Tarjeta:"), 4, 0)
        self.ventas_tarjeta = QLineEdit()
        self.ventas_tarjeta.setReadOnly(True)
        form_layout.addWidget(self.ventas_tarjeta, 4, 1)
        
        form_layout.addWidget(QLabel("Ventas por Transferencia:"), 5, 0)
        self.ventas_transferencia = QLineEdit()
        self.ventas_transferencia.setReadOnly(True)
        form_layout.addWidget(self.ventas_transferencia, 5, 1)
        
        form_layout.addWidget(QLabel("TOTAL VENTAS DEL DÍA:"), 6, 0)
        self.total_ventas = QLineEdit()
        self.total_ventas.setReadOnly(True)
        form_layout.addWidget(self.total_ventas, 6, 1)
        
        form_layout.addWidget(QLabel("Diferencia:"), 7, 0)
        self.diferencia = QLineEdit()
        self.diferencia.setReadOnly(True)
        form_layout.addWidget(self.diferencia, 7, 1)
        
        layout.addLayout(form_layout)
        
        # Botones de cierre
        buttons_layout = QHBoxLayout()
        
        btn_calculate = QPushButton("Calcular")
        btn_calculate.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        btn_calculate.clicked.connect(self.calcular_cierre)
        buttons_layout.addWidget(btn_calculate)
        
        btn_save_close = QPushButton("Guardar Cierre")
        btn_save_close.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_save_close.clicked.connect(self.guardar_cierre)
        buttons_layout.addWidget(btn_save_close)
        
        layout.addLayout(buttons_layout)
        
        # Historial de cierres
        history_group = QGroupBox("Historial de Cierres")
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Fecha", "Efectivo Inicial", "Efectivo Final", "Total Ventas", "Usuario"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
        
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)
        
        self.cargar_historial_cierres()
    
    def generar_reporte(self):
        fecha_desde = self.date_from.date().toString("yyyy-MM-dd")
        fecha_hasta = self.date_to.date().toString("yyyy-MM-dd 23:59:59")
        
        self.cargar_ventas(fecha_desde, fecha_hasta)
        self.cargar_productos_vendidos(fecha_desde, fecha_hasta)
        self.calcular_totales_cierre(fecha_desde, fecha_hasta)

    def exportar_reporte(self):
        """Abre diálogo de exportación para cierres - VERSIÓN CORREGIDA"""
        date_range = {
            'desde': self.date_from.date().toString("yyyy-MM-dd"),
            'hasta': self.date_to.date().toString("yyyy-MM-dd")
        }

        # ✅ CORRECCIÓN: Pasar db_manager como primer parámetro
        dialog = ExportDialog(self.db_manager, 'cierres', date_range, self)
        dialog.exec()
    
    def cargar_ventas(self, fecha_desde, fecha_hasta):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT v.id, v.fecha, v.total, v.iva, v.metodo_pago, u.nombre 
                FROM ventas v 
                JOIN usuarios u ON v.usuario_id = u.id 
                WHERE v.fecha BETWEEN ? AND ?
                ORDER BY v.fecha DESC
            """, (fecha_desde, fecha_hasta))
            
            ventas = cursor.fetchall()
            
            self.sales_table.setRowCount(len(ventas))
            for row, (id_, fecha, total, iva, metodo_pago, usuario) in enumerate(ventas):
                self.sales_table.setItem(row, 0, QTableWidgetItem(str(id_)))
                self.sales_table.setItem(row, 1, QTableWidgetItem(fecha))

                self.sales_table.setItem(row, 2, QTableWidgetItem(formato_moneda_mx(total)))
                self.sales_table.setItem(row, 3, QTableWidgetItem(formato_moneda_mx(iva)))

                self.sales_table.setItem(row, 4, QTableWidgetItem(metodo_pago))
                self.sales_table.setItem(row, 5, QTableWidgetItem(usuario))
    
    def cargar_productos_vendidos(self, fecha_desde, fecha_hasta):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    p.nombre, 
                    SUM(dv.cantidad), 
                    SUM(dv.subtotal), 
                    COALESCE(cat.nombre, 'Sin categoría') as categoria_nombre,
                    MAX(v.fecha)
                FROM detalle_ventas dv
                JOIN productos p ON dv.producto_id = p.id  
                LEFT JOIN categorias cat ON p.categoria_id = cat.id
                JOIN ventas v ON dv.venta_id = v.id
                WHERE v.fecha BETWEEN ? AND ?
                GROUP BY p.id, p.nombre, cat.nombre  
                ORDER BY SUM(dv.subtotal) DESC
            """, (fecha_desde, fecha_hasta))
            
            productos = cursor.fetchall()
            
            self.products_table.setRowCount(len(productos))
            for row, (nombre, cantidad, total, categoria, ultima_venta) in enumerate(productos):
                self.products_table.setItem(row, 0, QTableWidgetItem(nombre))
                self.products_table.setItem(row, 1, QTableWidgetItem(str(cantidad)))
                self.products_table.setItem(row, 2, QTableWidgetItem(formato_moneda_mx(total)))
                self.products_table.setItem(row, 3, QTableWidgetItem(categoria))
                self.products_table.setItem(row, 4, QTableWidgetItem(ultima_venta))
    
    def calcular_totales_cierre(self, fecha_desde, fecha_hasta):
        """Calcula los totales para el cierre de caja - VERSIÓN MEJORADA"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Totales por método de pago
                cursor.execute("""
                    SELECT metodo_pago, COALESCE(SUM(total), 0) 
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                    GROUP BY metodo_pago
                """, (fecha_desde, fecha_hasta))
                
                totales = {"Efectivo": 0, "Tarjeta": 0, "Transferencia": 0}
                for metodo, total in cursor.fetchall():
                    if metodo in totales:
                        totales[metodo] = total
                
                # Total general de ventas
                cursor.execute("""
                    SELECT COALESCE(SUM(total), 0) 
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                """, (fecha_desde, fecha_hasta))
                
                total_ventas = cursor.fetchone()[0]
                
                # Número total de ventas
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM ventas 
                    WHERE fecha BETWEEN ? AND ? AND estado = 'completada'
                """, (fecha_desde, fecha_hasta))
                
                numero_ventas = cursor.fetchone()[0] or 0
                
                # Calcular efectivo inicial (si ya se ingresó)
                try:
                    efectivo_inicial_text = self.efectivo_inicial.text().strip()
                    if not efectivo_inicial_text:
                        efectivo_inicial_text = "0"
                    efectivo_inicial_text = efectivo_inicial_text.replace('$', '').replace(',', '').strip()
                    efectivo_inicial = float(efectivo_inicial_text)
                except:
                    efectivo_inicial = 0
                
                # Calcular efectivo esperado
                efectivo_esperado = efectivo_inicial + totales['Efectivo']
                
                # Actualizar campos del formulario
                self.ventas_efectivo.setText(formato_moneda_mx(totales['Efectivo']))
                self.ventas_tarjeta.setText(formato_moneda_mx(totales['Tarjeta']))
                self.ventas_transferencia.setText(formato_moneda_mx(totales['Transferencia']))
                self.total_ventas.setText(formato_moneda_mx(total_ventas))
                self.efectivo_esperado.setText(formato_moneda_mx(efectivo_esperado))
                
                # ✅ ACTUALIZAR EL RESUMEN DE VENTAS (lo que ves vacío)
                if hasattr(self, 'sales_summary') and self.sales_summary:
                    fecha_hasta_corta = fecha_hasta.split()[0] 
                    
                    if numero_ventas > 0:
                        resumen_texto = f"""📊 REPORTE DE VENTAS ({fecha_desde} a {fecha_hasta_corta})

    • Total Ventas: {formato_moneda_mx(total_ventas)}
    • N° de Ventas: {numero_ventas}
    • Promedio por Venta: {formato_moneda_mx(total_ventas/numero_ventas)}

    • Efectivo: {formato_moneda_mx(totales['Efectivo'])} ({numero_ventas and (totales['Efectivo']/total_ventas*100):.1f}%)
    • Tarjeta: {formato_moneda_mx(totales['Tarjeta'])} ({numero_ventas and (totales['Tarjeta']/total_ventas*100):.1f}%)
    • Transferencia: {formato_moneda_mx(totales['Transferencia'])} ({numero_ventas and (totales['Transferencia']/total_ventas*100):.1f}%)"""
                    else:
                        resumen_texto = f"""📊 REPORTE DE VENTAS ({fecha_desde} a {fecha_hasta_corta})

    • No hay ventas registradas en este período
    • Total Ventas: {formato_moneda_mx(0)}
    • N° de Ventas: 0

    • Efectivo: {formato_moneda_mx(0)}
    • Tarjeta: {formato_moneda_mx(0)} 
    • Transferencia: {formato_moneda_mx(0)}"""
                    
                    self.sales_summary.setPlainText(resumen_texto)
                
                print(f"📊 CÁLCULOS DE CIERRE:")
                print(f"   Período: {fecha_desde} a {fecha_hasta}")
                print(f"   Ventas Efectivo: {totales['Efectivo']}")
                print(f"   Ventas Tarjeta: {totales['Tarjeta']}")
                print(f"   Ventas Transferencia: {totales['Transferencia']}")
                print(f"   TOTAL VENTAS: {total_ventas}")
                print(f"   N° VENTAS: {numero_ventas}")
                print(f"   EFECTIVO ESPERADO: {efectivo_esperado}")
                    
        except Exception as e:
            print(f"❌ Error calculando totales: {e}")
            # Si hay error, mostrar mensaje en el resumen
            if hasattr(self, 'sales_summary') and self.sales_summary:
                self.sales_summary.setPlainText(f"❌ Error cargando datos de ventas:\n{str(e)}")
            
            # Resumen de ventas
            summary_text = f"""
            📊 REPORTE DE VENTAS ({fecha_desde} a {fecha_hasta.split()[0]})
            • Total Ventas: {formato_moneda_mx(total_ventas)}
            • Efectivo: {formato_moneda_mx(totales['Efectivo'])}
            • Tarjeta: {formato_moneda_mx(totales['Tarjeta'])}
            • Transferencia: {formato_moneda_mx(totales['Transferencia'])}
            • N° de Ventas: {self.sales_table.rowCount()}
            """
            self.sales_summary.setPlainText(summary_text)
    
    def calcular_cierre(self):
        """Calcula el cierre de caja con manejo robusto de errores"""
        try:
            # Obtener y validar efectivo inicial
            efectivo_inicial_text = self.efectivo_inicial.text().strip()
            if not efectivo_inicial_text:
                efectivo_inicial_text = "0"
            
            efectivo_inicial_text = efectivo_inicial_text.replace('$', '').replace(',', '').strip()
            efectivo_inicial = float(efectivo_inicial_text)
            
            # Obtener y validar ventas en efectivo
            ventas_efectivo_text = self.ventas_efectivo.text().strip()
            if not ventas_efectivo_text:
                ventas_efectivo_text = "0"
            
            ventas_efectivo_text = ventas_efectivo_text.replace('$', '').replace(',', '').strip()
            ventas_efectivo = float(ventas_efectivo_text)
            
            # Calcular efectivo esperado
            efectivo_esperado = efectivo_inicial + ventas_efectivo
            
            # ✅ CORRECCIÓN: Actualizar AMBOS campos
            self.efectivo_esperado.setText(formato_moneda_mx(efectivo_esperado))
            self.efectivo_caja.setText(formato_moneda_mx(efectivo_esperado))  # ← ESTA LÍNEA FALTABA
            
            # Pedir al usuario el efectivo físico contado
            efectivo_fisico, ok = QInputDialog.getDouble(
                self, 
                "Efectivo Físico", 
                "Ingrese el efectivo físico contado en caja:",
                float(efectivo_esperado),  # Valor por defecto
                0,                         # Mínimo
                1000000,                   # Máximo
                2                          # Decimales
            )
            
            if ok:
                # Calcular diferencia
                diferencia = efectivo_fisico - efectivo_esperado
                
                # Mostrar la diferencia
                self.diferencia.setText(formato_moneda_mx(diferencia))
                
                # Colores para la diferencia
                if diferencia < 0:
                    # Faltante - Rojo
                    self.diferencia.setStyleSheet("color: #cc0000; font-weight: bold; background-color: #ffcccc; padding: 3px;")
                    print(f"🔴 Diferencia: FALTANTE de {formato_moneda_mx(abs(diferencia))}")
                elif diferencia > 0:
                    # Sobrante - Verde
                    self.diferencia.setStyleSheet("color: #006600; font-weight: bold; background-color: #ccffcc; padding: 3px;")
                    print(f"🟢 Diferencia: SOBRANTE de {formato_moneda_mx(diferencia)}")
                else:
                    # Exacto - Azul
                    self.diferencia.setStyleSheet("color: #0066cc; font-weight: bold; background-color: #e6f7ff; padding: 3px;")
                    print(f"🔵 Diferencia: EXACTO ({formato_moneda_mx(diferencia)})")
                    
                print(f"✅ Cálculo completado:")
                print(f"   Efectivo inicial: {formato_moneda_mx(efectivo_inicial)}")
                print(f"   Ventas efectivo: {formato_moneda_mx(ventas_efectivo)}")
                print(f"   Efectivo esperado: {formato_moneda_mx(efectivo_esperado)}")
                print(f"   Efectivo físico: {formato_moneda_mx(efectivo_fisico)}")
                print(f"   Diferencia: {formato_moneda_mx(diferencia)}")
            
        except ValueError as e:
            print(f"❌ Error de conversión numérica: {e}")
            QMessageBox.warning(self, "Error", "Por favor ingrese valores numéricos válidos")
        except Exception as e:
            print(f"❌ Error inesperado en calcular_cierre: {e}")
            QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {str(e)}")
    
    def guardar_cierre(self):
        """Guarda el cierre de caja con manejo correcto de formato de moneda"""
        try:
            # Función auxiliar para limpiar y convertir valores monetarios
            def limpiar_valor_monetario(texto):
                if not texto:
                    return 0.0
                # Eliminar símbolos de moneda, comas y espacios
                texto_limpio = texto.replace('$', '').replace(',', '').replace(' ', '').strip()
                return float(texto_limpio) if texto_limpio else 0.0
            
            # Obtener y limpiar todos los valores
            efectivo_inicial = limpiar_valor_monetario(self.efectivo_inicial.text())
            ventas_efectivo = limpiar_valor_monetario(self.ventas_efectivo.text())
            ventas_tarjeta = limpiar_valor_monetario(self.ventas_tarjeta.text())
            ventas_transferencia = limpiar_valor_monetario(self.ventas_transferencia.text())
            total_ventas = limpiar_valor_monetario(self.total_ventas.text())
            diferencia = limpiar_valor_monetario(self.diferencia.text())
            
            # Calcular efectivo final esperado
            efectivo_final = efectivo_inicial + ventas_efectivo

            print(f"💾 Guardando cierre:")
            print(f"   Efectivo inicial: {efectivo_inicial}")
            print(f"   Ventas efectivo: {ventas_efectivo}")
            print(f"   Ventas tarjeta: {ventas_tarjeta}")
            print(f"   Ventas transferencia: {ventas_transferencia}")
            print(f"   Total ventas: {total_ventas}")
            print(f"   Efectivo final: {efectivo_final}")
            print(f"   Diferencia: {diferencia}")

            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cierres_caja 
                    (usuario_id, monto_inicial, ventas_efectivo, ventas_tarjeta, 
                    ventas_transferencia, total_ventas, total_efectivo, diferencia)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    self.current_user['id'],
                    efectivo_inicial,
                    ventas_efectivo,
                    ventas_tarjeta,
                    ventas_transferencia,
                    total_ventas,
                    efectivo_final,
                    diferencia
                ))
                conn.commit()
            
            QMessageBox.information(self, "Éxito", "Cierre de caja guardado correctamente")
            self.cargar_historial_cierres()
        
        except ValueError as e:
            print(f"❌ Error de conversión numérica: {e}")
            QMessageBox.warning(
                self, 
                "Error de formato", 
                f"Error al convertir valores numéricos:\n{str(e)}\n\n"
                "Asegúrese de que todos los campos tengan valores válidos."
            )
        except Exception as e:
            print(f"❌ Error guardando cierre: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo guardar el cierre: {str(e)}")
    
    def cargar_historial_cierres(self):
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # ✅ CONSULTA SIMPLIFICADA Y CORREGIDA
                cursor.execute("""
                    SELECT 
                        COALESCE(c.fecha_cierre, c.fecha_apertura) as fecha,
                        c.monto_inicial,
                        COALESCE(c.total_efectivo, 0),
                        COALESCE(c.total_ventas, 0),
                        u.nombre
                    FROM cierres_caja c
                    JOIN usuarios u ON c.usuario_id = u.id
                    ORDER BY c.fecha_apertura DESC
                    LIMIT 20
                """)
                
                cierres = cursor.fetchall()
                
                self.history_table.setRowCount(len(cierres))
                for row, (fecha, monto_inicial, efectivo_final, total_ventas, usuario) in enumerate(cierres):
                    self.history_table.setItem(row, 0, QTableWidgetItem(str(fecha)))  
                    self.history_table.setItem(row, 1, QTableWidgetItem(formato_moneda_mx(monto_inicial)))
                    self.history_table.setItem(row, 2, QTableWidgetItem(formato_moneda_mx(efectivo_final)))
                    self.history_table.setItem(row, 3, QTableWidgetItem(formato_moneda_mx(total_ventas)))
                    self.history_table.setItem(row, 4, QTableWidgetItem(usuario))
                
        except Exception as e:
            print(f"Error cargando historial de cierres: {e}")
            QMessageBox.warning(self, "Error", f"No se pudo cargar el historial: {str(e)}")

    def cierre_diario(self):
        """Cierre automático del día actual"""
        try:
            # Establecer fechas para el día actual
            hoy = QDate.currentDate()
            self.date_from.setDate(hoy)
            self.date_to.setDate(hoy)
            
            # Generar reporte del día
            self.generar_reporte()
            
            # Calcular cierre automático
            self.calcular_cierre()
            
            QMessageBox.information(self, "Cierre Diario", "Reporte del día generado correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo generar el cierre diario: {str(e)}")