import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

class EmailSender:
    def __init__(self):
        self.config_path = "data/email_config.json"
        self.cargar_configuracion()
    
    def cargar_configuracion(self):
        """Cargar configuración de email"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            else:
                # Configuración por defecto
                self.config = {
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "email": "",
                    "password": "",
                    "habilitado": False
                }
                self.guardar_configuracion()
        except Exception as e:
            print(f"❌ Error cargando configuración email: {e}")
            self.config = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "email": "",
                "password": "",
                "habilitado": False
            }
    
    def guardar_configuracion(self):
        """Guardar configuración de email"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error guardando configuración email: {e}")
    
    def configurar_email(self, email, password, smtp_server="smtp.gmail.com", smtp_port=587):
        """Configurar credenciales de email"""
        try:
            self.config.update({
                "email": email,
                "password": password,
                "smtp_server": smtp_server,
                "smtp_port": smtp_port,
                "habilitado": True
            })
            self.guardar_configuracion()
            return True, "✅ Configuración de email guardada correctamente"
        except Exception as e:
            return False, f"❌ Error configurando email: {str(e)}"
    
    def enviar_ticket(self, ruta_ticket, email_cliente, numero_venta, total, nombre_negocio):
        """Enviar ticket por correo electrónico - MÉTODO SÍNCRONO (para compatibilidad)"""
        try:
            if not self.config["habilitado"] or not self.config["email"]:
                return False, "❌ Servicio de email no configurado"
            
            if not os.path.exists(ruta_ticket):
                return False, "❌ Archivo de ticket no encontrado"
            
            # Crear mensaje
            msg = MIMEMultipart()
            msg['From'] = self.config["email"]
            msg['To'] = email_cliente
            msg['Subject'] = f"Ticket de Compra #{numero_venta} - {nombre_negocio}"
            
            # Cuerpo del mensaje
            cuerpo = f"""
            Hola,
            
            Adjuntamos su ticket de compra #{numero_venta} de {nombre_negocio}.
            
            📋 Resumen:
            • Número de venta: {numero_venta}
            • Total: ${total:,.2f}
            • Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
            
            Gracias por su compra!
            
            --
            {nombre_negocio}
            """
            
            msg.attach(MIMEText(cuerpo, 'plain'))
            
            # Adjuntar ticket
            with open(ruta_ticket, 'rb') as archivo:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(archivo.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= "ticket_venta_{numero_venta}.txt"'
            )
            msg.attach(part)
            
            # Enviar email
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            server.starttls()
            server.login(self.config["email"], self.config["password"])
            server.send_message(msg)
            server.quit()
            
            return True, f"✅ Ticket enviado a {email_cliente}"
            
        except Exception as e:
            return False, f"❌ Error enviando email: {str(e)}"
    
    def enviar_ticket_async(self, ruta_ticket, email_cliente, numero_venta, total, nombre_negocio):
        """Enviar ticket de forma asíncrona usando QThreadPool"""
        try:
            print(f"📧 Iniciando envío asíncrono a: {email_cliente}")
            
            from email_system.email_thread import EmailWorker
            
            # Crear trabajador para QThreadPool
            email_worker = EmailWorker(
                self.config, 
                ruta_ticket, 
                email_cliente, 
                numero_venta, 
                total, 
                nombre_negocio
            )
            
            print(f"✅ Worker creado: {email_worker}")
            return email_worker
            
        except Exception as e:
            print(f"❌ Error creando worker: {e}")
            import traceback
            traceback.print_exc()
            # Fallback al método sincrónico si hay error
            return self.enviar_ticket(ruta_ticket, email_cliente, numero_venta, total, nombre_negocio)
    
    def probar_conexion(self):
        """Probar conexión con el servidor de email"""
        try:
            if not self.config["habilitado"]:
                return False, "Servicio de email no configurado"
            
            server = smtplib.SMTP(self.config["smtp_server"], self.config["smtp_port"])
            server.starttls()
            server.login(self.config["email"], self.config["password"])
            server.quit()
            
            return True, "✅ Conexión con servidor de email exitosa"
            
        except Exception as e:
            return False, f"❌ Error de conexión: {str(e)}"