from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QComboBox, QHeaderView,
    QFormLayout, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import os
import sys

class ConfigPanelDialog(QDialog):
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
        """Actualizar visualización del logo"""
        logo_path = self.config.get('logo_path', '')
        if logo_path and os.path.exists(os.path.join('data', logo_path)):
            pixmap = QPixmap(os.path.join('data', logo_path))
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                return
        self.logo_label.setText("Sin logo")

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
        """Seleccionar nuevo logo"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar logo", "", 
                "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico)"
            )
            if file_path:
                # Verificar que sea una imagen válida
                from PIL import Image
                try:
                    with Image.open(file_path) as img:
                        img.verify()
                    
                    # Copiar logo
                    import shutil
                    logo_name = os.path.basename(file_path)
                    dest_path = os.path.join('data', logo_name)
                    shutil.copy2(file_path, dest_path)
                    
                    self.config['logo_path'] = logo_name
                    self.actualizar_logo()
                    QMessageBox.information(self, "Éxito", "Logo actualizado correctamente")
                        
                except Exception as img_error:
                    QMessageBox.warning(self, "Error", f"El archivo no es una imagen válida: {img_error}")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el logo: {e}")

    def guardar_configuracion(self):
        """Guardar configuración"""
        try:
            # Validaciones
            nombre_negocio = self.nombre_input.text().strip()
            if not nombre_negocio:
                QMessageBox.warning(self, "Error", "El nombre del negocio no puede estar vacío")
                return
        
            try:
                impuestos = float(self.impuestos_input.text())
                if impuestos < 0 or impuestos > 100:
                    QMessageBox.warning(self, "Error", "Los impuestos deben estar entre 0 y 100%")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Los impuestos deben ser un número válido")
                return
    
            # Crear configuración
            nueva_config = {
                'nombre_negocio': nombre_negocio,
                'moneda': self.moneda_combo.currentText(),
                'impuestos': impuestos,
                'logo_path': self.config.get('logo_path', ''),
                'color_primario': self.config.get('color_primario', '#3498db'),
                'color_secundario': self.config.get('color_secundario', '#2ecc71'),
                'direccion': self.config.get('direccion', ''),
                'telefono': self.config.get('telefono', ''),
                'rfc': self.config.get('rfc', ''),
                'tema': 'oscuro' if self.radio_oscuro.isChecked() else 'claro'
            }
    
            # Guardar
            from config_manager import config_manager
            if hasattr(config_manager, 'update_config'):
                resultado = config_manager.update_config(nueva_config)
            else:
                import json
                with open('data/config.json', 'w', encoding='utf-8') as f:
                    json.dump(nueva_config, f, indent=4, ensure_ascii=False)
                resultado = True
    
            if resultado:
                tema = 'oscuro' if self.radio_oscuro.isChecked() else 'claro'
                QMessageBox.information(
                    self, "✅ Configuración Guardada",
                    f"La configuración se ha guardado correctamente.\n\n"
                    f"🎨 Tema seleccionado: {tema.upper()}\n\n"
                    f"⚠️ Cierre y vuelva a abrir la aplicación para aplicar los cambios."
                )
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar la configuración")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar: {str(e)}")

    def get_updated_config(self):
        """Obtener configuración actualizada"""
        try:
            impuestos = float(self.impuestos_input.text())
        except ValueError:
            impuestos = self.config.get('impuestos', 16.0)
        
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
            'tema': 'oscuro' if self.radio_oscuro.isChecked() else 'claro'
        }