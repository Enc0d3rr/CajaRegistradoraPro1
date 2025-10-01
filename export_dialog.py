from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QComboBox, QGroupBox
)
from PyQt6.QtGui import QPalette, QColor
import os
from datetime import datetime
from utils.helpers import formato_moneda_mx  

class ExportDialog(QDialog):
    def __init__(self, db_manager, report_type, date_range, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.report_type = report_type
        self.date_range = date_range
        self.setWindowTitle(f"Exportar Reporte de {report_type.capitalize()}")
        self.setGeometry(300, 200, 450, 250)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Información del reporte
        info_group = QGroupBox("Información del Reporte")
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Tipo: Reporte de {report_type}"))
        info_layout.addWidget(QLabel(f"Desde: {date_range['desde']}"))
        info_layout.addWidget(QLabel(f"Hasta: {date_range['hasta']}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Selección de formato
        format_group = QGroupBox("Formato de Exportación")
        format_layout = QVBoxLayout()
        format_layout.addWidget(QLabel("Seleccione el formato:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems([
            "PDF - Documento imprimible"
        ])
        format_layout.addWidget(self.format_combo)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_export = QPushButton("💾 Exportar")
        btn_export.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        btn_export.clicked.connect(self.exportar_reporte)
        buttons_layout.addWidget(btn_export)
        
        btn_cancel = QPushButton("❌ Cancelar")
        btn_cancel.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        btn_cancel.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancel)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def verificar_datos_reporte(self):
        """Verificar si hay datos para el reporte"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                fecha_desde = self.date_range['desde'].split(' ')[0] + ' 00:00:00'
                fecha_hasta = self.date_range['hasta'].split(' ')[0] + ' 23:59:59'
                
                if self.report_type == "ventas":
                    cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha BETWEEN ? AND ?", (fecha_desde, fecha_hasta))
                else:
                    cursor.execute("SELECT COUNT(*) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", (fecha_desde, fecha_hasta))
                
                count = cursor.fetchone()[0]
                return count > 0
                
        except Exception as e:
            return False
    
    def normalizar_fechas_consulta(self):
        """Normalizar formato de fechas para consultas SQL - CON DIAGNÓSTICO"""
        try:
            print(f"🔍 Normalizando fechas. Original: {self.date_range}")
            
            # Verificar que date_range tenga la estructura correcta
            if not isinstance(self.date_range, dict) or 'desde' not in self.date_range or 'hasta' not in self.date_range:
                print("❌ Estructura de date_range incorrecta, usando fechas por defecto")
                return {
                    'desde': '2000-01-01 00:00:00',
                    'hasta': '2030-12-31 23:59:59'
                }
            
            desde_str = str(self.date_range['desde'])
            hasta_str = str(self.date_range['hasta'])
            
            print(f"📅 Fechas originales - Desde: '{desde_str}', Hasta: '{hasta_str}'")
            
            # Si son solo fechas (sin hora), agregar hora
            if ' ' not in desde_str:
                fecha_desde = f"{desde_str} 00:00:00"
            else:
                fecha_desde = desde_str
                
            if ' ' not in hasta_str:
                fecha_hasta = f"{hasta_str} 23:59:59"
            else:
                fecha_hasta = hasta_str
            
            print(f"📅 Fechas normalizadas - Desde: '{fecha_desde}', Hasta: '{fecha_hasta}'")
            
            return {
                'desde': fecha_desde,
                'hasta': fecha_hasta
            }
                
        except Exception as e:
            print(f"❌ Error normalizando fechas: {e}")
            # Fechas por defecto muy amplias para asegurar que haya datos
            return {
                'desde': '2000-01-01 00:00:00',
                'hasta': '2030-12-31 23:59:59'
            }
        
    def diagnosticar_exportacion(self):
        """Función de diagnóstico para ver qué está pasando"""
        print("=== DIAGNÓSTICO DE EXPORTACIÓN ===")
        
        # 1. Verificar conexión a la base de datos
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Verificar tablas existentes
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tablas = cursor.fetchall()
                print("📊 Tablas en la base de datos:", [t[0] for t in tablas])
                
                # Verificar fechas que se están usando
                fechas = self.normalizar_fechas_consulta()
                print("📅 Fechas normalizadas:", fechas)
                
                # Verificar datos en ventas
                if self.report_type == "ventas":
                    cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha BETWEEN ? AND ?", 
                                (fechas['desde'], fechas['hasta']))
                    count_ventas = cursor.fetchone()[0]
                    print(f"🛒 Ventas en el período: {count_ventas}")
                    
                    # Ver algunas ventas de ejemplo
                    cursor.execute("SELECT id, fecha, total FROM ventas ORDER BY fecha DESC LIMIT 3")
                    ventas_ejemplo = cursor.fetchall()
                    print("📝 Últimas 3 ventas:", ventas_ejemplo)
                    
                else:  # cierres
                    cursor.execute("SELECT COUNT(*) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", 
                                (fechas['desde'], fechas['hasta']))
                    count_cierres = cursor.fetchone()[0]
                    print(f"💰 Cierres en el período: {count_cierres}")
                    
                    # Ver algunos cierres de ejemplo
                    cursor.execute("SELECT id, fecha_apertura, total_ventas FROM cierres_caja ORDER BY fecha_apertura DESC LIMIT 3")
                    cierres_ejemplo = cursor.fetchall()
                    print("📝 Últimos 3 cierres:", cierres_ejemplo)
                    
        except Exception as e:
            print(f"❌ Error en diagnóstico: {e}")
    
    def exportar_reporte(self):
        reports_dir = "Reportes"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{reports_dir}/{self.report_type}_{timestamp}.pdf"
        
        try:
            self.exportar_pdf(filename)
            QMessageBox.information(self, "✅ Éxito", 
                f"Reporte PDF exportado correctamente\n\nArchivo: {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"No se pudo exportar PDF: {str(e)}")
    
    def exportar_pdf(self, filename):
        """Exportar a PDF - VERSIÓN MEJORADA QUE USA REPORTLAB REAL"""
        try:
            print(f"🔄 Exportando PDF a: {filename}")
            
            # Verificar explícitamente si reportlab está disponible
            try:
                import reportlab
                print("✅ ReportLab está instalado, generando PDF real...")
                
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib import colors
                from reportlab.lib.units import inch
                
                # Crear documento PDF real
                doc = SimpleDocTemplate(filename, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                
                # Título
                title_style = getSampleStyleSheet()['Heading1']
                elements.append(Paragraph(f"REPORTE DE {self.report_type.upper()}", title_style))
                elements.append(Spacer(1, 20))
                
                # Información del reporte
                normal_style = styles['Normal']
                elements.append(Paragraph(f"<b>Generado:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
                elements.append(Paragraph(f"<b>Período:</b> {self.date_range['desde']} a {self.date_range['hasta']}", normal_style))
                elements.append(Spacer(1, 20))
                
                # Contenido específico del reporte
                if self.report_type == "ventas":
                    content = self._generar_contenido_ventas_pdf()
                else:
                    content = self._generar_contenido_cierres_pdf()
                
                elements.extend(content)
                
                # Construir PDF
                doc.build(elements)
                print(f"✅ PDF real generado correctamente: {filename}")
                
                QMessageBox.information(self, "✅ PDF Exportado", 
                    f"PDF con formato profesional generado correctamente\n\nArchivo: {os.path.basename(filename)}")
                
                return filename
                
            except ImportError as e:
                print(f"⚠️ ReportLab no disponible: {e}")
                raise ImportError("ReportLab no está instalado")
                
        except ImportError:
            # Fallback a texto plano solo si ReportLab no está instalado
            print("🔄 Usando fallback a texto plano para PDF")
            return self._exportar_pdf_fallback(filename)
        except Exception as e:
            print(f"❌ Error generando PDF real: {e}")
            # Fallback a texto plano en caso de error
            return self._exportar_pdf_fallback(filename)
        
    def _exportar_pdf_fallback(self, filename):
        """Fallback a texto plano para PDF"""
        txt_filename = filename.replace('.pdf', '.txt')
        
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("SISTEMA DE CAJA REGISTRADORA\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"REPORTE DE {self.report_type.upper()}\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Período: {self.date_range['desde']} a {self.date_range['hasta']}\n\n")
            
            if self.report_type == "ventas":
                self._exportar_ventas_texto(f)
            else:
                self._exportar_cierres_texto(f)
        
        print(f"✅ PDF fallback generado como texto: {txt_filename}")
        return txt_filename
    
    def _generar_contenido_ventas_pdf(self):
        """Generar contenido para PDF de ventas - VERSIÓN SIMPLIFICADA Y FUNCIONAL"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        elements = []
        styles = getSampleStyleSheet()
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                fechas = self.normalizar_fechas_consulta()
                
                # Resumen
                cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ?", 
                            (fechas['desde'], fechas['hasta']))
                resultado = cursor.fetchone()
                total_ventas = resultado[0] if resultado else 0
                monto_total = resultado[1] if resultado else 0
                
                elements.append(Paragraph(f"<b>Total de ventas:</b> {total_ventas}", styles['Normal']))
                elements.append(Paragraph(f"<b>Monto total:</b> {formato_moneda_mx(monto_total)}", styles['Normal']))
                elements.append(Spacer(1, 15))
                
                if total_ventas > 0:
                    # Detalle de ventas (limitado para no hacer el PDF muy grande)
                    cursor.execute("""
                        SELECT v.id, v.fecha, v.total, v.metodo_pago, u.nombre
                        FROM ventas v 
                        JOIN usuarios u ON v.usuario_id = u.id 
                        WHERE v.fecha BETWEEN ? AND ?
                        ORDER BY v.fecha DESC
                        LIMIT 30
                    """, (fechas['desde'], fechas['hasta']))
                    
                    ventas = cursor.fetchall()
                    
                    # Crear tabla simple
                    data = [['ID', 'Fecha', 'Total', 'Método', 'Vendedor']]
                    for venta in ventas:
                        id_venta, fecha, total, metodo, vendedor = venta
                        # Formatear fecha para que sea más corta
                        fecha_corta = fecha.split()[0] if ' ' in fecha else fecha
                        data.append([
                            str(id_venta),
                            fecha_corta,
                            formato_moneda_mx(total),
                            metodo,
                            vendedor
                        ])
                    
                    if len(data) > 1:  # Si hay datos además del encabezado
                        table = Table(data, colWidths=[50, 80, 70, 80, 100])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F3F3')),
                            ('FONTSIZE', (0, 1), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                        ]))
                        elements.append(table)
                    else:
                        elements.append(Paragraph("No hay datos para mostrar", styles['Normal']))
                
        except Exception as e:
            print(f"❌ Error generando contenido PDF: {e}")
            elements.append(Paragraph(f"Error al generar contenido: {str(e)}", styles['Normal']))
        
        return elements
    
    def _generar_contenido_cierres_pdf(self):
        """Generar contenido para PDF de cierres"""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib import colors
        
        elements = []
        styles = getSampleStyleSheet()
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                fechas = self.normalizar_fechas_consulta()
                
                # Resumen
                cursor.execute("SELECT COUNT(*), SUM(total_ventas), AVG(diferencia) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", 
                             (fechas['desde'], fechas['hasta']))
                resultado = cursor.fetchone()
                total_cierres = resultado[0] if resultado else 0
                ventas_total = resultado[1] if resultado else 0
                diff_promedio = resultado[2] if resultado else 0
                
                elements.append(Paragraph(f"<b>Total de cierres:</b> {total_cierres}", styles['Normal']))
                elements.append(Paragraph(f"<b>Ventas totales:</b> {formato_moneda_mx(ventas_total)}", styles['Normal']))
                elements.append(Paragraph(f"<b>Diferencia promedio:</b> {formato_moneda_mx(diff_promedio)}", styles['Normal']))
                elements.append(Spacer(1, 15))
                
                if total_cierres > 0:
                    # Detalle de cierres
                    cursor.execute("""
                        SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.ventas_efectivo,
                               c.ventas_tarjeta, c.total_ventas, c.diferencia
                        FROM cierres_caja c
                        JOIN usuarios u ON c.usuario_id = u.id
                        WHERE c.fecha_apertura BETWEEN ? AND ?
                        ORDER BY c.fecha_apertura DESC
                    """, (fechas['desde'], fechas['hasta']))
                    
                    cierres = cursor.fetchall()
                    
                    # Crear tabla
                    data = [['Fecha', 'Usuario', 'Monto Inicial', 'Ventas Efectivo', 'Ventas Tarjeta', 'Total', 'Diferencia']]
                    for cierre in cierres:
                        fecha, usuario, inicial, efectivo, tarjeta, total, diff = cierre
                        fecha_corta = fecha.split()[0] if ' ' in fecha else fecha
                        data.append([
                            fecha_corta,
                            usuario,
                            formato_moneda_mx(inicial),
                            formato_moneda_mx(efectivo),
                            formato_moneda_mx(tarjeta),
                            formato_moneda_mx(total),
                            formato_moneda_mx(diff)
                        ])
                    
                    if len(data) > 1:
                        table = Table(data, colWidths=[80, 80, 70, 70, 70, 70, 70])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 9),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F3F3F3')),
                            ('FONTSIZE', (0, 1), (-1, -1), 8),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
                        ]))
                        elements.append(table)
                    else:
                        elements.append(Paragraph("No hay datos para mostrar", styles['Normal']))
                
        except Exception as e:
            print(f"❌ Error generando contenido PDF cierres: {e}")
            elements.append(Paragraph(f"Error al generar contenido: {str(e)}", styles['Normal']))
        
        return elements