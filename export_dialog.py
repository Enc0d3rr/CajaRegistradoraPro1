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
    
    def verificar_datos_reporte(self):
        """Verificar si hay datos para el reporte"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # ✅ CORRECCIÓN: Convertir fechas a rango completo del día
                fecha_desde = self.date_range['desde'].split(' ')[0] + ' 00:00:00'
                fecha_hasta = self.date_range['hasta'].split(' ')[0] + ' 23:59:59'
                
                print(f"🎯 Buscando {self.report_type} entre: {fecha_desde} y {fecha_hasta}")
                
                if self.report_type == "ventas":
                    cursor.execute("""
                        SELECT COUNT(*) FROM ventas 
                        WHERE fecha BETWEEN ? AND ?
                    """, (fecha_desde, fecha_hasta))
                else:
                    cursor.execute("""
                        SELECT COUNT(*) FROM cierres_caja 
                        WHERE fecha_apertura BETWEEN ? AND ?
                    """, (fecha_desde, fecha_hasta))
                
                count = cursor.fetchone()[0]
                print(f"✅ {self.report_type} encontrados: {count}")
                return count > 0
                
        except Exception as e:
            print(f"❌ Error verificando datos: {e}")
            return False
    
    def normalizar_fechas_consulta(self):
        """Normalizar formato de fechas para consultas SQL - VERSIÓN DEFINITIVA"""
        try:
            print(f"🔄 Normalizando fechas: {self.date_range}")
            
            # ✅ SIEMPRE usar rango completo del día
            if ' ' in str(self.date_range['desde']):
                # Si ya tiene hora, extraer solo la fecha
                fecha_base = self.date_range['desde'].split(' ')[0]
            else:
                # Si solo tiene fecha, usar directamente
                fecha_base = self.date_range['desde']
            
            fecha_desde = f"{fecha_base} 00:00:00"
            fecha_hasta = f"{fecha_base} 23:59:59"
            
            print(f"📅 Fechas normalizadas: {fecha_desde} -> {fecha_hasta}")
            return {
                'desde': fecha_desde,
                'hasta': fecha_hasta
            }
                
        except Exception as e:
            print(f"❌ Error normalizando fechas: {e}")
            # Fallback seguro
            return {
                'desde': '2000-01-01 00:00:00',
                'hasta': '2030-12-31 23:59:59'
            }
    
    def debug_exportacion(self, formato):
        """Método de diagnóstico para la exportación"""
        print(f"\n🔧 INICIANDO EXPORTACIÓN {formato}")
        print(f"📋 Tipo de reporte: {self.report_type}")
        print(f"📅 Fechas originales: {self.date_range}")
        
        fechas = self.normalizar_fechas_consulta()
        print(f"📅 Fechas normalizadas: {fechas}")
        
        # Verificar datos reales
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            if self.report_type == "ventas":
                cursor.execute("SELECT id, fecha, total FROM ventas WHERE fecha BETWEEN ? AND ?", 
                             (fechas['desde'], fechas['hasta']))
            else:
                cursor.execute("SELECT id, fecha_apertura, total_ventas FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", 
                             (fechas['desde'], fechas['hasta']))
            
            datos = cursor.fetchall()
            print(f"📊 Datos encontrados: {len(datos)} registros")
            for i, dato in enumerate(datos[:3]):  # Mostrar primeros 3
                print(f"   {i+1}. {dato}")
        
        return fechas

    def obtener_total_ventas(self):
        """Obtener total de ventas en BD para diagnóstico"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM ventas")
                return cursor.fetchone()[0]
        except:
            return 0
    
    def exportar_reporte(self):
        formato = self.format_combo.currentText()
        reports_dir = "Reportes"
        os.makedirs(reports_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{reports_dir}/{self.report_type}_{timestamp}"
        
        try:
            # ✅ DIAGNÓSTICO COMPLETO
            print("=" * 50)
            print("🚀 INICIANDO DIAGNÓSTICO DE EXPORTACIÓN")
            fechas = self.debug_exportacion(formato)
            
            # ✅ VERIFICAR DATOS
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.report_type == "ventas":
                    cursor.execute("SELECT COUNT(*) FROM ventas WHERE fecha BETWEEN ? AND ?", 
                                 (fechas['desde'], fechas['hasta']))
                else:
                    cursor.execute("SELECT COUNT(*) FROM cierres_caja WHERE fecha_apertura BETWEEN ? AND ?", 
                                 (fechas['desde'], fechas['hasta']))
                
                count = cursor.fetchone()[0]
                print(f"✅ VERIFICACIÓN: {count} registros encontrados")
                
                if count == 0:
                    QMessageBox.warning(self, "Sin datos", 
                        f"No hay {self.report_type} en el período.\n"
                        f"Fechas: {fechas['desde']} a {fechas['hasta']}\n"
                        f"Pero en BD hay: {self.obtener_total_ventas()} ventas totales")
                    return
            
            # ✅ PROSEGUIR CON EXPORTACIÓN
            print(f"📤 Exportando a {formato}...")
            
            if "PDF" in formato:
                filename = f"{base_filename}.pdf"
                self.exportar_pdf(filename)
                
            elif "Excel" in formato:
                filename = f"{base_filename}.xlsx"
                self.exportar_excel(filename)
                
            elif "CSV" in formato:
                filename = f"{base_filename}.csv"
                self.exportar_csv(filename)
            
            print("✅ Exportación completada aparentemente")
            
            QMessageBox.information(self, "✅ Éxito", 
                f"Reporte exportado correctamente\n\n"
                f"Archivo: {os.path.basename(filename)}\n"
                f"Registros: {count} {self.report_type}\n"
                f"Ubicación: {os.path.abspath(filename)}")
            
        except Exception as e:
            print(f"❌ Error durante exportación: {e}")
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
        
            # ✅ USAR FECHAS NORMALIZADAS
            fechas = self.normalizar_fechas_consulta()
            
            print(f"🔍 Exportando PDF - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
            
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total) FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """, (fechas['desde'], fechas['hasta']))
            total_ventas, monto_total = cursor.fetchone()
        
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, y_position, f"Total de ventas: {total_ventas or 0}")
            c.drawString(50, y_position - 20, f"Monto total: ${monto_total or 0:.2f}")
        
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, COUNT(*), SUM(total) 
                FROM ventas WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
            """, (fechas['desde'], fechas['hasta']))
        
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
            """, (fechas['desde'], fechas['hasta']))
        
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
            
            # ✅ USAR FECHAS NORMALIZADAS
            fechas = self.normalizar_fechas_consulta()
            
            print(f"🔍 Exportando PDF cierres - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
            
            cursor.execute("""
                SELECT COUNT(*), SUM(total_ventas), AVG(diferencia)
                FROM cierres_caja 
                WHERE fecha_apertura BETWEEN ? AND ?
            """, (fechas['desde'], fechas['hasta']))
        
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
            """, (fechas['desde'], fechas['hasta']))
        
            y = y_position - 90
            c.setFont("Helvetica", 10)
            for fecha, usuario, inicial, total, diff in cursor.fetchall():
                c.drawString(70, y, f"{fecha} - {usuario}: ${inicial:.2f} → ${total:.2f} (diff: ${diff:.2f})")
                y -= 15

    def _exportar_cierres_texto(self, f):
        """Datos de cierres para texto plano (fallback)"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # ✅ USAR FECHAS NORMALIZADAS
            fechas = self.normalizar_fechas_consulta()
            
            print(f"🔍 Exportando texto cierres - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
        
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total_ventas), AVG(diferencia)
                FROM cierres_caja 
                WHERE fecha_apertura BETWEEN ? AND ?
            """, (fechas['desde'], fechas['hasta']))
        
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
            """, (fechas['desde'], fechas['hasta']))
        
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
            
            # ✅ USAR FECHAS NORMALIZADAS
            fechas = self.normalizar_fechas_consulta()
            
            print(f"🔍 Exportando texto ventas - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
        
            # Totales generales
            cursor.execute("""
                SELECT COUNT(*), SUM(total) FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """, (fechas['desde'], fechas['hasta']))
            total_ventas, monto_total = cursor.fetchone()
        
            f.write(f"Total de ventas: {total_ventas or 0}\n")
            f.write(f"Monto total: ${monto_total or 0:.2f}\n\n")
        
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, COUNT(*), SUM(total) 
                FROM ventas WHERE fecha BETWEEN ? AND ?
                GROUP BY metodo_pago
            """, (fechas['desde'], fechas['hasta']))
        
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
            """, (fechas['desde'], fechas['hasta']))
        
            for fecha, total, metodo, usuario in cursor.fetchall():
                f.write(f"{fecha} - {usuario} - {metodo} - ${total:.2f}\n")
    
    def exportar_excel(self, filename):
        """Exportar a Excel - Implementación básica"""
        try:
            print(f"🔍 Exportando Excel - {filename}")
            
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
                    self._exportar_ventas_excel(f)
                else:
                    f.write("Tipo Reporte,Cierres de Caja\n")
                    self._exportar_cierres_excel(f)
            
            QMessageBox.information(self, "📊 Excel", 
                "Exportación Excel completada.\n\n"
                "Para funcionalidad completa con formatos .xlsx reales, "
                "instale: pip install openpyxl")
                
        except Exception as e:
            raise Exception(f"Error Excel: {str(e)}")
    
    def _exportar_ventas_excel(self, f):
        """Datos de ventas para Excel"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # ✅ USAR FECHAS NORMALIZADAS
            fechas = self.normalizar_fechas_consulta()
            
            print(f"🔍 Exportando Excel ventas - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
            
            cursor.execute("""
                SELECT COUNT(*), SUM(total) FROM ventas 
                WHERE fecha BETWEEN ? AND ?
            """, (fechas['desde'], fechas['hasta']))
            total_ventas, monto_total = cursor.fetchone()
            
            f.write(f"Total Ventas,{total_ventas or 0}\n")
            f.write(f"Monto Total,${monto_total or 0:.2f}\n\n")
            
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
                f.write(f"{fecha},{total},{iva},{metodo},{usuario}\n")
    
    def _exportar_cierres_excel(self, f):
        """Datos de cierres para Excel"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # ✅ USAR FECHAS NORMALIZADAS
            fechas = self.normalizar_fechas_consulta()
            
            print(f"🔍 Exportando Excel cierres - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
            
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
                f.write(f"{fecha},{usuario},{inicial},{efectivo},{tarjeta},{total},{diff}\n")
    
    def exportar_csv(self, filename):
        """Exportar a CSV - Implementación completa"""
        try:
            print(f"🔍 Exportando CSV - {filename}")
            
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
                    
            print("✅ CSV exportado correctamente")
                    
        except Exception as e:
            raise Exception(f"Error CSV: {str(e)}")
    
    def _exportar_ventas_csv(self, writer):
        """Datos de ventas para CSV"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # ✅ USAR FECHAS NORMALIZADAS
                fechas = self.normalizar_fechas_consulta()
                
                print(f"🔍 Exportando CSV ventas - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
                
                # 1. Primero verificar que hay datos
                cursor.execute("""
                    SELECT COUNT(*), SUM(total) FROM ventas 
                    WHERE fecha BETWEEN ? AND ?
                """, (fechas['desde'], fechas['hasta']))
                
                total_ventas, monto_total = cursor.fetchone()
                print(f"📊 Datos para CSV: {total_ventas} ventas, ${monto_total or 0:.2f}")
                
                if not total_ventas:
                    writer.writerow(['NO HAY VENTAS EN EL PERÍODO SELECCIONADO'])
                    writer.writerow(['Fechas buscadas:', f"{fechas['desde']} a {fechas['hasta']}"])
                    return
                    
                # 2. Escribir encabezados
                writer.writerow(['TOTAL VENTAS', total_ventas])
                writer.writerow(['MONTO TOTAL', f"${monto_total or 0:.2f}"])
                writer.writerow([])
                writer.writerow(['VENTAS DETALLADAS'])
                writer.writerow(['Fecha', 'Total', 'IVA', 'Método Pago', 'Usuario'])
                
                # 3. Obtener ventas detalladas
                cursor.execute("""
                    SELECT v.fecha, v.total, v.iva, v.metodo_pago, u.nombre
                    FROM ventas v 
                    JOIN usuarios u ON v.usuario_id = u.id 
                    WHERE v.fecha BETWEEN ? AND ?
                    ORDER BY v.fecha
                """, (fechas['desde'], fechas['hasta']))
                
                ventas = cursor.fetchall()
                print(f"📝 Escribiendo {len(ventas)} ventas en CSV")
                
                for fecha, total, iva, metodo, usuario in ventas:
                    writer.writerow([fecha, total, iva, metodo, usuario])
                
                print("✅ CSV de ventas exportado correctamente")
                
        except Exception as e:
            print(f"❌ Error en exportación CSV ventas: {e}")
            writer.writerow(['ERROR AL EXPORTAR VENTAS:', str(e)])
    
    def _exportar_cierres_csv(self, writer):
        """Datos de cierres para CSV"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # ✅ USAR FECHAS NORMALIZADAS
                fechas = self.normalizar_fechas_consulta()
                
                print(f"🔍 Exportando CSV cierres - Buscando entre: {fechas['desde']} y {fechas['hasta']}")
                
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
                
                resultados = cursor.fetchall()
                print(f"📈 Cierres encontrados: {len(resultados)}")
                
                for fecha, usuario, inicial, efectivo, tarjeta, total, diff in resultados:
                    writer.writerow([fecha, usuario, inicial, efectivo, tarjeta, total, diff])
                    
                print("✅ CSV de cierres exportado correctamente")
                
        except Exception as e:
            print(f"❌ Error en exportación CSV cierres: {e}")
            writer.writerow(['ERROR AL EXPORTAR CIERRES:', str(e)])

class AutoBackupConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Auto-Backup")
        self.setGeometry(300, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # TODO: Implementar interfaz para configurar auto-backup
        label = QLabel("Configuración de Backup Automático")
        layout.addWidget(label)
        
        self.setLayout(layout)