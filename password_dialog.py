from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.setWindowTitle("Cambiar Contraseña")
        self.setGeometry(300, 200, 400, 250)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Contraseña actual
        layout.addWidget(QLabel("Contraseña actual:"))
        self.current_pass = QLineEdit()
        self.current_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.current_pass)
        
        # Nueva contraseña
        layout.addWidget(QLabel("Nueva contraseña:"))
        self.new_pass = QLineEdit()
        self.new_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.new_pass)
        
        # Confirmar nueva contraseña
        layout.addWidget(QLabel("Confirmar nueva contraseña:"))
        self.confirm_pass = QLineEdit()
        self.confirm_pass.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.confirm_pass)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_aceptar = QPushButton("💾 Cambiar Contraseña")
        btn_aceptar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_aceptar.clicked.connect(self.cambiar_contrasena)
        buttons_layout.addWidget(btn_aceptar)
        
        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def cambiar_contrasena(self):
        current = self.current_pass.text().strip()
        new = self.new_pass.text().strip()
        confirm = self.confirm_pass.text().strip()
        
        if not all([current, new, confirm]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        if new != confirm:
            QMessageBox.warning(self, "Error", "Las nuevas contraseñas no coinciden")
            return
        
        if len(new) < 4:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 4 caracteres")
            return
        
        # Verificar contraseña actual
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM usuarios WHERE id = ?", (self.user_id,))
            result = cursor.fetchone()
            
            if not result or result[0] != current:
                QMessageBox.warning(self, "Error", "Contraseña actual incorrecta")
                return
            
            # Actualizar contraseña
            cursor.execute("UPDATE usuarios SET password = ? WHERE id = ?", (new, self.user_id))
            conn.commit()
        
        QMessageBox.information(self, "Éxito", "Contraseña cambiada correctamente")
        self.accept()