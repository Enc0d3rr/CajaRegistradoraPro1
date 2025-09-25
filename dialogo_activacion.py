from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTextEdit,
                             QGroupBox, QFrame)
from PyQt6.QtCore import Qt
from datetime import datetime

class DialogoActivacion(QDialog):
    def __init__(self, license_manager, parent=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setWindowTitle("💎 Activación de Licencia Premium")
        self.setFixedSize(600, 600)
        self.setModal(True)  # Diálogo modal
        
        self.setup_ui()
        self.cargar_estado_actual()

    def setup_ui(self):
        """Configurar interfaz - SOLO LICENCIA PREMIUM"""
        try:
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            
            # Título principal
            titulo = QLabel("💎 ACTIVACIÓN DE LICENCIA PREMIUM")
            titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin: 20px;")
            layout.addWidget(titulo)
            
            # Estado actual
            self.estado_label = QLabel("Verificando estado de licencia...")
            self.estado_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.estado_label.setStyleSheet("font-size: 16px; padding: 15px; background-color: #ecf0f1; border-radius: 5px;")
            layout.addWidget(self.estado_label)
            
            # Separador
            separador = QFrame()
            separador.setFrameShape(QFrame.Shape.HLine)
            separador.setStyleSheet("background-color: #bdc3c7; margin: 20px 0;")
            layout.addWidget(separador)
            
            # SECCIÓN DE ACTIVACIÓN PREMIUM
            grupo_activacion = QGroupBox("🔑 ACTIVAR LICENCIA PREMIUM")
            grupo_activacion.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
            layout_activacion = QVBoxLayout()
            
            # Instrucciones
            instrucciones = QLabel(
                "Para usar el software, necesitas una licencia premium válida.\n"
                "Ingresa el código de activación que recibiste al realizar tu compra."
            )
            instrucciones.setStyleSheet("font-size: 14px; line-height: 1.5; margin-bottom: 15px;")
            layout_activacion.addWidget(instrucciones)
            
            # Código de activación
            layout_codigo = QHBoxLayout()
            layout_codigo.addWidget(QLabel("Código de activación:"))
            self.codigo_input = QLineEdit()
            self.codigo_input.setPlaceholderText("CRP1234567890123")
            self.codigo_input.textChanged.connect(self.validar_formato_codigo)
            layout_codigo.addWidget(self.codigo_input)
            layout_activacion.addLayout(layout_codigo)
            
            # Botón activar
            btn_activar = QPushButton("💳 ACTIVAR LICENCIA PREMIUM")
            btn_activar.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6; 
                    color: white; 
                    font-weight: bold; 
                    padding: 12px;
                    border: none;
                    border-radius: 5px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
            """)
            btn_activar.clicked.connect(self.activar_licencia)
            layout_activacion.addWidget(btn_activar)
            
            grupo_activacion.setLayout(layout_activacion)
            layout.addWidget(grupo_activacion)
            
            # SECCIÓN DE INFORMACIÓN DE CONTACTO
            grupo_contacto = QGroupBox("📞 ¿NO TIENES LICENCIA?")
            grupo_contacto.setStyleSheet("QGroupBox { font-weight: bold; color: #2c3e50; }")
            layout_contacto = QVBoxLayout()
            
            contacto_texto = QTextEdit()
            contacto_texto.setHtml("""
            <h3 style="color: #2c3e50;">💼 Contáctanos para adquirir tu licencia:</h3>
            
            <p><strong>📧 Email:</strong> ventas@cajaregistradora.com</p>
            <p><strong>📱 WhatsApp:</strong> +52 55 1234 5678</p>
            <p><strong>🌐 Sitio web:</strong> www.cajaregistradora.com</p>
            
            <h4 style="color: #27ae60;">💵 Licencias Disponibles:</h4>
            <ul>
                <li><strong>1 mes:</strong> $300 MXN</li>
                <li><strong>3 meses:</strong> $800 MXN (¡Ahorra $100!)</li>
                <li><strong>1 año:</strong> $2,800 MXN (¡Ahorra $800!)</li>
                <li><strong>Licencia vitalicia:</strong> $8,000 MXN</li>
            </ul>
            
            <p style="color: #7f8c8d;"><i>💡 Ofrecemos demostraciones personalizadas</i></p>
            """)
            contacto_texto.setReadOnly(True)
            contacto_texto.setMaximumHeight(300)
            layout_contacto.addWidget(contacto_texto)
            
            grupo_contacto.setLayout(layout_contacto)
            layout.addWidget(grupo_contacto)
            
            # Botones de acción
            layout_botones = QHBoxLayout()
            
            btn_cerrar = QPushButton("Cerrar")
            btn_cerrar.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px; border-radius: 5px;")
            btn_cerrar.clicked.connect(self.reject)
            layout_botones.addWidget(btn_cerrar)
            
            layout_botones.addStretch()
            
            layout.addLayout(layout_botones)
            self.setLayout(layout)
            
        except Exception as e:
            print(f"Error en setup_ui: {e}")

    def cargar_estado_actual(self):
        """Cargar estado de licencia"""
        try:
            info = self.license_manager.obtener_info_licencia()
            
            if info['estado'] == 'activa':
                self.estado_label.setText("💎 LICENCIA PREMIUM ACTIVA")
                self.estado_label.setStyleSheet("color: #27ae60; font-size: 16px; padding: 15px; background-color: #d5f4e6; border-radius: 5px;")
            else:
                self.estado_label.setText("❌ LICENCIA NO ACTIVA")
                self.estado_label.setStyleSheet("color: #e74c3c; font-size: 16px; padding: 15px; background-color: #fadbd8; border-radius: 5px;")
                
        except Exception as e:
            print(f"Error cargando estado: {e}")
            self.estado_label.setText("❌ ERROR CARGANDO LICENCIA")

    def validar_formato_codigo(self, texto):
        """Valida el formato del código"""
        if len(texto) > 0:
            if texto.startswith("CRP") and len(texto) <= 16:
                self.codigo_input.setStyleSheet("border: 2px solid #27ae60; padding: 5px;")
            else:
                self.codigo_input.setStyleSheet("border: 2px solid #e74c3c; padding: 5px;")

    def activar_licencia(self):
        """Activa la licencia premium"""
        codigo = self.codigo_input.text().strip()
        
        if not codigo:
            QMessageBox.warning(self, "Código Requerido", "Por favor ingresa un código de activación.")
            return
        
        if len(codigo) != 16 or not codigo.startswith("CRP"):
            QMessageBox.warning(
                self,
                "Código Inválido",
                "El código de activación debe tener:\n"
                "• 16 caracteres de longitud\n"
                "• Comenzar con 'CRP'\n\n"
                "Ejemplo: CRP1234567890123"
            )
            return
        
        if self.license_manager.activar_licencia_paga(codigo):
            QMessageBox.information(
                self,
                "✅ Licencia Activada",
                "¡Licencia premium activada correctamente!\n\n"
                "Ahora puedes usar todas las funciones del software.\n\n"
                "¡Gracias por tu compra!"
            )
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "❌ Error de Activación",
                "El código de activación no es válido.\n\n"
                "Por favor verifica:\n"
                "• Que el código sea correcto\n"
                "• Que no haya espacios\n"
                "• Contacta soporte si el problema persiste"
            )