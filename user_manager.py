from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QInputDialog, QGridLayout
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class UserManagerDialog(QDialog):
    def __init__(self, db_manager, user_id=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id  # ✅ Para edición
        self.setWindowTitle("Gestión de Usuarios")
        self.setGeometry(200, 100, 800, 600)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Tabla de usuarios
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Usuario", "Nombre", "Rol", "Estado"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Formulario para agregar/editar usuarios
        form_layout = QVBoxLayout()
        
        # Campos de entrada
        fields_layout = QGridLayout()
        
        fields_layout.addWidget(QLabel("Usuario:"), 0, 0)
        self.username_input = QLineEdit()
        fields_layout.addWidget(self.username_input, 0, 1)
        
        fields_layout.addWidget(QLabel("Contraseña:"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Dejar vacío para mantener actual")
        fields_layout.addWidget(self.password_input, 1, 1)
        
        fields_layout.addWidget(QLabel("Nombre:"), 2, 0)
        self.nombre_input = QLineEdit()
        fields_layout.addWidget(self.nombre_input, 2, 1)
        
        fields_layout.addWidget(QLabel("Rol:"), 3, 0)
        self.rol_combo = QComboBox()
        self.rol_combo.addItems(["administrador", "vendedor"])
        fields_layout.addWidget(self.rol_combo, 3, 1)
        
        form_layout.addLayout(fields_layout)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_guardar = QPushButton("💾 Guardar Usuario")
        self.btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_guardar.clicked.connect(self.guardar_usuario)
        buttons_layout.addWidget(self.btn_guardar)
        
        self.btn_eliminar = QPushButton("🗑️ Eliminar/Activar")
        self.btn_eliminar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_eliminar.clicked.connect(self.toggle_usuario)
        buttons_layout.addWidget(self.btn_eliminar)
        
        self.btn_cambiar_pass = QPushButton("🔑 Cambiar Contraseña")
        self.btn_cambiar_pass.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.btn_cambiar_pass.clicked.connect(self.cambiar_password)
        buttons_layout.addWidget(self.btn_cambiar_pass)
        
        form_layout.addLayout(buttons_layout)
        layout.addLayout(form_layout)
        
        # Botón cerrar
        btn_cerrar = QPushButton("❌ Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)
        
        self.cargar_usuarios()
        self.limpiar_formulario()
        
        # ✅ CARGAR USUARIO SI SE PROVEE user_id (PARA EDICIÓN)
        if self.user_id:
            self.cargar_usuario_existente()
    
    def cargar_usuario_existente(self):
        """Cargar datos de usuario existente para editar"""
        if not self.user_id:
            return
            
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT username, nombre, rol FROM usuarios WHERE id = ?", (self.user_id,))
                usuario = cursor.fetchone()
                
                if usuario:
                    self.username_input.setText(usuario[0])
                    self.nombre_input.setText(usuario[1])
                    # Buscar el índice del rol en el ComboBox
                    index = self.rol_combo.findText(usuario[2])
                    if index >= 0:
                        self.rol_combo.setCurrentIndex(index)
                    
                    # Deshabilitar username para edición (no se puede cambiar)
                    self.username_input.setEnabled(False)
                    self.password_input.setPlaceholderText("Dejar vacío para mantener la actual")
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudieron cargar los datos del usuario: {e}")
    
    def cargar_usuarios(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, nombre, rol, activo FROM usuarios ORDER BY id")
            usuarios = cursor.fetchall()
            
            self.table.setRowCount(len(usuarios))
            for row, (id_, username, nombre, rol, activo) in enumerate(usuarios):
                self.table.setItem(row, 0, QTableWidgetItem(str(id_)))
                self.table.setItem(row, 1, QTableWidgetItem(username))
                self.table.setItem(row, 2, QTableWidgetItem(nombre))
                self.table.setItem(row, 3, QTableWidgetItem(rol))
                estado = "Activo" if activo else "Inactivo"
                self.table.setItem(row, 4, QTableWidgetItem(estado))
                
                # Colorear filas según estado
                if not activo:
                    for col in range(5):
                        self.table.item(row, col).setBackground(QColor("#ffcccc"))
    
    def limpiar_formulario(self):
        self.username_input.clear()
        self.username_input.setEnabled(True)
        self.password_input.clear()
        self.password_input.setPlaceholderText("Contraseña")
        self.nombre_input.clear()
        self.rol_combo.setCurrentIndex(0)
    
    def get_selected_user(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            return (
                int(self.table.item(selected_row, 0).text()),  # ID
                self.table.item(selected_row, 1).text(),       # Username
                self.table.item(selected_row, 4).text()        # Estado
            )
        return None
    
    def guardar_usuario(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        nombre = self.nombre_input.text().strip()
        rol = self.rol_combo.currentText()
        
        if not all([username, nombre]):
            QMessageBox.warning(self, "Error", "Usuario y nombre son obligatorios")
            return
        
        # ✅ VALIDACIÓN DIFERENTE PARA NUEVOS VS EDITAR
        if not self.user_id and not password:  # Solo para nuevos usuarios
            QMessageBox.warning(self, "Error", "La contraseña es obligatoria para nuevos usuarios")
            return
        
        if password and len(password) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                if self.user_id:
                    # ✅ EDITAR usuario existente
                    if password:
                        cursor.execute(
                            "UPDATE usuarios SET nombre = ?, rol = ?, password = ? WHERE id = ?",
                            (nombre, rol, password, self.user_id)
                        )
                    else:
                        cursor.execute(
                            "UPDATE usuarios SET nombre = ?, rol = ? WHERE id = ?",
                            (nombre, rol, self.user_id)
                        )
                else:
                    # ✅ CREAR nuevo usuario
                    cursor.execute(
                        "INSERT INTO usuarios (username, password, nombre, rol) VALUES (?, ?, ?, ?)",
                        (username, password, nombre, rol)
                    )
                
                conn.commit()
            
            QMessageBox.information(self, "Éxito", "Usuario guardado correctamente")
            self.cargar_usuarios()
            self.limpiar_formulario()
            self.accept()  # Cerrar diálogo después de guardar
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar el usuario: {str(e)}")
    
    def toggle_usuario(self):
        selected = self.get_selected_user()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un usuario")
            return
        
        user_id, username, estado = selected
        
        nuevo_estado = 0 if estado == "Activo" else 1
        accion = "desactivar" if nuevo_estado == 0 else "activar"
        
        if user_id == 1 and nuevo_estado == 0:
            QMessageBox.warning(self, "Error", "No se puede desactivar el usuario admin principal")
            return
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que quiere {accion} al usuario '{username}'?"
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE usuarios SET activo = ? WHERE id = ?",
                        (nuevo_estado, user_id)
                    )
                    conn.commit()
                
                QMessageBox.information(self, "Éxito", f"Usuario {accion}do correctamente")
                self.cargar_usuarios()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo {accion} el usuario: {str(e)}")
    
    def cambiar_password(self):
        selected = self.get_selected_user()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un usuario")
            return
        
        user_id, username, estado = selected
        
        if estado == "Inactivo":
            QMessageBox.warning(self, "Error", "No se puede cambiar contraseña a usuario inactivo")
            return
        
        nueva_password, ok = QInputDialog.getText(
            self, "Cambiar Contraseña", 
            f"Nueva contraseña para '{username}':",
            QLineEdit.EchoMode.Password
        )
        
        if ok and nueva_password:
            if len(nueva_password) < 4:
                QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
                return
            
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE usuarios SET password = ? WHERE id = ?",
                        (nueva_password, user_id)
                    )
                    conn.commit()
                
                QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo cambiar la contraseña: {str(e)}")