import os
import csv
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from database import DatabaseManager
from utils.helpers import formato_moneda_mx  # ✅ IMPORTACIÓN AÑADIDA

class ExportDialog(QDialog):
    def __init__(self, parent=None, report_type="ventas", date_range=None):
        super().__init__(parent)
        self.report_type = report_type
        self.date_range = date_range or {
            'desde': datetime.now().strftime('%Y-%m-%d 00:00:00'),
            'hasta': datetime.now().strftime('%Y-%m-%d 23:59:59')
        }
        self.db_manager = DatabaseManager()
        
        self.setWindowTitle(f"Exportar Reporte de {report_type.title()}")
        self.setGeometry(300, 200, 400, 200)
        
        layout = QVBoxLayout()
        
        # Selección de formato
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PDF (Recomendado)", "Excel (.xlsx)", "CSV (.csv)"])
        format_layout.addWidget(self.format_combo)
        layout.addLayout(format_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        self.export_btn = QPushButton("Exportar")
        self.export_btn.clicked.connect(self.exportar_reporte)
        self.cancel_btn = QPushButton("Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.export_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
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
        """Normalizar formato de fechas para consultas SQL"""
        try:
            if ' ' in str(self.date_range['desde']):
                fecha_base = self.date_range['desde'].split(' ')[0]
            else:
                fecha_base = self.date_range['desde']
            
            fecha_desde = f"{fecha_base} 00:00:00"
            fecha_hasta = f"{fecha_base} 23:59:59"
            
            return {'desde': fecha_desde, 'hasta': fecha_hasta}
                
        except Exception as e:
            return {'desde': '2000-01-01 00:00:00', 'hasta': '2030-12-31 23:59:59'}
    
    def exportar_reporte(self):
        formato = self.format_combo.currentText()
        reports_dir = "Reportes"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{reports_dir}/{self.report_type}_{timestamp}"
        
        try:
            fechas = self.normalizar_fechas_consulta()
            
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.report_type == "ventas":
                    cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha BETWEEN ? AND ?", (fechas['desde'], fechas['hasta']))
                else:
                    cursor.execute("SELECT COUNT(*) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", (fechas['desde'], fechas['hasta']))
                
                count = cursor.fetchone()[0]
                
                if count == 0:
                    QMessageBox.warning(self, "Sin datos", f"No hay {self.report_type} en el período seleccionado.")
                    return
            
            if "PDF" in formato:
                filename = f"{base_filename}.pdf"
                self.exportar_pdf(filename)
            elif "Excel" in formato:
                filename = f"{base_filename}.xlsx"
                self.exportar_excel(filename)
            elif "CSV" in formato:
                filename = f"{base_filename}.csv"
                self.exportar_csv(filename)
            
            QMessageBox.information(self, "✅ Éxito", f"Reporte exportado correctamente\n\nArchivo: {os.path.basename(filename)}")
            
        except Exception as e:
            QMessageBox.critical(self, "❌ Error", f"No se pudo exportar: {str(e)}")
    
    def exportar_pdf(self, filename):
        """Exportar a PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(filename, pagesize=letter)
            width, height = letter

            # Encabezado
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, f"REPORTE DE {self.report_type.upper()}")

            c.setFont("Helvetica", 12)
            c.drawString(50, height - 70, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            c.drawString(50, height - 85, f"Período: {self.date_range['desde']} a {self.date_range['hasta']}")

            c.line(50, height - 95, width - 50, height - 95)
            
            y_position = height - 120
            
            if self.report_type == "ventas":
                self._exportar_ventas_pdf(c, y_position)
            else:
                self._exportar_cierres_pdf(c, y_position)
            
            c.save()
            
        except ImportError:
            self._exportar_pdf_texto_plano(filename)
        except Exception as e:
            raise Exception(f"Error PDF: {str(e)}")
        
    def _exportar_pdf_texto_plano(self, filename):
        """Fallback para PDF de texto plano"""
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
    
        QMessageBox.information(self, "📄 Exportado como Texto", 
            "Se generó un archivo de texto (.txt) en lugar de PDF.\n\nPara PDFs con formato avanzado, instale: pip install reportlab")
    
    def _exportar_ventas_pdf(self, c, y_position):
        """Datos de ventas para PDF con reportlab"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            fechas = self.normalizar_fechas_consulta()
            
            # Totales generales
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ?", (fechas['desde'], fechas['hasta']))
            total_ventas, monto_total = cursor.fetchone()
        
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"Total de ventas: {total_ventas or 0}")
            
            # ✅ CAMBIO: Formateo de moneda
            monto_total_formateado = formato_moneda_mx(monto_total or 0)
            c.drawString(50, y_position - 20, f"Monto total: {monto_total_formateado}")
        
            # Por método de pago
            cursor.execute("SELECT metodo_pago, COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ? GROUP BY metodo_pago", 
                         (fechas['desde'], fechas['hasta']))
        
            y = y_position - 40
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y, "Por método de pago:")
        
            y -= 20
            c.setFont("Helvetica", 10)
            for metodo, count, monto in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                monto_formateado = formato_moneda_mx(monto or 0)
                c.drawString(70, y, f"{metodo}: {count} ventas ({monto_formateado})")
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
                ORDER BY v.fecha DESC LIMIT 10
            """, (fechas['desde'], fechas['hasta']))
        
            c.setFont("Helvetica", 8)
            for fecha, total, metodo, usuario in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                total_formateado = formato_moneda_mx(total)
                texto = f"{fecha} - {usuario} - {metodo} - {total_formateado}"
                if len(texto) > 80:
                    texto = texto[:77] + "..."
                c.drawString(70, y, texto)
                y -= 12
    
    def _exportar_cierres_pdf(self, c, y_position):
        """Datos de cierres para PDF con reportlab"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            fechas = self.normalizar_fechas_consulta()
            
            cursor.execute("SELECT COUNT(*), SUM(total_ventas), AVG(diferencia) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", 
                         (fechas['desde'], fechas['hasta']))
        
            total_cierres, ventas_total, diff_promedio = cursor.fetchone()
        
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"Cierres realizados: {total_cierres or 0}")
            
            # ✅ CAMBIO: Formateo de moneda
            ventas_total_formateado = formato_moneda_mx(ventas_total or 0)
            diff_promedio_formateado = formato_moneda_mx(diff_promedio or 0)
            c.drawString(50, y_position - 20, f"Ventas totales: {ventas_total_formateado}")
            c.drawString(50, y_position - 40, f"Diferencia promedio: {diff_promedio_formateado}")
        
            # Detalles de cierres
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position - 70, "Detalles de cierres:")
        
            cursor.execute("""
                SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.total_ventas, c.diferencia
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.fecha_apertura BETWEEN ? AND ?
                ORDER BY c.fecha_apertura DESC LIMIT 10
            """, (fechas['desde'], fechas['hasta']))
        
            y = y_position - 90
            c.setFont("Helvetica", 10)
            for fecha, usuario, inicial, total, diff in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                inicial_formateado = formato_moneda_mx(inicial)
                total_formateado = formato_moneda_mx(total)
                diff_formateado = formato_moneda_mx(diff)
                c.drawString(70, y, f"{fecha} - {usuario}: {inicial_formateado} → {total_formateado} (diff: {diff_formateado})")
                y -= 15

    def _exportar_ventas_texto(self, f):
        """Datos de ventas para texto plano"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            fechas = self.normalizar_fechas_consulta()
        
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ?", (fechas['desde'], fechas['hasta']))
            total_ventas, monto_total = cursor.fetchall()
        
            # ✅ CAMBIO: Formateo de moneda
            monto_total_formateado = formato_moneda_mx(monto_total or 0)
            f.write(f"Total de ventas: {total_ventas or 0}\n")
            f.write(f"Monto total: {monto_total_formateado}\n\n")
        
            cursor.execute("SELECT metodo_pago, COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ? GROUP BY metodo_pago", 
                         (fechas['desde'], fechas['hasta']))
        
            f.write("POR MÉTODO DE PAGO:\n")
            f.write("=" * 30 + "\n")
            for metodo, count, monto in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                monto_formateado = formato_moneda_mx(monto or 0)
                f.write(f"{metodo}: {count} ventas ({monto_formateado})\n")
        
            f.write("\n" + "=" * 50 + "\n")
            f.write("ÚLTIMAS 20 VENTAS:\n")
            f.write("=" * 50 + "\n")
        
            cursor.execute("""
                SELECT v.fecha, v.total, v.metodo_pago, u.nombre
                FROM ventas v 
                JOIN usuarios u ON v.usuario_id = u.id 
                WHERE v.fecha BETWEEN ? AND ?
                ORDER BY v.fecha DESC LIMIT 20
            """, (fechas['desde'], fechas['hasta']))
        
            for fecha, total, metodo, usuario in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                total_formateado = formato_moneda_mx(total)
                f.write(f"{fecha} - {usuario} - {metodo} - {total_formateado}\n")
    
    def _exportar_cierres_texto(self, f):
        """Datos de cierres para texto plano"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            fechas = self.normalizar_fechas_consulta()
        
            cursor.execute("SELECT COUNT(*), SUM(total_ventas), AVG(diferencia) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", 
                         (fechas['desde'], fechas['hasta']))
        
            total_cierres, ventas_total, diff_promedio = cursor.fetchone()
        
            # ✅ CAMBIO: Formateo de moneda
            ventas_total_formateado = formato_moneda_mx(ventas_total or 0)
            diff_promedio_formateado = formato_moneda_mx(diff_promedio or 0)
            
            f.write(f"Cierres realizados: {total_cierres or 0}\n")
            f.write(f"Ventas totales: {ventas_total_formateado}\n")
            f.write(f"Diferencia promedio: {diff_promedio_formateado}\n\n")
        
            f.write("DETALLES DE CIERRES:\n")
            f.write("=" * 50 + "\n")
        
            cursor.execute("""
                SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.ventas_efectivo,
                    c.ventas_tarjeta, c.total_ventas, c.diferencia
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.fecha_apertura BETWEEN ? AND ?
                ORDER BY c.fecha_apertura DESC
            """, (fechas['desde'], fechas['hasta']))
        
            for fecha, usuario, inicial, efectivo, tarjeta, total, diff in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                inicial_formateado = formato_moneda_mx(inicial)
                efectivo_formateado = formato_moneda_mx(efectivo)
                tarjeta_formateado = formato_moneda_mx(tarjeta)
                total_formateado = formato_moneda_mx(total)
                diff_formateado = formato_moneda_mx(diff)
                
                f.write(f"\nFecha: {fecha}\n")
                f.write(f"Usuario: {usuario}\n")
                f.write(f"Efectivo inicial: {inicial_formateado}\n")
                f.write(f"Ventas efectivo: {efectivo_formateado}\n")
                f.write(f"Ventas tarjeta: {tarjeta_formateado}\n")
                f.write(f"Total ventas: {total_formateado}\n")
                f.write(f"Diferencia: {diff_formateado}\n")
                f.write("-" * 30 + "\n")

    def exportar_excel(self, filename):
        """Exportar a Excel"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Sep=,\n")
                f.write("Reporte exportado desde Sistema de Caja Registradora\n")
                f.write(f"Fecha,{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Tipo,{self.report_type}\n")
                f.write(f"Desde,{self.date_range['desde']}\n")
                f.write(f"Hasta,{self.date_range['hasta']}\n\n")
                
                if self.report_type == "ventas":
                    f.write("Tipo Reporte,Ventas\n")
                    self._exportar_ventas_excel(f)
                else:
                    f.write("Tipo Reporte,Cierres de Caja\n")
                    self._exportar_cierres_excel(f)
            
            QMessageBox.information(self, "📊 Excel", "Exportación Excel completada.")
                
        except Exception as e:
            raise Exception(f"Error Excel: {str(e)}")
    
    def _exportar_ventas_excel(self, f):
        """Datos de ventas para Excel"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            fechas = self.normalizar_fechas_consulta()
            
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ?", 
                         (fechas['desde'], fechas['hasta']))
            total_ventas, monto_total = cursor.fetchone()
            
            # ✅ CAMBIO: Formateo de moneda
            monto_total_formateado = formato_moneda_mx(monto_total or 0)
            f.write(f"Total Ventas,{total_ventas or 0}\n")
            f.write(f"Monto Total,{monto_total_formateado}\n\n")
            
            f.write("Detalle de Ventas\n")
            f.write("Fecha,Total,IVA,Método Pago,Usuario\n")
            
            cursor.execute("""
                SELECT v.fecha, v.total, v.iva, v.metodo_pago, u.nombre
                FROM ventas v 
                JOIN usuarios u ON v.usuario_id = u.id 
                WHERE v.fecha BETWEEN ? AND ?
                ORDER BY v.fecha
            """, (fechas['desde'], fechas['hasta']))
            
            for fecha, total, iva, metodo, usuario in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                total_formateado = formato_moneda_mx(total)
                f.write(f"{fecha},{total_formateado},{iva},{metodo},{usuario}\n")
    
    def _exportar_cierres_excel(self, f):
        """Datos de cierres para Excel"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            fechas = self.normalizar_fechas_consulta()
            
            f.write("Detalle de Cierres de Caja\n")
            f.write("Fecha Apertura,Usuario,Monto Inicial,Ventas Efectivo,Ventas Tarjeta,Total Ventas,Diferencia\n")
            
            cursor.execute("""
                SELECT c.fecha_apertura, u.nombre, c.monto_inicial, c.ventas_efectivo,
                       c.ventas_tarjeta, c.total_ventas, c.diferencia
                FROM cierres_caja c
                JOIN usuarios u ON c.usuario_id = u.id
                WHERE c.fecha_apertura BETWEEN ? AND ?
                ORDER BY c.fecha_apertura
            """, (fechas['desde'], fechas['hasta']))
            
            for fecha, usuario, inicial, efectivo, tarjeta, total, diff in cursor.fetchall():
                # ✅ CAMBIO: Formateo de moneda
                inicial_formateado = formato_moneda_mx(inicial)
                efectivo_formateado = formato_moneda_mx(efectivo)
                tarjeta_formateado = formato_moneda_mx(tarjeta)
                total_formateado = formato_moneda_mx(total)
                diff_formateado = formato_moneda_mx(diff)
                f.write(f"{fecha},{usuario},{inicial_formateado},{efectivo_formateado},{tarjeta_formateado},{total_formateado},{diff_formateado}\n")
    
    def exportar_csv(self, filename):
        """Exportar a CSV"""
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                writer.writerow(['Sistema de Caja Registradora - Reporte'])
                writer.writerow(['Tipo', self.report_type])
                writer.writerow(['Fecha generación', datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
                writer.writerow(['Desde', self.date_range['desde']])
                writer.writerow(['Hasta', self.date_range['hasta']])
                writer.writerow([])
                
                if self.report_type == "ventas":
                    self._exportar_ventas_csv(writer)
                else:
                    self._exportar_cierres_csv(writer)
                    
        except Exception as e:
            raise Exception(f"Error CSV: {str(e)}")
    
    def _exportar_ventas_csv(self, writer):
        """Datos de ventas para CSV"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                fechas = self.normalizar_fechas_consulta()
                
                cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha BETWEEN ? AND ?", 
                             (fechas['desde'], fechas['hasta']))
                
                total_ventas, monto_total = cursor.fetchone()
                
                if not total_ventas:
                    writer.writerow(['NO HAY VENTAS EN EL PERÍODO SELECCIONADO'])
                    return
                    
                # ✅ CAMBIO: Formateo de moneda
                monto_total_formateado = formato_moneda_mx(monto_total or 0)
                writer.writerow(['TOTAL VENTAS', total_ventas])
                writer.writerow(['MONTO TOTAL', monto_total_formateado])
                writer.writerow([])
                writer.writerow(['VENTAS DETALLADAS'])
                writer.writerow(['Fecha', 'Total', 'IVA', 'Método Pago', 'Usuario'])
                
                cursor.execute("""
                    SELECT v.fecha, v.total, v.iva, v.metodo_pago, u.nombre
                    FROM ventas v 
                    JOIN usuarios u ON v.usuario_id = u.id 
                    WHERE v.fecha BETWEEN ? AND ?
                    ORDER BY v.fecha
                """, (fechas['desde'], fechas['hasta']))
                
                for fecha, total, iva, metodo, usuario in cursor.fetchall():
                    # ✅ CAMBIO: Formateo de moneda
                    total_formateado = formato_moneda_mx(total)
                    writer.writerow([fecha, total_formateado, iva, metodo, usuario])
                
        except Exception as e:
            writer.writerow(['ERROR AL EXPORTAR VENTAS:', str(e)])
    
    def _exportar_cierres_csv(self, writer):
        """Datos de cierres para CSV"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                fechas = self.normalizar_fechas_consulta()
                
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
                """, (fechas['desde'], fechas['hasta']))
                
                for fecha, usuario, inicial, efectivo, tarjeta, total, diff in cursor.fetchall():
                    # ✅ CAMBIO: Formateo de moneda
                    inicial_formateado = formato_moneda_mx(inicial)
                    efectivo_formateado = formato_moneda_mx(efectivo)
                    tarjeta_formateado = formato_moneda_mx(tarjeta)
                    total_formateado = formato_moneda_mx(total)
                    diff_formateado = formato_moneda_mx(diff)
                    writer.writerow([fecha, usuario, inicial_formateado, efectivo_formateado, tarjeta_formateado, total_formateado, diff_formateado])
                    
        except Exception as e:
            writer.writerow(['ERROR AL EXPORTAR CIERRES:', str(e)])

class AutoBackupConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Auto-Backup")
        self.setGeometry(300, 200, 400, 300)
        
        layout = QVBoxLayout()
        label = QLabel("Configuración de Backup Automático")
        layout.addWidget(label)
        self.setLayout(layout)