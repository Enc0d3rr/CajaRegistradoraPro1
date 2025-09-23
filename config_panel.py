from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QColorDialog, QFileDialog, QMessageBox, QComboBox, QHeaderView,
    QInputDialog, QFormLayout, QGroupBox
)
from PyQt6.QtGui import QColor, QPixmap
from PyQt6.QtCore import Qt
import os
import json
import sys

class ConfigPanelDialog(QDialog):
    def __init__(self, db_manager, config, parent=None):
        super().__init__(parent)

        # ✅ SOLUCIÓN WINDOWS INMEDIATA PARA DIÁLOGOS
        if sys.platform.startswith('win'):
            self.setStyleSheet("""
                QDialog { 
                    background-color: #f0f0f0 !important; 
                    font-family: "Segoe UI", Arial, sans-serif !important;
                }
                QGroupBox { 
                    background-color: white !important; 
                    border: 1px solid #ccc !important;
                }
                QLabel { 
                    color: #000000 !important; 
                    background-color: transparent !important;
                }
            
            """)

        self.db_manager = db_manager
        self.config = config.copy()  # Copia para trabajar
        self.setWindowTitle("Panel de Configuración - Administrador")
        self.setGeometry(100, 100, 900, 600)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Pestañas
        self.tabs = QTabWidget()
        
        # Pestaña General
        general_tab = QWidget()
        self.setup_general_tab(general_tab)
        self.tabs.addTab(general_tab, "🏢 General")
        
        # Pestaña Apariencia
        appearance_tab = QWidget()
        self.setup_appearance_tab(appearance_tab)
        self.tabs.addTab(appearance_tab, "🎨 Apariencia")
        
        # Pestaña Usuarios
        users_tab = QWidget()
        self.setup_users_tab(users_tab)
        self.tabs.addTab(users_tab, "👥 Usuarios")
        
        layout.addWidget(self.tabs)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px;")
        btn_guardar.clicked.connect(self.guardar_configuracion)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold; padding: 10px;")
        btn_cancelar.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_guardar)
        btn_layout.addWidget(btn_cancelar)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def setup_general_tab(self, tab):
        layout = QVBoxLayout()
        
        group = QGroupBox("Configuración General del Negocio")
        form_layout = QFormLayout()
        
        # Nombre del negocio
        self.nombre_input = QLineEdit(self.config.get('nombre_negocio', ''))
        form_layout.addRow("Nombre del negocio:", self.nombre_input)
        
        # Logo actual
        self.logo_label = QLabel()
        logo_path = self.config.get('logo_path', '')
        if logo_path and os.path.exists(os.path.join('data', logo_path)):
            pixmap = QPixmap(os.path.join('data', logo_path))
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
        form_layout.addRow("Logo actual:", self.logo_label)
        
        # Botón seleccionar logo
        btn_logo = QPushButton("📁 Seleccionar nuevo logo...")
        btn_logo.clicked.connect(self.seleccionar_logo)
        form_layout.addRow("Cambiar logo:", btn_logo)
        
        # Moneda
        self.moneda_combo = QComboBox()
        self.moneda_combo.addItems(["MXN", "USD", "EUR"])
        self.moneda_combo.setCurrentText(self.config.get('moneda', 'MXN'))
        form_layout.addRow("Moneda:", self.moneda_combo)
        
        # Impuestos
        self.impuestos_input = QLineEdit(str(self.config.get('impuestos', 16.0)))
        form_layout.addRow("Impuestos (%):", self.impuestos_input)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch()
        tab.setLayout(layout)
    
    def setup_appearance_tab(self, tab):
        layout = QVBoxLayout()
        
        group = QGroupBox("Personalización de Apariencia")
        form_layout = QFormLayout()
        
        # Color primario
        self.color_primario_btn = QPushButton("🎨 Seleccionar color primario")
        self.color_primario_btn.setStyleSheet(f"background-color: {self.config.get('color_primario', '#3498db')}; color: white;")
        self.color_primario_btn.clicked.connect(self.seleccionar_color_primario)
        form_layout.addRow("Color primario:", self.color_primario_btn)
        
        # Color secundario
        self.color_secundario_btn = QPushButton("🎨 Seleccionar color secundario")
        self.color_secundario_btn.setStyleSheet(f"background-color: {self.config.get('color_secundario', '#2ecc71')}; color: white;")
        self.color_secundario_btn.clicked.connect(self.seleccionar_color_secundario)
        form_layout.addRow("Color secundario:", self.color_secundario_btn)
        
        # Previsualización
        self.preview_label = QLabel("Previsualización de colores")
        self.preview_label.setStyleSheet(f"""
            background-color: {self.config.get('color_primario', '#3498db')};
            color: white;
            padding: 20px;
            font-weight: bold;
            border: 2px solid {self.config.get('color_secundario', '#2ecc71')};
            border-radius: 10px;
        """)
        form_layout.addRow("Previsualización:", self.preview_label)
        
        group.setLayout(form_layout)
        layout.addWidget(group)
        layout.addStretch()
        tab.setLayout(layout)
    
    def setup_users_tab(self, tab):
        layout = QVBoxLayout()
        
        group = QGroupBox("Gestión de Usuarios")
        user_layout = QVBoxLayout()
        
        # Tabla de usuarios
        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(4)
        self.tabla_usuarios.setHorizontalHeaderLabels(["ID", "Nombre", "Usuario", "Rol"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        user_layout.addWidget(self.tabla_usuarios)
        
        # Botones de usuarios
        btn_layout = QHBoxLayout()
        btn_agregar = QPushButton("➕ Agregar Usuario")
        btn_agregar.clicked.connect(self.agregar_usuario)
        btn_editar = QPushButton("✏️ Editar Usuario")
        btn_editar.clicked.connect(self.editar_usuario)
        btn_eliminar = QPushButton("🗑️ Eliminar Usuario")
        btn_eliminar.clicked.connect(self.eliminar_usuario)
        
        btn_layout.addWidget(btn_agregar)
        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_eliminar)
        user_layout.addLayout(btn_layout)
        
        group.setLayout(user_layout)
        layout.addWidget(group)
        
        # Cargar usuarios
        self.cargar_usuarios()
        
        tab.setLayout(layout)
    
    def cargar_usuarios(self):
        """Cargar usuarios en la tabla"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                # Verificar estructura de la tabla
                cursor.execute("PRAGMA table_info(usuarios)")
                columnas = [col[1] for col in cursor.fetchall()]
                print("Columnas de usuarios:", columnas)  # Para debug
            
                # Usar el nombre correcto de la columna
                if 'username' in columnas:
                    cursor.execute("SELECT id, nombre, username, rol FROM usuarios")
                elif 'usuario' in columnas:
                    cursor.execute("SELECT id, nombre, usuario, rol FROM usuarios")
                else:
                    QMessageBox.warning(self, "Error", "No se encuentra columna de usuario")
                    return
            
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
        
            # Pasar solo los parámetros necesarios
            dialog = UserManagerDialog(db_manager=self.db_manager, parent=self)
        
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.cargar_usuarios()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el editor de usuarios: {str(e)}")
    
    def editar_usuario(self):
        """Editar usuario seleccionado"""
        try:

            from user_manager import UserManagerDialog
    
            fila = self.tabla_usuarios.currentRow()
            if fila >= 0:
                id_usuario = int(self.tabla_usuarios.item(fila, 0).text())
        
                # Pasar parámetros simples
                dialog = UserManagerDialog(
                    db_manager=self.db_manager, 
                    user_id=id_usuario,  # Parámetro simple, no objeto
                    parent=self
                )
        
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.cargar_usuarios()
            else:
                QMessageBox.warning(self, "Error", "Selecciona un usuario para editar")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al editar usuario: {str(e)}")
    
    def eliminar_usuario(self):
        """Eliminar usuario seleccionado"""
        fila = self.tabla_usuarios.currentRow()
        if fila >= 0:
            id_usuario = int(self.tabla_usuarios.item(fila, 0).text())
            usuario = self.tabla_usuarios.item(fila, 2).text()
            
            if QMessageBox.question(self, "Confirmar", f"¿Eliminar usuario '{usuario}'?") == QMessageBox.StandardButton.Yes:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
                    conn.commit()
                self.cargar_usuarios()
        else:
            QMessageBox.warning(self, "Error", "Selecciona un usuario para eliminar")
    
    def seleccionar_logo(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar logo", "", 
                "Imágenes (*.png *.jpg *.jpeg *.bmp *.ico)"
            )
            if file_path:
                # Verificar que el archivo sea una imagen válida
                from PIL import Image
                try:
                    with Image.open(file_path) as img:
                        img.verify()  # Verificar que es una imagen válida
                    
                    # Copiar logo a carpeta data
                    import shutil
                    logo_name = os.path.basename(file_path)
                    dest_path = os.path.join('data', logo_name)
                    shutil.copy2(file_path, dest_path)
                    
                    self.config['logo_path'] = logo_name
                    
                    # Actualizar previsualización
                    pixmap = QPixmap(dest_path)
                    if not pixmap.isNull():
                        self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                        QMessageBox.information(self, "Éxito", "Logo actualizado correctamente")
                    else:
                        QMessageBox.warning(self, "Error", "El archivo no es una imagen válida")
                        
                except Exception as img_error:
                    QMessageBox.warning(self, "Error", f"El archivo no es una imagen válida: {img_error}")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el logo: {e}")
    
    def seleccionar_color_primario(self):
        color = QColorDialog.getColor(QColor(self.config.get('color_primario', '#3498db')))
        if color.isValid():
            self.config['color_primario'] = color.name()
            self.color_primario_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
            self.actualizar_preview()
    
    def seleccionar_color_secundario(self):
        color = QColorDialog.getColor(QColor(self.config.get('color_secundario', '#2ecc71')))
        if color.isValid():
            self.config['color_secundario'] = color.name()
            self.color_secundario_btn.setStyleSheet(f"background-color: {color.name()}; color: white;")
            self.actualizar_preview()
    
    def actualizar_preview(self):
        self.preview_label.setStyleSheet(f"""
            background-color: {self.config.get('color_primario', '#3498db')};
            color: white;
            padding: 20px;
            font-weight: bold;
            border: 2px solid {self.config.get('color_secundario', '#2ecc71')};
            border-radius: 10px;
        """)
    
    def guardar_configuracion(self):
        try:
            # Validar nombre no vacío
            nombre_negocio = self.nombre_input.text().strip()
            if not nombre_negocio:
                QMessageBox.warning(self, "Error", "El nombre del negocio no puede estar vacío")
                return
        
            # Validar impuestos (0-100%)
            try:
                impuestos = float(self.impuestos_input.text())
                if impuestos < 0 or impuestos > 100:
                    QMessageBox.warning(self, "Error", "Los impuestos deben estar entre 0 y 100%")
                    return
            except ValueError:
                QMessageBox.warning(self, "Error", "Los impuestos deben ser un número válido")
                return
        
            # ACTUALIZAR self.config con los valores ACTUALES del formulario
            self.config.update({
                'nombre_negocio': nombre_negocio,
                'moneda': self.moneda_combo.currentText(),
                'impuestos': impuestos,
                # Los colores YA deberían estar en self.config desde los métodos de selección
                # pero nos aseguramos de tener los valores actuales
                'color_primario': self.config.get('color_primario', '#3498db'),
                'color_secundario': self.config.get('color_secundario', '#2ecc71'),
                'logo_path': self.config.get('logo_path', '')
            })
        
            print(f"DEBUG - Config a guardar: {self.config}")  # ✅ Para debugging
    
            # Guardar en archivo
            from config_manager import config_manager
            if config_manager.update_config(self.config):
                QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo guardar la configuración")
        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar: {str(e)}")

    def get_updated_config(self):
        """Devolver la configuración actualizada"""
        # Asegurarnos de que tenemos los valores más recientes
        try:
            impuestos = float(self.impuestos_input.text())
        except ValueError:
            impuestos = self.config.get('impuestos', 16.0)
        
        self.config.update({
            'nombre_negocio': self.nombre_input.text().strip(),
            'moneda': self.moneda_combo.currentText(),
            'impuestos': impuestos,
            'color_primario': self.config.get('color_primario', '#3498db'),
            'color_secundario': self.config.get('color_secundario', '#2ecc71'),
            'logo_path': self.config.get('logo_path', '')
        })
        return self.config.copy()