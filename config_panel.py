from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QComboBox, QHeaderView,
    QFormLayout, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, pyqtSignal
import os
import sys

class ConfigPanelDialog(QDialog):

    # SEÑAL PARA NOTIFICAR CAMBIOS
    config_changed = pyqtSignal(dict)

    def __init__(self, db_manager, config, parent=None):
        super().__init__(parent)

        # Estilos para Windows
        if sys.platform.startswith('win'):
            self.setStyleSheet("""
                QDialog { 
                    background-color: #f0f0f0; 
                    font-family: "Segoe UI", Arial, sans-serif;
                }
                QGroupBox { 
                    background-color: white; 
                    border: 1px solid #ccc;
                }
                QLabel { 
                    color: #000000; 
                    background-color: transparent;
                }
            """)

        self.db_manager = db_manager
        self.config = config.copy()
        self.setWindowTitle("Panel de Configuración - Administrador")
        self.setFixedSize(900, 600)  # Usar setFixedSize en lugar de setGeometry
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Sistema de pestañas
        tabs = QTabWidget()
        tabs.addTab(self.crear_pestaña_general(), "🏢 General")
        tabs.addTab(self.crear_pestaña_apariencia(), "🎨 Apariencia")
        tabs.addTab(self.crear_pestaña_usuarios(), "👥 Usuarios")
        
        layout.addWidget(tabs)
        layout.addLayout(self.crear_botones_accion())
        self.setLayout(layout)

    def crear_botones_accion(self):
        """Crear botones de acción"""
        btn_layout = QHBoxLayout()
        
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        btn_guardar.clicked.connect(self.guardar_configuracion)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        return btn_layout

    def crear_pestaña_general(self):
        """Crear pestaña de configuración general"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Grupo de configuración del negocio
        group = QGroupBox("Configuración General del Negocio")
        form_layout = QFormLayout()
        
        self.nombre_input = QLineEdit(self.config.get('nombre_negocio', ''))
        form_layout.addRow("Nombre del negocio:", self.nombre_input)
        
        # Logo
        self.logo_label = QLabel()
        self.actualizar_logo()
        form_layout.addRow("Logo actual:", self.logo_label)
        
        btn_logo = QPushButton("📁 Seleccionar nuevo logo...")
        btn_logo.clicked.connect(self.seleccionar_logo)
        form_layout.addRow("Cambiar logo:", btn_logo)
        
        # Moneda e impuestos
        self.moneda_combo = QComboBox()
        self.moneda_combo.addItems(["MXN", "USD", "EUR"])
        self.moneda_combo.setCurrentText(self.config.get('moneda', 'MXN'))
        form_layout.addRow("Moneda:", self.moneda_combo)
        
        self.impuestos_input = QLineEdit(str(self.config.get('impuestos', 16.0)))
        form_layout.addRow("Impuestos (%):", self.impuestos_input)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab

    def actualizar_logo(self):
        """Actualizar visualización del logo - VERSIÓN MEJORADA"""
        try:
            logo_path = self.config.get('logo_path', '')
            
            if not logo_path:
                self.mostrar_logo_por_defecto()
                return
                
            full_logo_path = os.path.join('data', logo_path)
            
            if os.path.exists(full_logo_path):
                pixmap = QPixmap(full_logo_path)
                if not pixmap.isNull():
                    # Redimensionar manteniendo aspecto
                    pixmap_redimensionada = pixmap.scaled(
                        100, 100, 
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.logo_label.setPixmap(pixmap_redimensionada)
                    print(f"✅ Logo cargado: {logo_path}")
                    return
                else:
                    print(f"❌ No se pudo cargar el logo: {logo_path}")
            
            # Si llegamos aquí, hay un problema con el logo
            self.mostrar_logo_por_defecto()
            
        except Exception as e:
            print(f"❌ Error actualizando logo: {e}")
            self.mostrar_logo_por_defecto()

    def mostrar_logo_por_defecto(self):
        """Mostrar estado por defecto cuando no hay logo"""
        nombre_negocio = self.config.get('nombre_negocio', 'Mi Negocio')
        self.logo_label.setText(f"🏪\n{nombre_negocio[:15]}...")
        self.logo_label.setStyleSheet("""
            color: #7f8c8d; 
            font-style: italic; 
            font-weight: bold;
            font-size: 10px;
            text-align: center;
            border: 1px dashed #bdc3c7;
            padding: 5px;
        """)

    def crear_pestaña_apariencia(self):
        """Crear pestaña de apariencia"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Selector de tema
        group_tema = QGroupBox("Selección de Tema")
        layout_tema = QVBoxLayout()
        
        desc_label = QLabel("Elige el tema de la interfaz. Los cambios requieren reiniciar la aplicación.")
        desc_label.setWordWrap(True)
        layout_tema.addWidget(desc_label)
        
        # Selector de temas
        self.tema_group = QButtonGroup(self)
        self.radio_claro = QRadioButton("🌞 Tema Claro")
        self.radio_oscuro = QRadioButton("🌙 Tema Oscuro")
        
        self.tema_group.addButton(self.radio_claro, 1)
        self.tema_group.addButton(self.radio_oscuro, 2)
        
        # Configurar descripciones
        claro_desc = QLabel("Interfaz luminosa y moderna - Ideal para entornos bien iluminados")
        oscuro_desc = QLabel("Interfaz elegante - Reduce fatiga visual en uso prolongado")
        
        for desc in [claro_desc, oscuro_desc]:
            desc.setStyleSheet("color: #666; padding-left: 10px;")
        
        # Agregar opciones al layout
        for radio, desc in [(self.radio_claro, claro_desc), (self.radio_oscuro, oscuro_desc)]:
            radio_layout = QHBoxLayout()
            radio.setStyleSheet("font-weight: bold; padding: 10px;")
            radio_layout.addWidget(radio)
            radio_layout.addWidget(desc)
            radio_layout.addStretch()
            layout_tema.addLayout(radio_layout)
        
        # Seleccionar tema actual
        tema_actual = self.config.get('tema', 'claro')
        self.radio_oscuro.setChecked(tema_actual == 'oscuro')
        self.radio_claro.setChecked(tema_actual == 'claro')
        
        group_tema.setLayout(layout_tema)
        layout.addWidget(group_tema)
        
        # Previsualización
        group_prev = QGroupBox("Vista Previa")
        layout_prev = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.actualizar_preview_tema()
        layout_prev.addWidget(self.preview_label)
        
        group_prev.setLayout(layout_prev)
        layout.addWidget(group_prev)
        layout.addStretch()
        
        tab.setLayout(layout)
        return tab

    def actualizar_preview_tema(self):
        """Actualizar previsualización del tema"""
        tema_actual = 'oscuro' if self.radio_oscuro.isChecked() else 'claro'
        
        if tema_actual == 'oscuro':
            texto = "🌙 Tema Oscuro: Fondos oscuros, textos claros"
            estilo = """
                background-color: #2d3239; 
                color: #e9ecef; 
                padding: 15px; 
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid #495057;
            """
        else:
            texto = "🌞 Tema Claro: Fondos claros, textos oscuros"
            estilo = """
                background-color: #f8f9fa; 
                color: #212529; 
                padding: 15px; 
                border-radius: 8px;
                font-weight: bold;
                border: 2px solid #dee2e6;
            """
        
        self.preview_label.setText(texto)
        self.preview_label.setStyleSheet(estilo)

    def crear_pestaña_usuarios(self):
        """Crear pestaña de gestión de usuarios"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        group = QGroupBox("Gestión de Usuarios")
        user_layout = QVBoxLayout()
        
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(4)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Nombre", "Usuario", "Rol"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        user_layout.addWidget(self.tabla_usuarios)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        acciones = [
            ("➕ Agregar Usuario", self.agregar_usuario),
            ("✏️ Editar Usuario", self.editar_usuario),
            ("🗑️ Eliminar Usuario", self.eliminar_usuario)
        ]
        
        for texto, funcion in acciones:
            btn = QPushButton(texto)
            btn.clicked.connect(funcion)
            btn_layout.addWidget(btn)
        
        user_layout.addLayout(btn_layout)
        group.setLayout(user_layout)
        layout.addWidget(group)
        
        self.cargar_usuarios()
        tab.setLayout(layout)
        return tab

    def cargar_usuarios(self):
        """Cargar usuarios en la tabla"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                # Determinar nombre de columna de usuario
                cursor.execute("PRAGMA table_info(usuarios)")
                columnas = [col[1] for col in cursor.fetchall()]
                
                columna_usuario = 'username' if 'username' in columnas else 'usuario'
                cursor.execute(f"SELECT id, nombre, {columna_usuario}, rol FROM usuarios")
                
                usuarios = cursor.fetchall()
                self.tabla_usuarios.setRowCount(len(usuarios))
                
                for row, (id_usuario, nombre, username, rol) in enumerate(usuarios):
                    self.tabla_usuarios.setItem(row, 0, QTableWidgetItem(str(id_usuario)))
                    self.tabla_usuarios.setItem(row, 1, QTableWidgetItem(nombre))
                    self.tabla_usuarios.setItem(row, 2, QTableWidgetItem(username))
                    self.tabla_usuarios.setItem(row, 3, QTableWidgetItem(rol))
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar usuarios: {str(e)}")

    def agregar_usuario(self):
        """Agregar nuevo usuario"""
        try:
            from user_manager import UserManagerDialog
            dialog = UserManagerDialog(db_manager=self.db_manager, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.cargar_usuarios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el editor de usuarios: {str(e)}")

    def editar_usuario(self):
        """Editar usuario seleccionado"""
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un usuario para editar")
            return
            
        try:
            from user_manager import UserManagerDialog
            id_usuario = int(self.tabla_usuarios.item(fila, 0).text())
            dialog = UserManagerDialog(db_manager=self.db_manager, user_id=id_usuario, parent=self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.cargar_usuarios()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al editar usuario: {str(e)}")

    def eliminar_usuario(self):
        """Eliminar usuario seleccionado"""
        fila = self.tabla_usuarios.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Selecciona un usuario para eliminar")
            return
            
        id_usuario = int(self.tabla_usuarios.item(fila, 0).text())
        usuario = self.tabla_usuarios.item(fila, 2).text()
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de eliminar al usuario '{usuario}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
                    conn.commit()
                self.cargar_usuarios()
                QMessageBox.information(self, "Éxito", "Usuario eliminado correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el usuario: {str(e)}")

    def seleccionar_logo(self):
        """Seleccionar nuevo logo desde cualquier ubicación - VERSIÓN ROBUSTA"""
        try:
            # Abrir diálogo para seleccionar imagen
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Seleccionar logo del negocio", 
                "",  # Directorio inicial (vacío = directorio por defecto)
                "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico *.svg);;Todos los archivos (*)"
            )
            
            if not file_path:
                return  # Usuario canceló la selección
            
            print(f"🖼️ Imagen seleccionada: {file_path}")
                
            # VERIFICAR QUE SEA UNA IMAGEN VÁLIDA
            try:
                from PIL import Image
                with Image.open(file_path) as img:
                    img.verify()  # Verificar integridad del archivo
                    
                # Volver a abrir para obtener propiedades
                with Image.open(file_path) as img:
                    ancho, alto = img.size
                    formato = img.format
                    print(f"📐 Dimensiones: {ancho}x{alto}, Formato: {formato}")
                    
                    # RECOMENDACIÓN: Verificar tamaño máximo recomendado
                    if ancho > 2000 or alto > 2000:
                        respuesta = QMessageBox.question(
                            self, 
                            "Imagen muy grande", 
                            f"La imagen seleccionada es muy grande ({ancho}x{alto}).\n"
                            f"Se recomienda usar imágenes menores a 1000x1000 píxeles.\n\n"
                            f"¿Desea continuar de todos modos?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if respuesta == QMessageBox.StandardButton.No:
                            return
                            
            except Exception as img_error:
                QMessageBox.warning(
                    self, 
                    "Archivo no válido", 
                    f"El archivo seleccionado no es una imagen válida:\n{img_error}"
                )
                return

            # COPIAR IMAGEN A LA CARPETA DATA CON NOMBRE ÚNICO
            import shutil
            from datetime import datetime
            
            # Crear nombre único para evitar sobreescribir
            nombre_archivo = os.path.basename(file_path)
            nombre_base, extension = os.path.splitext(nombre_archivo)
            
            # Si el archivo ya existe en data/, crear nombre único
            dest_path = os.path.join('data', nombre_archivo)
            contador = 1
            while os.path.exists(dest_path):
                # Verificar si es exactamente el mismo archivo
                if os.path.abspath(file_path) == os.path.abspath(dest_path):
                    print("✅ El archivo seleccionado ya está en la carpeta data/")
                    break
                # Si no es el mismo, crear nuevo nombre
                nuevo_nombre = f"{nombre_base}_{contador}{extension}"
                dest_path = os.path.join('data', nuevo_nombre)
                contador += 1
            else:
                # Solo copiar si no es el mismo archivo
                if os.path.abspath(file_path) != os.path.abspath(dest_path):
                    shutil.copy2(file_path, dest_path)
                    print(f"✅ Logo copiado: {file_path} -> {dest_path}")
                else:
                    print("✅ Usando archivo existente en data/")

            # ACTUALIZAR CONFIGURACIÓN CON EL NOMBRE DEL ARCHIVO (no la ruta completa)
            nombre_final = os.path.basename(dest_path)
            self.config['logo_path'] = nombre_final
            
            # ACTUALIZAR VISUALIZACIÓN DEL LOGO
            self.actualizar_logo()
            
            # MOSTRAR CONFIRMACIÓN
            QMessageBox.information(
                self, 
                "Logo actualizado", 
                f"Logo del negocio actualizado correctamente.\n\n"
                f"Archivo: {nombre_final}\n"
                f"Tamaño: {ancho}x{alto} píxeles"
            )
                    
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo cargar el logo:\n{str(e)}"
            )

    def guardar_configuracion(self):
        """Guardar configuración"""
        try:
            # Validaciones
            nombre_negocio = self.nombre_input.text().strip()
            if not nombre_negocio:
                QMessageBox.warning(self, "Error", "El nombre del negocio no puede estar vacío")
                return
        
            try:
                # CORREGIDO: Usar impuestos_input (que es el campo real)
                impuestos = float(self.impuestos_input.text() or 16.0)
                if impuestos < 0 or impuestos > 100:
                    QMessageBox.warning(self, "Error", "Los impuestos deben estar entre 0 y 100%")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Los impuestos deben ser un número válido")
                return

            # DETERMINAR TEMA SELECCIONADO (de los radio buttons)
            tema_seleccionado = 'oscuro' if self.radio_oscuro.isChecked() else 'claro'

            # ACTUALIZAR CONFIGURACIÓN ACTUAL - USANDO LOS CAMPOS CORRECTOS
            nuevo_config = {
                'nombre_negocio': self.nombre_input.text(),
                'tema': tema_seleccionado,  # ✅ CORREGIDO: Usar el tema de los radio buttons
                'impuestos': impuestos,  # ✅ CORREGIDO: impuestos en lugar de iva
                'moneda': self.moneda_combo.currentText(),  # ✅ CORREGIDO: moneda_combo en lugar de moneda_input
                'logo_path': self.config.get('logo_path', ''),  # ✅ CORREGIDO: Usar self.config
                'telefono': self.config.get('telefono', ''),    # ✅ CORREGIDO: Usar self.config
                'direccion': self.config.get('direccion', '')   # ✅ CORREGIDO: Usar self.config
            }
            
            print(f"✅ Configuración a guardar: {nuevo_config}")  # Para debug
            
            # EMITIR SEÑAL CON LA NUEVA CONFIGURACIÓN
            self.config_changed.emit(nuevo_config)
            
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar: {str(e)}")

    def get_updated_config(self):
        """Obtener configuración actualizada"""
        try:
            impuestos = float(self.impuestos_input.text())
        except ValueError:
            impuestos = self.config.get('impuestos', 16.0)
        
        # DETERMINAR TEMA SELECCIONADO (de los radio buttons)
        tema_seleccionado = 'oscuro' if self.radio_oscuro.isChecked() else 'claro'
        
        return {
            'nombre_negocio': self.nombre_input.text().strip(),
            'moneda': self.moneda_combo.currentText(),
            'impuestos': impuestos,
            'logo_path': self.config.get('logo_path', ''),
            'color_primario': self.config.get('color_primario', '#3498db'),
            'color_secundario': self.config.get('color_secundario', '#2ecc71'),
            'direccion': self.config.get('direccion', ''),
            'telefono': self.config.get('telefono', ''),
            'rfc': self.config.get('rfc', ''),
            'tema': tema_seleccionado  
    }