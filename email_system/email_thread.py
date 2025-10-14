import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from PyQt6.QtCore import QObject, QRunnable, pyqtSignal

class EmailWorkerSignals(QObject):
    """Señales para comunicación con el hilo principal"""
    email_enviado = pyqtSignal(bool, str)  # (éxito, mensaje)
    progreso = pyqtSignal(str)  # Mensajes de progreso

class EmailWorker(QRunnable):
    """Trabajador para enviar emails usando QThreadPool"""
    
    def __init__(self, config, ruta_ticket, email_cliente, numero_venta, total, nombre_negocio):
        super().__init__()
        self.config = config
        self.ruta_ticket = ruta_ticket
        self.email_cliente = email_cliente
        self.numero_venta = numero_venta
        self.total = total
        self.nombre_negocio = nombre_negocio
        self.signals = EmailWorkerSignals()
        self.setAutoDelete(True)  # ✅ IMPORTANTE: Auto-eliminarse al terminar
    
    def run(self):
        """Ejecutar envío de email en segundo plano"""
        try:
            self.signals.progreso.emit("🔄 Conectando con servidor de email...")
            
            if not self.config["habilitado"] or not self.config["email"]:
                self.signals.email_enviado.emit(False, "❌ Servicio de email no configurado")
                return
            
            if not os.path.exists(self.ruta_ticket):
                self.signals.email_enviado.emit(False, "❌ Archivo de ticket no encontrado")
                return
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]
            msg['To'] = self.email_cliente
            msg['Subject'] = f"Ticket de Compra #{self.numero_venta} - {self.nombre_negocio}"
            
            # USAR FORMATO MONEDA MEXICANA
            total_formateado = self.formato_moneda_mx(self.total)
            
            # Cuerpo del mensaje
            cuerpo = f"""
            Hola,
            
            Adjuntamos su ticket de compra #{self.numero_venta} de {self.nombre_negocio}.
            
            📋 Resumen:
            • Número de venta: {self.numero_venta}
            • Total: {total_formateado}
            • Fecha: {self.get_current_datetime()}
            
            Gracias por su compra!
            
            --
            {self.nombre_negocio}
            """
            
            msg.attach(MIMEText(cuerpo, 'plain'))
            
            self.signals.progreso.emit("📎 Adjuntando ticket...")
            
            # Adjuntar ticket
            with open(self.ruta_ticket, 'rb') as archivo:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(archivo.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename="ticket_venta_{self.numero_venta}.txt"'
            )
            msg.attach(part)
            
            self.signals.progreso.emit("📤 Enviando email...")
            
            # CONEXIÓN OPTIMIZADA CON TIMEOUTS MÁS CORTOS
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"], timeout=15)
            server.starttls()
            server.login(self.config["email"], self.config["password"])
            server.send_message(msg)
            server.quit()
            
            self.signals.email_enviado.emit(True, f"✅ Ticket enviado a {self.email_cliente}")
            
        except smtplib.SMTPException as e:
            self.signals.email_enviado.emit(False, f"❌ Error SMTP: {str(e)}")
        except Exception as e:
            self.signals.email_enviado.emit(False, f"❌ Error enviando email: {str(e)}")
    
    def get_current_datetime(self):
        """Obtener fecha y hora actual formateada"""
        return datetime.now().strftime('%d/%m/%Y %H:%M')
    
    def formato_moneda_mx(self, valor, simbolo="$", decimales=2):
        """
        Formatea un número al formato de moneda mexicana
        Ejemplo: 13000 -> "$13,000.00"
        """
        try:
            valor_float = float(valor)
            
            # Formatear correctamente con separadores de miles
            formatted = f"{valor_float:,.{decimales}f}"
            
            # Asegurar el formato mexicano: $1,200.00 (no $1200.00)
            return f"{simbolo}{formatted}"
            
        except (ValueError, TypeError):
            return f"{simbolo}0.00"