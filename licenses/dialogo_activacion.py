# ===== SEGURIDAD AVANZADA =====
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTextEdit,
                             QGroupBox, QFrame, QScrollArea, QWidget)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import os

class DialogoActivacion(QDialog):
    def __init__(self, licencias_manager, parent=None, tema="claro"):
        super().__init__(parent)
        self.licencias_manager = licencias_manager
        self.tema = tema  # 'claro' o 'oscuro'
        self.setWindowTitle("🎫 Activación de Licencia Premium - Seguridad Avanzada")
        self.setFixedSize(750, 650)  # Un poco más grande para nueva información
        self.init_ui()
    
    def obtener_colores_tema(self):
        """Devuelve colores según el tema activo"""
        if self.tema == "oscuro":
            return {
                'fondo_principal': '#1e1e1e',
                'fondo_secundario': '#2d2d2d',
                'fondo_tarjeta': '#3d3d3d',
                'texto_primario': '#ffffff',
                'texto_secundario': '#cccccc',
                'texto_terciario': '#999999',
                'borde': '#555555',
                'exito': '#27ae60',
                'error': '#e74c3c',
                'advertencia': '#f39c12',
                'info': '#3498db',
                'boton_primario': '#2980b9',
                'boton_secundario': '#7f8c8d',
                'boton_exito': '#27ae60',
                'gradiente_primario': ['#3498db', '#2980b9'],
                'gradiente_secundario': ['#2c3e50', '#34495e']
            }
        else:  # tema claro por defecto
            return {
                'fondo_principal': '#f8f9fa',
                'fondo_secundario': '#e9ecef',
                'fondo_tarjeta': '#ffffff',
                'texto_primario': '#2c3e50',
                'texto_secundario': '#7f8c8d',
                'texto_terciario': '#95a5a6',
                'borde': '#bdc3c7',
                'exito': '#27ae60',
                'error': '#e74c3c',
                'advertencia': '#f39c12',
                'info': '#3498db',
                'boton_primario': '#3498db',
                'boton_secundario': '#95a5a6',
                'boton_exito': '#27ae60',
                'gradiente_primario': ['#3498db', '#2c3e50'],
                'gradiente_secundario': ['#ecf0f1', '#bdc3c7']
            }
    
    def obtener_estilo(self):
        """Estilo dinámico según el tema"""
        colores = self.obtener_colores_tema()
        
        return f"""
            QDialog {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                          stop: 0 {colores['fondo_principal']}, 
                                          stop: 1 {colores['fondo_secundario']});
                font-family: 'Segoe UI', Arial, sans-serif;
                color: {colores['texto_primario']};
            }}
            
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {colores['texto_primario']};
                border: 2px solid {colores['borde']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: {colores['fondo_tarjeta']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {colores['texto_primario']};
                background-color: {colores['fondo_tarjeta']};
            }}
            
            QLabel {{
                color: {colores['texto_primario']};
                font-size: 13px;
                background: transparent;
            }}
            
            QLineEdit {{
                padding: 10px;
                border: 2px solid {colores['borde']};
                border-radius: 5px;
                font-size: 14px;
                background-color: {colores['fondo_tarjeta']};
                color: {colores['texto_primario']};
                selection-background-color: {colores['info']};
            }}
            
            QLineEdit:focus {{
                border-color: {colores['info']};
                background-color: {colores['fondo_principal']};
            }}
            
            QLineEdit:disabled {{
                background-color: {colores['fondo_secundario']};
                color: {colores['texto_terciario']};
            }}
            
            QPushButton {{
                padding: 12px 20px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
                color: white;
            }}
            
            QTextEdit {{
                border: 1px solid {colores['borde']};
                border-radius: 5px;
                padding: 10px;
                background-color: {colores['fondo_tarjeta']};
                font-size: 13px;
                color: {colores['texto_primario']};
            }}
            
            QTextEdit:focus {{
                border-color: {colores['info']};
            }}
            
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            
            QScrollBar:vertical {{
                background: {colores['fondo_secundario']};
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {colores['borde']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {colores['texto_terciario']};
            }}
        """
    
    def init_ui(self):
        # Aplicar estilo dinámico
        self.setStyleSheet(self.obtener_estilo())
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con icono
        header_layout = self.crear_header()
        layout.addLayout(header_layout)
        
        # Área de scroll para contenido largo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # Información de seguridad
        seguridad_group = self.crear_seccion_seguridad()
        content_layout.addWidget(seguridad_group)
        
        # Información de beneficios
        beneficios_group = self.crear_seccion_beneficios()
        content_layout.addWidget(beneficios_group)
        
        # Sección de activación
        activacion_group = self.crear_seccion_activacion()
        content_layout.addWidget(activacion_group)
        
        # Información de contacto
        contacto_group = self.crear_seccion_contacto()
        content_layout.addWidget(contacto_group)
        
        # Estado actual
        estado_group = self.crear_seccion_estado()
        content_layout.addWidget(estado_group)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        # Botones de acción
        botones_layout = self.crear_botones()
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)
        
        # Timer para actualizar estado
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_estado)
        self.timer.start(1000)
    
    def crear_header(self):
        layout = QHBoxLayout()
        colores = self.obtener_colores_tema()
        
        titulo = QLabel("ACTIVACIÓN DE LICENCIA PREMIUM\nSEGURIDAD AVANZADA v2.0")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet(f"""
            QLabel {{
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y1: 0,
                                          stop: 0 {colores['gradiente_primario'][0]}, 
                                          stop: 1 {colores['gradiente_primario'][1]});
                border-radius: 10px;
                color: white;
            }}
        """)
        
        layout.addWidget(titulo)
        return layout
    
    def crear_seccion_seguridad(self):
        group = QGroupBox("🛡️ SISTEMA DE SEGURIDAD AVANZADA")
        
        layout = QVBoxLayout()
        
        seguridad_text = QTextEdit()
        seguridad_text.setHtml(self.obtener_html_seguridad())
        seguridad_text.setReadOnly(True)
        seguridad_text.setFixedHeight(120)
        
        layout.addWidget(seguridad_text)
        group.setLayout(layout)
        return group
    
    def obtener_html_seguridad(self):
        """HTML para información de seguridad"""
        colores = self.obtener_colores_tema()
        
        if self.tema == "oscuro":
            texto_primario = '#ffffff'
            color_exito = '#27ae60'
            color_info = '#3498db'
        else:
            texto_primario = '#2c3e50'
            color_exito = '#155724'
            color_info = '#2980b9'
        
        return f"""
            <div style='font-family: Segoe UI, Arial; font-size: 12px; color: {texto_primario};'>
            <p style='color: {color_info}; margin: 0;'><b>🔒 Sistema de Seguridad Mejorado v2.0</b></p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>HMAC-SHA512:</b> Hashes seguros resistentes a colisiones</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>AES-256:</b> Encriptación militar de datos sensibles</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>Validación Multi-capa:</b> 5 niveles de verificación</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>SHA3-512:</b> Checksums para integridad de datos</p>
            </div>
        """
    
    def crear_seccion_beneficios(self):
        group = QGroupBox("💎 BENEFICIOS LICENCIA PREMIUM")
        
        layout = QVBoxLayout()
        
        beneficios_text = QTextEdit()
        beneficios_text.setHtml(self.obtener_html_beneficios())
        beneficios_text.setReadOnly(True)
        beneficios_text.setFixedHeight(200)
        
        layout.addWidget(beneficios_text)
        group.setLayout(layout)
        return group
    
    def obtener_html_beneficios(self):
        """HTML dinámico según el tema"""
        colores = self.obtener_colores_tema()
        
        if self.tema == "oscuro":
            fondo_tarjeta = '#2d2d2d'
            texto_primario = '#ffffff'
            texto_secundario = '#cccccc'
            color_exito = '#27ae60'
            color_info = '#3498db'
        else:
            fondo_tarjeta = '#e8f4fd'
            texto_primario = '#2c3e50'
            texto_secundario = '#7f8c8d'
            color_exito = '#155724'
            color_info = '#2980b9'
        
        return f"""
            <div style='font-family: Segoe UI, Arial; font-size: 13px; color: {texto_primario};'>
            <h3 style='color: {texto_primario}; margin-top: 0;'>¡Desbloquea el poder completo de tu software!</h3>
            
            <table style='width: 100%; border-collapse: collapse;'>
            <tr>
                <td style='padding: 8px; vertical-align: top; width: 50%;'>
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    <b style='color: {color_info};'>📈 VENTAS ILIMITADAS</b><br>
                    <span style='color: {texto_secundario};'>Sin restricciones de uso - crece sin límites</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    <b style='color: {color_info};'>🕒 SIN FECHAS LÍMITE</b><br>
                    <span style='color: {texto_secundario};'>Usa el software el tiempo que necesites</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    <b style='color: {color_info};'>🌟 SOPORTE PRIORITARIO</b><br>
                    <span style='color: {texto_secundario};'>Atención personalizada y rápida</span>
                    </div>
                </td>
                
                <td style='padding: 8px; vertical-align: top; width: 50%;'>
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    <b style='color: {color_info};'>🔄 ACTUALIZACIONES GRATIS</b><br>
                    <span style='color: {texto_secundario};'>Todas las mejoras incluidas</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    <b style='color: {color_info};'>👥 MÚLTIPLES USUARIOS</b><br>
                    <span style='color: {texto_secundario};'>Gestión completa de equipo</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    <b style='color: {color_info};'>🔒 SEGURIDAD AVANZADA</b><br>
                    <span style='color: {texto_secundario};'>Protección de nivel empresarial</span>
                    </div>
                </td>
            </tr>
            </table>
            
            <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin-top: 10px; color: {color_exito};'>
            <b>💡 Inversión inteligente:</b> La licencia premium se paga sola con el aumento de productividad y seguridad.
            </div>
            </div>
        """
    
    def crear_seccion_activacion(self):
        group = QGroupBox("🔑 ACTIVAR LICENCIA")
        
        layout = QVBoxLayout()
        
        # Instrucciones
        instrucciones = QLabel(
            "Ingrese el código de licencia que recibió por email.\n"
            "El código debe tener formato: CAJA-PRO-XXXX-XXXX-XXXX\n\n"
            "🔒 <b>Nueva seguridad:</b> Su licencia será protegida con encriptación AES-256 y validación multi-capa."
        )
        instrucciones.setWordWrap(True)
        instrucciones.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(instrucciones)
        
        # Campo de código
        codigo_layout = QHBoxLayout()
        codigo_layout.addWidget(QLabel("Código de licencia:"))
        
        self.input_licencia = QLineEdit()
        self.input_licencia.setPlaceholderText("Ej: CAJA-PRO-ABC123-XYZ789-DEF456")
        self.input_licencia.textChanged.connect(self.validar_formato_codigo)
        self.input_licencia.setMinimumHeight(40)
        codigo_layout.addWidget(self.input_licencia)
        
        layout.addLayout(codigo_layout)
        
        # Indicador de formato
        self.label_formato = QLabel("⌨️ Ingrese su código de licencia")
        self.label_formato.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        layout.addWidget(self.label_formato)
        
        group.setLayout(layout)
        return group
    
    def crear_seccion_contacto(self):
        group = QGroupBox("📞 ¿NECESITA AYUDA?")
        
        layout = QVBoxLayout()
        
        contacto_text = QTextEdit()
        contacto_text.setHtml(self.obtener_html_contacto())
        contacto_text.setReadOnly(True)
        contacto_text.setFixedHeight(150)
        
        layout.addWidget(contacto_text)
        group.setLayout(layout)
        return group
    
    def obtener_html_contacto(self):
        """HTML dinámico para contacto"""
        colores = self.obtener_colores_tema()
        
        if self.tema == "oscuro":
            texto_primario = '#ffffff'
            texto_secundario = '#cccccc'
            color_error = '#e74c3c'
        else:
            texto_primario = '#2c3e50'
            texto_secundario = '#7f8c8d'
            color_error = '#721c24'
        
        return f"""
            <div style='font-family: Segoe UI, Arial; font-size: 13px; color: {texto_primario};'>
            <p style='color: {texto_primario};'>Estamos aquí para ayudarte a activar tu licencia:</p>
            
            <table style='width: 100%; color: {texto_primario};'>
            <tr>
                <td style='padding: 5px;'><b>📧 Email:</b></td>
                <td style='padding: 5px;'>ventas@cajaregistradora.com</td>
            </tr>
            <tr>
                <td style='padding: 5px;'><b>📱 Teléfono:</b></td>
                <td style='padding: 5px;'>+52 55 1234 5678</td>
            </tr>
            <tr>
                <td style='padding: 5px;'><b>🌐 Sitio web:</b></td>
                <td style='padding: 5px;'>www.cajaregistradora.com</td>
            </tr>
            <tr>
                <td style='padding: 5px;'><b>⏰ Horario:</b></td>
                <td style='padding: 5px;'>Lunes a Viernes 9:00 - 18:00</td>
            </tr>
            </table>
            
            <p style='margin-top: 10px; color: {color_error};'>
            <b>⚠️ Importante:</b> Solo acepte licencias de fuentes oficiales. Su seguridad es nuestra prioridad.
            </p>
            </div>
        """
    
    def crear_seccion_estado(self):
        self.estado_group = QGroupBox("📊 ESTADO ACTUAL DEL SISTEMA")
        
        layout = QVBoxLayout()
        
        self.label_estado = QLabel("Cargando información de seguridad...")
        self.label_estado.setWordWrap(True)
        self.label_estado.setStyleSheet("""
            QLabel {
                padding: 15px;
                border-radius: 5px;
                font-size: 13px;
            }
        """)
        
        layout.addWidget(self.label_estado)
        self.estado_group.setLayout(layout)
        
        self.actualizar_estado()
        return self.estado_group
    
    def crear_botones(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        colores = self.obtener_colores_tema()
        
        # Botón de activar
        self.btn_activar = QPushButton("🎫 ACTIVAR LICENCIA AVANZADA")
        self.btn_activar.setStyleSheet(f"""
            QPushButton {{
                background-color: {colores['boton_exito']};
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.oscurecer_color(colores['boton_exito'])};
            }}
            QPushButton:pressed {{
                background-color: {self.oscurecer_color(colores['boton_exito'], 40)};
            }}
            QPushButton:disabled {{
                background-color: {colores['boton_secundario']};
                color: {colores['texto_terciario']};
            }}
        """)
        self.btn_activar.clicked.connect(self.activar_licencia)
        self.btn_activar.setEnabled(False)
        self.btn_activar.setMinimumHeight(45)
        
        # Botón de validar
        btn_validar = QPushButton("🔄 VALIDAR SEGURIDAD")
        btn_validar.setStyleSheet(f"""
            QPushButton {{
                background-color: {colores['boton_primario']};
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.oscurecer_color(colores['boton_primario'])};
            }}
        """)
        btn_validar.clicked.connect(self.validar_estado)
        btn_validar.setMinimumHeight(45)
        
        # Botón de cancelar
        btn_cancelar = QPushButton("CERRAR")
        btn_cancelar.setStyleSheet(f"""
            QPushButton {{
                background-color: {colores['boton_secundario']};
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.oscurecer_color(colores['boton_secundario'])};
            }}
        """)
        btn_cancelar.clicked.connect(self.reject)
        btn_cancelar.setMinimumHeight(45)
        
        layout.addWidget(self.btn_activar)
        layout.addWidget(btn_validar)
        layout.addWidget(btn_cancelar)
        
        return layout
    
    def oscurecer_color(self, color_hex, porcentaje=20):
        """Oscurece un color hexadecimal"""
        color = QColor(color_hex)
        return color.darker(100 + porcentaje).name()
    
    def validar_formato_codigo(self, texto):
        """Valida el formato del código de licencia"""
        texto = texto.strip()
        colores = self.obtener_colores_tema()
        
        if len(texto) >= 10 and '-' in texto:
            self.label_formato.setText("✅ Formato válido - Listo para activar con seguridad avanzada")
            self.label_formato.setStyleSheet(f"color: {colores['exito']}; font-size: 12px; padding: 5px;")
            self.btn_activar.setEnabled(True)
        elif len(texto) > 0:
            self.label_formato.setText("❌ El código debe tener al menos 10 caracteres y guiones")
            self.label_formato.setStyleSheet(f"color: {colores['error']}; font-size: 12px; padding: 5px;")
            self.btn_activar.setEnabled(False)
        else:
            self.label_formato.setText("⌨️ Ingrese su código de licencia")
            self.label_formato.setStyleSheet(f"color: {colores['texto_terciario']}; font-size: 12px; padding: 5px;")
            self.btn_activar.setEnabled(False)
    
    def actualizar_estado(self):
        """Actualiza la sección de estado con información de seguridad"""
        try:
            info = self.licencias_manager.obtener_info_licencia()
            colores = self.obtener_colores_tema()
            
            seguridad = info.get('seguridad', 'avanzada')
            
            if info['tipo'] == 'premium':
                fondo = colores['exito'] if self.tema == 'oscuro' else '#d5eddb'
                texto = '#ffffff' if self.tema == 'oscuro' else '#155724'
                borde = self.oscurecer_color(colores['exito'])
                
                mensaje = f"""
                <div style='background: {fondo}; padding: 15px; border-radius: 5px; color: {texto};'>
                <b>💎 LICENCIA PREMIUM ACTIVA</b><br><br>
                • Estado: <b>{info['estado']}</b><br>
                • Días restantes: <b>{info['dias_restantes']}</b><br>
                • Expira: <b>{info['expiracion']}</b><br>
                • Seguridad: <b>{seguridad.upper()}</b><br>
                • Código: <b>{info['codigo']}</b><br><br>
                <i>¡Disfrute de todas las funciones premium con seguridad avanzada!</i>
                </div>
                """
            else:
                if info['estado'] == 'activa':
                    fondo = colores['advertencia'] if self.tema == 'oscuro' else '#fff3cd'
                    texto = '#ffffff' if self.tema == 'oscuro' else '#856404'
                    borde = self.oscurecer_color(colores['advertencia'])
                    
                    mensaje = f"""
                    <div style='background: {fondo}; padding: 15px; border-radius: 5px; color: {texto};'>
                    <b>🔬 VERSIÓN DE PRUEBA</b><br><br>
                    • Estado: <b>{info['estado']}</b><br>
                    • Ventas restantes: <b>{info['dias_restantes']}</b><br>
                    • Límite total: <b>{getattr(self.licencias_manager, 'limite_ventas_demo', 5)} ventas</b><br>
                    • Seguridad: <b>{seguridad.upper()}</b><br><br>
                    <i>Active una licencia premium para uso ilimitado con seguridad avanzada</i>
                    </div>
                    """
                else:
                    fondo = colores['error'] if self.tema == 'oscuro' else '#f8d7da'
                    texto = '#ffffff' if self.tema == 'oscuro' else '#721c24'
                    borde = self.oscurecer_color(colores['error'])
                    
                    mensaje = f"""
                    <div style='background: {fondo}; padding: 15px; border-radius: 5px; color: {texto};'>
                    <b>❌ LÍMITE ALCANZADO</b><br><br>
                    • Estado: <b>{info['estado']}</b><br>
                    • Ventas realizadas: <b>{getattr(self.licencias_manager, 'config_demo', {}).get('ventas_realizadas', 0)}</b><br>
                    • Límite: <b>{getattr(self.licencias_manager, 'limite_ventas_demo', 5)} ventas</b><br>
                    • Seguridad: <b>{seguridad.upper()}</b><br><br>
                    <i>Para continuar, active una licencia premium con seguridad avanzada</i>
                    </div>
                    """
            
            self.label_estado.setText(mensaje)
            self.estado_group.setStyleSheet(f"QGroupBox {{ border: 2px solid {borde}; }}")
            
        except Exception as e:
            self.label_estado.setText(f"Error cargando estado: {str(e)}")
    
    def validar_estado(self):
        """Valida el estado actual de la licencia"""
        self.actualizar_estado()
        QMessageBox.information(self, "Estado del Sistema", 
                              "Información de licencia y seguridad actualizada\n\n"
                              "🔒 Sistema de seguridad: AVANZADO v2.0\n"
                              "• HMAC-SHA512 + AES-256 + SHA3-512")
    
    def activar_licencia(self):
        """Activa la licencia ingresada - VERSIÓN MEJORADA"""
        codigo = self.input_licencia.text().strip()
        
        if not codigo:
            QMessageBox.warning(self, "Error", "Por favor ingrese un código de licencia")
            return
        
        # Deshabilitar botón durante la activación
        self.btn_activar.setEnabled(False)
        self.btn_activar.setText("🔄 ACTIVANDO...")
        
        # Mostrar progreso
        QMessageBox.information(self, "Activando", 
                              "Validando y activando licencia con seguridad avanzada...\n\n"
                              "🔒 Aplicando:\n"
                              "• HMAC-SHA512 para integridad\n"
                              "• AES-256 para encriptación\n"
                              "• Validación multi-capa")
        
        try:
            # Intentar activar con el nuevo sistema
            resultado, mensaje = self.licencias_manager.activar_licencia(codigo)
            
            if resultado:
                QMessageBox.information(self, "✅ Activación Exitosa", 
                                      f"{mensaje}\n\n"
                                      f"¡Bienvenido a la versión Premium!\n"
                                      f"🔒 Seguridad avanzada activada:\n"
                                      f"• HMAC-SHA512\n"
                                      f"• AES-256\n" 
                                      f"• Validación multi-capa\n\n"
                                      f"Reinicie la aplicación para aplicar los cambios.")
                self.actualizar_estado()
                self.accept()
            else:
                QMessageBox.warning(self, "❌ Error de Activación", 
                                  f"{mensaje}\n\n"
                                  f"Verifique que el código sea correcto o contacte a soporte.\n"
                                  f"Código ingresado: {codigo}\n\n"
                                  f"🔍 El sistema usa validación de seguridad avanzada.")
        
        except Exception as e:
            # Manejar cualquier error inesperado
            QMessageBox.critical(self, "❌ Error Inesperado", 
                              f"Ocurrió un error inesperado durante la activación:\n{str(e)}\n\n"
                              f"Por favor contacte a soporte técnico.")
        
        finally:
            # ✅ CORRECCIÓN: RESTAURAR SIEMPRE EL BOTÓN
            self.btn_activar.setEnabled(True)
            self.btn_activar.setText("🎫 ACTIVAR LICENCIA AVANZADA")