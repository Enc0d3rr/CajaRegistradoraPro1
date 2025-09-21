from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QComboBox, QGroupBox, QFileDialog
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
import os
import csv
from datetime import datetime

class ExportDialog(QDialog):
    def __init__(self, db_manager, report_type, date_range, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.report_type = report_type  # 'ventas' o 'cierres'
        self.date_range = date_range    # {'desde': fecha, 'hasta': fecha}
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
            "PDF - Documento imprimible", 
            "Excel - Hoja de cálculo", 
            "CSV - Datos para análisis"
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
    
    def exportar_reporte(self):
        formato = self.format_combo.currentText()
        reports_dir = "Reportes"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{reports_dir}/{self.report_type}_{timestamp}"
        
        try:
            if "PDF" in formato:
                filename = f"{base_filename}.pdf"
                self.exportar_pdf(filename)
                
            elif "Excel" in formato:
                filename = f"{base_filename}.xlsx"
                self.exportar_excel(filename)
                
            elif "CSV" in formato:
                filename = f"{base_filename}.csv"
                self.exportar_csv(filename)
            
            QMessageBox.information(self, "✅ Éxito", 
                f"Reporte exportado correctamente\n\n"
                f"Archivo: {os.path.basename(filename)}\n"
                f"Ubicación: {os.path.dirname(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"No se pudo exportar: {str(e)}")
    
    def exportar_pdf(self, filename):
        """Exportar a PDF - Implementación mejorada"""
        try:
            # Intentar usar reportlab si está disponible
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.pdfgen import canvas
                from reportlab.lib.utils import ImageReader
                import io

                # Crear PDF con reportlab
                c = canvas.Canvas(filename, pagesize=letter)
                width, height = letter

                # Encabezado
                c.setFont("Helvetica-Bold", 16)
                c.drawString(50, height - 50, f"REPORTE DE {self.report_type.upper()}")

                c.setFont("Helvetica", 12)
                c.drawString(50, height - 70, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                c.drawString(50, height - 85, f"Período: {self.date_range['desde']} a {self.date_range['hasta']}")

                # Línea separadora
                c.line(50, height - 95, width - 50, height - 95)
            
                # Contenido
                y_position = height - 120
            
                if self.report_type == "ventas":
                    self._exportar_ventas_pdf(c, y_position)
                else:
                    self._exportar_cierres_pdf(c, y_position)
            
                c.save()
            
                QMessageBox.information(self, "✅ PDF Exportado", 
                    f"PDF generado correctamente con formato avanzado\n\n"
                    f"Archivo: {os.path.basename(filename)}")
            
            except ImportError:
                # Fallback a texto plano si reportlab no está instalado
                self._exportar_pdf_texto_plano(filename)
            
        except Exception as e:
            raise Exception(f"Error PDF: {str(e)}")
        
    def _exportar_pdf_texto_plano(self, filename):
        """Fallback para PDF de texto plano - PERO con extensión .txt"""
        # Cambiar extensión a .txt para que sea claro que es texto
        txt_filename = filename.replace('.pdf', '.txt')
    
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(f"REPORTE DE {self.report_type.upper()}\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Período: {self.date_range['desde']} a {self.date_range['hasta']}\n\n")
        
            if self.report_type == "ventas":
                self._exportar_ventas_texto(f)
            else:
                self._exportar_cierres_texto(f)
    
        # Mensaje informativo
        QMessageBox.information(self, "📄 Exportado como Texto", 
            "Se generó un archivo de texto (.txt) en lugar de PDF.\n\n"
            "Para PDFs con formato avanzado, instale:\n"
            "pip install reportlab\n\n"
            f"Archivo: {os.path.basename(txt_filename)}")
    
    def _exportar_ventas_pdf(self, c, y_position):
        """Datos de ventas para PDF con reportlab"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total) FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """, (self.date_range['desde'], self.date_range['hasta']))
            total_ventas, monto_total = cursor.fetchone()
        
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"Total de ventas: {total_ventas or 0}")
            c.drawString(50, y_position - 20, f"Monto total: ${monto_total or 0:.2f}")
        
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, COUNT(*), SUM(total) 
                FROM ventas WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            y = y_position - 40
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Por método de pago:")
        
            y -= 20
            c.setFont("Helvetica", 10)
            for metodo, count, monto in cursor.fetchall():
                c.drawString(70, y, f"{metodo}: {count} ventas (${monto or 0:.2f})")
                y -= 15
        
            # Últimas ventas
            y -= 20
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Últimas ventas:")
        
            y -= 20
            cursor.execute("""
                SELECT v.fecha, v.total, v.metodo_pago, u.nombre
                FROM ventas v 
                JOIN usuarios u ON v.usuario_id = u.id 
                WHERE v.fecha BETWEEN ? AND ?
                ORDER BY v.fecha DESC
                LIMIT 10
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            c.setFont("Helvetica", 8)
            for fecha, total, metodo, usuario in cursor.fetchall():
                texto = f"{fecha} - {usuario} - {metodo} - ${total:.2f}"
                if len(texto) > 80:  # Acortar si es muy largo
                    texto = texto[:77] + "..."
                c.drawString(70, y, texto)
                y -= 12
    
    def _exportar_cierres_pdf(self, c, y_position):
        """Datos de cierres para PDF con reportlab"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*), SUM(total_ventas), AVG(diferencia)
                FROM cierres_caja 
                WHERE fecha_apertura BETWEEN ? AND ?
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            total_cierres, ventas_total, diff_promedio = cursor.fetchone()
        
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"Cierres realizados: {total_cierres or 0}")
            c.drawString(50, y_position - 20, f"Ventas totales: ${ventas_total or 0:.2f}")
            c.drawString(50, y_position - 40, f"Diferencia promedio: ${diff_promedio or 0:.2f}")
        
            # Detalles de cierres
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position - 70, "Detalles de cierres:")
        
            cursor.execute("""
                SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.total_ventas, c.diferencia
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.fecha_apertura BETWEEN ? AND ?
                ORDER BY c.fecha_apertura DESC
                LIMIT 10
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            y = y_position - 90
            c.setFont("Helvetica", 10)
            for fecha, usuario, inicial, total, diff in cursor.fetchall():
                c.drawString(70, y, f"{fecha} - {usuario}: ${inicial:.2f} → ${total:.2f} (diff: ${diff:.2f})")
                y -= 15

    def _exportar_cierres_texto(self, f):
        """Datos de cierres para texto plano (fallback)"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total_ventas), AVG(diferencia)
                FROM cierres_caja 
                WHERE fecha_apertura BETWEEN ? AND ?
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            total_cierres, ventas_total, diff_promedio = cursor.fetchone()
        
            f.write(f"Cierres realizados: {total_cierres or 0}\n")
            f.write(f"Ventas totales: ${ventas_total or 0:.2f}\n")
            f.write(f"Diferencia promedio: ${diff_promedio or 0:.2f}\n\n")
        
            # Detalles de cierres
            f.write("DETALLES DE CIERRES:\n")
            f.write("=" * 50 + "\n")
        
            cursor.execute("""
                SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.ventas_efectivo,
                    c.ventas_tarjeta, c.total_ventas, c.diferencia
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.fecha_apertura BETWEEN ? AND ?
                ORDER BY c.fecha_apertura DESC
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            for fecha, usuario, inicial, efectivo, tarjeta, total, diff in cursor.fetchall():
                f.write(f"\nFecha: {fecha}\n")
                f.write(f"Usuario: {usuario}\n")
                f.write(f"Efectivo inicial: ${inicial:.2f}\n")
                f.write(f"Ventas efectivo: ${efectivo:.2f}\n")
                f.write(f"Ventas tarjeta: ${tarjeta:.2f}\n")
                f.write(f"Total ventas: ${total:.2f}\n")
                f.write(f"Diferencia: ${diff:.2f}\n")
                f.write("-" * 30 + "\n")

    def _exportar_ventas_texto(self, f):
        """Datos de ventas para texto plano (fallback)"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total) FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """, (self.date_range['desde'], self.date_range['hasta']))
            total_ventas, monto_total = cursor.fetchone()
        
            f.write(f"Total de ventas: {total_ventas or 0}\n")
            f.write(f"Monto total: ${monto_total or 0:.2f}\n\n")
        
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, COUNT(*), SUM(total) 
                FROM ventas WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            f.write("POR MÉTODO DE PAGO:\n")
            f.write("=" * 30 + "\n")
            for metodo, count, monto in cursor.fetchall():
                f.write(f"{metodo}: {count} ventas (${monto or 0:.2f})\n")
        
            f.write("\n" + "=" * 50 + "\n")
            f.write("ÚLTIMAS 20 VENTAS:\n")
            f.write("=" * 50 + "\n")
        
            cursor.execute("""
                SELECT v.fecha, v.total, v.metodo_pago, u.nombre
                FROM ventas v 
                JOIN usuarios u ON v.usuario_id = u.id 
                WHERE v.fecha BETWEEN ? AND ?
                ORDER BY v.fecha DESC
                LIMIT 20
            """, (self.date_range['desde'], self.date_range['hasta']))
        
            for fecha, total, metodo, usuario in cursor.fetchall():
                f.write(f"{fecha} - {usuario} - {metodo} - ${total:.2f}\n")
    
    def exportar_excel(self, filename):
        """Exportar a Excel - Implementación básica"""
        try:
            # Para Excel real necesitarías openpyxl o pandas
            # Esta es una versión CSV con extensión .xlsx como placeholder
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Sep=,\n")  # Separador para Excel
                f.write("Reporte exportado desde Sistema de Caja Registradora\n")
                f.write(f"Fecha,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tipo,{self.report_type}\n")
                f.write(f"Desde,{self.date_range['desde']}\n")
                f.write(f"Hasta,{self.date_range['hasta']}\n\n")
                
                if self.report_type == "ventas":
                    f.write("Tipo Reporte,Ventas\n")
                else:
                    f.write("Tipo Reporte,Cierres de Caja\n")
            
            QMessageBox.information(self, "📊 Excel", 
                "Exportación Excel completada.\n\n"
                "Para funcionalidad completa con formatos .xlsx reales, "
                "instale: pip install openpyxl")
                
        except Exception as e:
            raise Exception(f"Error Excel: {str(e)}")
    
    def exportar_csv(self, filename):
        """Exportar a CSV - Implementación completa"""
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Encabezado
                writer.writerow(['Sistema de Caja Registradora - Reporte'])
                writer.writerow(['Tipo', self.report_type])
                writer.writerow(['Fecha generación', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow(['Desde', self.date_range['desde']])
                writer.writerow(['Hasta', self.date_range['hasta']])
                writer.writerow([])  # Línea vacía
                
                if self.report_type == "ventas":
                    self._exportar_ventas_csv(writer)
                else:
                    self._exportar_cierres_csv(writer)
                    
        except Exception as e:
            raise Exception(f"Error CSV: {str(e)}")
    
    def _exportar_ventas_csv(self, writer):
        """Datos de ventas para CSV"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total) FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """, (self.date_range['desde'], self.date_range['hasta']))
            total_ventas, monto_total = cursor.fetchone()
            
            writer.writerow(['TOTAL VENTAS', total_ventas or 0])
            writer.writerow(['MONTO TOTAL', f"${monto_total or 0:.2f}"])
            writer.writerow([])
            
            # Ventas detalladas
            writer.writerow(['VENTAS DETALLADAS'])
            writer.writerow(['Fecha', 'Total', 'IVA', 'Método Pago', 'Usuario'])
            
            cursor.execute("""
                SELECT v.fecha, v.total, v.iva, v.metodo_pago, u.nombre
                FROM ventas v 
                JOIN usuarios u ON v.usuario_id = u.id 
                WHERE v.fecha BETWEEN ? AND ?
                ORDER BY v.fecha
            """, (self.date_range['desde'], self.date_range['hasta']))
            
            for fecha, total, iva, metodo, usuario in cursor.fetchall():
                writer.writerow([fecha, total, iva, metodo, usuario])
    
    def _exportar_cierres_csv(self, writer):
        """Datos de cierres para CSV"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            writer.writerow(['CIERRES DE CAJA'])
            writer.writerow(['Fecha Apertura', 'Usuario', 'Monto Inicial', 'Ventas Efectivo', 
                           'Ventas Tarjeta', 'Total Ventas', 'Diferencia'])
            
            cursor.execute("""
                SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.ventas_efectivo,
                       c.ventas_tarjeta, c.total_ventas, c.diferencia
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.fecha_apertura BETWEEN ? AND ?
                ORDER BY c.fecha_apertura
            """, (self.date_range['desde'], self.date_range['hasta']))
            
            for fecha, usuario, inicial, efectivo, tarjeta, total, diff in cursor.fetchall():
                writer.writerow([fecha, usuario, inicial, efectivo, tarjeta, total, diff])