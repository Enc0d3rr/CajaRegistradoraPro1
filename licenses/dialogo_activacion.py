# ===== SEGURIDAD AVANZADA =====
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTextEdit,
                             QGroupBox, QFrame, QScrollArea, QWidget, QFileDialog)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
import os
import json
import subprocess
import platform

class DialogoActivacion(QDialog):
    def __init__(self, licencias_manager, parent=None, tema="claro"):
        super().__init__(parent)
        self.licencias_manager = licencias_manager
        self.tema = tema
        self.setWindowTitle("🎫 Activación de Licencia Premium - Seguridad Avanzada")
        self.setFixedSize(800, 700)  # Un poco más grande para nueva información
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
        else:
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

    def init_ui(self):
        self.setStyleSheet(self.obtener_estilo())
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = self.crear_header()
        layout.addLayout(header_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(15)
        
        # NUEVA SECCIÓN: Información del equipo
        equipo_group = self.crear_seccion_equipo()
        content_layout.addWidget(equipo_group)
        
        seguridad_group = self.crear_seccion_seguridad()
        content_layout.addWidget(seguridad_group)
        
        beneficios_group = self.crear_seccion_beneficios()
        content_layout.addWidget(beneficios_group)
        
        activacion_group = self.crear_seccion_activacion()
        content_layout.addWidget(activacion_group)
        
        contacto_group = self.crear_seccion_contacto()
        content_layout.addWidget(contacto_group)
        
        estado_group = self.crear_seccion_estado()
        content_layout.addWidget(estado_group)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(content_widget)
        layout.addWidget(scroll_area)
        
        botones_layout = self.crear_botones()
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_estado)
        self.timer.start(1000)

    def crear_seccion_equipo(self):
        """NUEVA SECCIÓN: Información del equipo actual"""
        group = QGroupBox("🖥️ INFORMACIÓN DE SU EQUIPO")
        
        layout = QVBoxLayout()
        
        # Obtener información del equipo
        equipo_id = getattr(self.licencias_manager, 'equipo_id', 'No disponible')
        sistema = platform.system()
        
        info_text = QTextEdit()
        info_text.setHtml(f"""
            <div style='font-family: Segoe UI, Arial; font-size: 12px;'>
            <p><b>ID Único del Equipo:</b></p>
            <div style='background: #2c3e50; color: white; padding: 10px; border-radius: 5px; font-family: monospace;'>
            {equipo_id}
            </div>
            <p style='margin-top: 10px;'><b>Sistema Operativo:</b> {sistema}</p>
            <p style='color: #e74c3c; font-size: 11px;'>
            ⚠️ <b>IMPORTANTE:</b> Cada licencia está vinculada a este equipo. 
            No puede transferirse a otros equipos.
            </p>
            </div>
        """)
        info_text.setReadOnly(True)
        info_text.setFixedHeight(150)
        
        layout.addWidget(info_text)
        group.setLayout(layout)
        return group

    def crear_seccion_activacion(self):
        group = QGroupBox("🔑 ACTIVAR LICENCIA")
    
        layout = QVBoxLayout()
        
        # ✅ TEXTO PLANO - SIN PROBLEMAS DE HTML
        instrucciones = QLabel()
        instrucciones.setText(
            "Seleccione el archivo de licencia (.json) que recibió.\n\n"
            "🔒 NUEVA SEGURIDAD:\n"
            "• La licencia está VINCULADA a su equipo\n" 
            "• No se puede transferir a otros equipos\n"
            "• Mayor protección contra uso no autorizado"
        )
        instrucciones.setWordWrap(True)
        instrucciones.setStyleSheet("color: #7f8c8d; font-style: italic; line-height: 1.4;")
        layout.addWidget(instrucciones)
        
        # Campo para archivo de licencia
        archivo_layout = QHBoxLayout()
        archivo_layout.addWidget(QLabel("Archivo de licencia:"))
        
        self.input_archivo = QLineEdit()
        self.input_archivo.setPlaceholderText("Seleccione el archivo .json de licencia...")
        self.input_archivo.setReadOnly(True)
        self.input_archivo.setMinimumHeight(40)
        archivo_layout.addWidget(self.input_archivo)
        
        btn_examinar = QPushButton("📁 Examinar")
        btn_examinar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_examinar.clicked.connect(self.examinar_archivo)
        archivo_layout.addWidget(btn_examinar)
        
        layout.addLayout(archivo_layout)
        
        self.label_estado_archivo = QLabel("📁 No se ha seleccionado archivo de licencia")
        self.label_estado_archivo.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        layout.addWidget(self.label_estado_archivo)
        
        group.setLayout(layout)
        return group

    def examinar_archivo(self):
        """Abre diálogo para seleccionar archivo de licencia"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de licencia",
            "",
            "Archivos JSON (*.json);;Todos los archivos (*)"
        )
        
        if archivo:
            self.input_archivo.setText(archivo)
            self.validar_archivo_licencia(archivo)

    def validar_archivo_licencia(self, archivo):
        """Valida el archivo de licencia seleccionado"""
        colores = self.obtener_colores_tema()
        
        if not os.path.exists(archivo):
            self.label_estado_archivo.setText("❌ Archivo no encontrado")
            self.label_estado_archivo.setStyleSheet(f"color: {colores['error']}; font-size: 12px; padding: 5px;")
            self.btn_activar.setEnabled(False)
            return
        
        try:
            import json
            with open(archivo, 'r', encoding='utf-8') as f:
                licencia_data = json.load(f)
            
            # Verificar estructura básica
            if not isinstance(licencia_data, dict):
                raise ValueError("Formato de licencia inválido")
            
            # Verificar campos requeridos
            campos_requeridos = ['codigo', 'hash_seguro', 'datos_encriptados', 'checksum']
            for campo in campos_requeridos:
                if campo not in licencia_data:
                    raise ValueError(f"Falta campo requerido: {campo}")
            
            self.label_estado_archivo.setText("✅ Archivo de licencia válido - Listo para activar")
            self.label_estado_archivo.setStyleSheet(f"color: {colores['exito']}; font-size: 12px; padding: 5px;")
            self.btn_activar.setEnabled(True)
            
        except Exception as e:
            self.label_estado_archivo.setText(f"❌ Error en archivo: {str(e)}")
            self.label_estado_archivo.setStyleSheet(f"color: {colores['error']}; font-size: 12px; padding: 5px;")
            self.btn_activar.setEnabled(False)

    def crear_botones(self):
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        colores = self.obtener_colores_tema()
        
        # Botón de activar
        self.btn_activar = QPushButton("🎫 ACTIVAR LICENCIA")
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
        
        # Botón de obtener ID
        btn_obtener_id = QPushButton("🆔 OBTENER MI ID")
        btn_obtener_id.setStyleSheet(f"""
            QPushButton {{
                background-color: {colores['info']};
                color: white;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.oscurecer_color(colores['info'])};
            }}
        """)
        btn_obtener_id.clicked.connect(self.mostrar_id_equipo)
        btn_obtener_id.setMinimumHeight(45)
        
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
        layout.addWidget(btn_obtener_id)
        layout.addWidget(btn_cancelar)
        
        return layout

    def mostrar_id_equipo(self):
        """Muestra el ID del equipo y cómo obtenerlo"""
        equipo_id = getattr(self.licencias_manager, 'equipo_id', 'No disponible')
        
        mensaje = f"""
        🖥️ <b>ID ÚNICO DE SU EQUIPO</b>
        
        <div style='background: #2c3e50; color: white; padding: 15px; border-radius: 5px; font-family: monospace; margin: 10px 0;'>
        {equipo_id}
        </div>
        
        <b>📋 INSTRUCCIONES PARA OBTENER SU LICENCIA:</b>
        <ol>
        <li>Copie este ID y envíelo al vendedor</li>
        <li>El vendedor generará una licencia VINCULADA a este ID</li>
        <li>Recibirá un archivo .json de licencia</li>
        <li>Seleccione ese archivo aquí para activar</li>
        </ol>
        
        <p style='color: #e74c3c;'>
        ⚠️ <b>IMPORTANTE:</b> Cada licencia es única para este equipo. 
        No puede usarse en otros equipos.
        </p>
        """
        
        QMessageBox.information(self, "ID del Equipo", mensaje)

    def activar_licencia(self):
        """Activa la licencia desde archivo - VERSIÓN MEJORADA CON EQUIPO_ID"""
        archivo_licencia = self.input_archivo.text().strip()
        
        if not archivo_licencia:
            QMessageBox.warning(self, "Error", "Por favor seleccione un archivo de licencia")
            return
        
        if not os.path.exists(archivo_licencia):
            QMessageBox.warning(self, "Error", "El archivo de licencia no existe")
            return
        
        # Deshabilitar botón durante la activación
        self.btn_activar.setEnabled(False)
        self.btn_activar.setText("🔄 ACTIVANDO...")
        
        try:
            # Mostrar información de seguridad
            QMessageBox.information(self, "Activando", 
                                "Validando licencia con seguridad avanzada...\n\n"
                                "🔒 Verificando:\n"
                                "• Integridad del archivo\n"
                                "• Vinculación con este equipo\n"
                                "• Validez de la licencia\n"
                                "• Seguridad multi-capa")
            
            # Intentar activar con el manager de licencias
            resultado, mensaje = self.licencias_manager.activar_licencia(archivo_licencia)
            
            if resultado:
                # ÉXITO: Licencia activada
                equipo_id_licencia = "No disponible"
                try:
                    with open(archivo_licencia, 'r', encoding='utf-8') as f:
                        licencia_data = json.load(f)
                    # Intentar obtener equipo_id de la licencia
                    if 'datos_encriptados' in licencia_data:
                        datos_desencriptados = self.licencias_manager.security.desencriptar_datos(
                            licencia_data['datos_encriptados']
                        )
                        equipo_id_licencia = datos_desencriptados.get('equipo_id', 'No especificado')
                except:
                    pass
                
                mensaje_exito = f"""
                {mensaje}
                
                🎉 ¡LICENCIA PREMIUM ACTIVADA!
                
                🔒 Información de Seguridad:
                • Licencia vinculada a: {equipo_id_licencia[:16]}...
                • Equipo actual: {self.licencias_manager.equipo_id[:16]}...
                • Sistema: {platform.system()}
                
                💎 Beneficios activados:
                • Ventas ilimitadas
                • Todas las funciones premium
                • Seguridad avanzada
                • Soporte prioritario
                
                Reinicie la aplicación para aplicar los cambios.
                """
                
                QMessageBox.information(self, "✅ Activación Exitosa", mensaje_exito)
                self.actualizar_estado()
                self.accept()
                
            else:
                # ERROR: Mostrar detalles SIN HTML
                mensaje_error = f"""
                {mensaje}
                
                🔍 POSIBLES CAUSAS:
                • La licencia no es para este equipo
                • El archivo está corrupto
                • La licencia ya fue usada
                • Problema de seguridad
                
                💡 SOLUCIÓN:
                Contacte al vendedor para obtener una licencia válida para su equipo.
                
                🖥️ SU ID DE EQUIPO: 
                {self.licencias_manager.equipo_id}
                """
                
                QMessageBox.warning(self, "❌ Error de Activación", mensaje_error)
        
        except Exception as e:
            QMessageBox.critical(self, "❌ Error Inesperado", 
                            f"Error durante la activación:\n{str(e)}\n\n"
                            f"Por favor contacte a soporte técnico.")
        
        finally:
            # Restaurar botón
            self.btn_activar.setEnabled(True)
            self.btn_activar.setText("🎫 ACTIVAR LICENCIA")

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
        colores = self.obtener_colores_tema()
        
        if self.tema == "oscuro":
            texto_primario = '#ffffff'
            color_info = '#3498db'
        else:
            texto_primario = '#2c3e50'
            color_info = '#2980b9'
        
        return f"""
            <div style='font-family: Segoe UI, Arial; font-size: 12px; color: {texto_primario};'>
            <p style='color: {color_info}; margin: 0;'><b>🔒 Sistema de Seguridad Mejorado v2.0</b></p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>VINCULACIÓN POR EQUIPO:</b> Licencia única por hardware</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>HMAC-SHA512:</b> Hashes seguros resistentes a colisiones</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>AES-256:</b> Encriptación militar de datos sensibles</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• <b>Validación Multi-capa:</b> 5 niveles de verificación</p>
            </div>
        """

    def obtener_html_beneficios(self):
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
                    📈 VENTAS ILIMITADAS<br>
                    <span style='color: {texto_secundario};'>Sin restricciones de uso - crece sin límites</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    🕒 SIN FECHAS LÍMITE<br>
                    <span style='color: {texto_secundario};'>Usa el software el tiempo que necesites</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    🌟 SOPORTE PRIORITARIO<br>
                    <span style='color: {texto_secundario};'>Atención personalizada y rápida</span>
                    </div>
                </td>
                
                <td style='padding: 8px; vertical-align: top; width: 50%;'>
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    🔄 ACTUALIZACIONES GRATIS<br>
                    <span style='color: {texto_secundario};'>Todas las mejoras incluidas</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    👥 MÚLTIPLES USUARIOS<br>
                    <span style='color: {texto_secundario};'>Gestión completa de equipo</span>
                    </div>
                    
                    <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin: 5px; color: {texto_primario};'>
                    🔒 SEGURIDAD AVANZADA<br>
                    <span style='color: {texto_secundario};'>Protección de nivel empresarial</span>
                    </div>
                </td>
            </tr>
            </table>
            
            <div style='background: {fondo_tarjeta}; padding: 10px; border-radius: 5px; margin-top: 10px; color: {color_exito};'>
            💡 Inversión inteligente: La licencia premium se paga sola con el aumento de productividad y seguridad.
            </div>
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

    def obtener_html_seguridad(self):
        colores = self.obtener_colores_tema()
        
        if self.tema == "oscuro":
            texto_primario = '#ffffff'
            color_info = '#3498db'
        else:
            texto_primario = '#2c3e50'
            color_info = '#2980b9'
        
        return f"""
            <div style='font-family: Segoe UI, Arial; font-size: 12px; color: {texto_primario};'>
            <p style='color: {color_info}; margin: 0;'>🔒 Sistema de Seguridad Mejorado v2.0</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• VINCULACIÓN POR EQUIPO: Licencia única por hardware</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• HMAC-SHA512: Hashes seguros resistentes a colisiones</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• AES-256: Encriptación militar de datos sensibles</p>
            <p style='color: {texto_primario}; margin: 5px 0;'>• Validación Multi-capa: 5 niveles de verificación</p>
            </div>
        """

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
                <td style='padding: 5px;'>📧 Email:</td>
                <td style='padding: 5px;'>enc0d3rservicios@gmail.com</td>
            </tr>
            <tr>
                <td style='padding: 5px;'>📱 WhatsApp:</td>
                <td style='padding: 5px;'>5518604370</td>
            </tr>
            <tr>
                <td style='padding: 5px;'>⏰ Horario:</td>
                <td style='padding: 5px;'>Lunes a Viernes 9:00 - 18:00</td>
            </tr>
            </table>
            
            <p style='margin-top: 10px; color: {color_error};'>
            ⚠️ Importante: Solo acepte licencias de fuentes oficiales. Su seguridad es nuestra prioridad.
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

    def actualizar_estado(self):
        """Actualiza el estado de la licencia - VERSIÓN CORREGIDA"""
        try:
            info = self.licencias_manager.obtener_info_licencia()
            colores = self.obtener_colores_tema()
            
            fondo = ""
            texto = ""
            borde = ""
            
            if info['tipo'] == 'premium':
                fondo = colores['exito'] if self.tema == 'oscuro' else '#d5eddb'
                texto = '#ffffff' if self.tema == 'oscuro' else '#155724'
                borde = self.oscurecer_color(colores['exito'])
                
                # Determinar tipo de plan
                plan = info.get('plan', 'premium')
                if plan == "perpetua":
                    mensaje_plan = "💎 LICENCIA PERPETUA"
                    dias_info = "• Sin expiración"
                elif plan == "anual":
                    mensaje_plan = "📅 SUSCRIPCIÓN ANUAL" 
                    dias_info = f"• Días restantes: <b>{info['dias_restantes']}</b>"
                elif plan == "empresarial":
                    mensaje_plan = "🏢 PLAN EMPRESARIAL"
                    dias_info = "• Sin expiración + Soporte premium"
                else:
                    mensaje_plan = "💎 LICENCIA PREMIUM"
                    dias_info = f"• Días restantes: <b>{info['dias_restantes']}</b>"
                
                mensaje = f"""
                <div style='background: {fondo}; padding: 15px; border-radius: 5px; color: {texto};'>
                <b>{mensaje_plan} ACTIVA</b><br><br>
                • Estado: <b>{info['estado']}</b><br>
                {dias_info}<br>
                • Expira: <b>{info['expiracion']}</b><br>
                • Equipo ID: <b>{self.licencias_manager.equipo_id[:16]}...</b><br>
                • Código: <b>{info['codigo']}</b><br><br>
                <i>¡Disfrute de todas las funciones premium!</i>
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
                    • Equipo ID: <b>{self.licencias_manager.equipo_id[:16]}...</b><br>
                    • Límite total: <b>{getattr(self.licencias_manager, 'limite_ventas_demo', 50)} ventas</b><br><br>
                    <i>Active una licencia premium para uso ilimitado</i>
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
                    • Equipo ID: <b>{self.licencias_manager.equipo_id[:16]}...</b><br>
                    • Límite: <b>{getattr(self.licencias_manager, 'limite_ventas_demo', 50)} ventas</b><br><br>
                    <i>Para continuar, active una licencia premium</i>
                    </div>
                    """
            
            self.label_estado.setText(mensaje)
            self.estado_group.setStyleSheet(f"QGroupBox {{ border: 2px solid {borde}; }}")
            
        except Exception as e:
            error_msg = f"""
            <div style='background: #f8d7da; padding: 15px; border-radius: 5px; color: #721c24;'>
            <b>❌ ERROR CARGANDO ESTADO</b><br><br>
            No se pudo cargar la información de la licencia.<br>
            Error: {str(e)}<br><br>
            <i>Reinicie la aplicación o contacte a soporte.</i>
            </div>
            """
            self.label_estado.setText(error_msg)
            self.estado_group.setStyleSheet("QGroupBox { border: 2px solid #e74c3c; }")

    def oscurecer_color(self, color_hex, porcentaje=20):
        color = QColor(color_hex)
        return color.darker(100 + porcentaje).name()