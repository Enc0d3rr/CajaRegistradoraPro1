from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt  

class LoginDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle("Iniciar Sesión")
        self.setGeometry(400, 300, 300, 200)
        
        # LÍNEA PARA EL BOTÓN CERRAR (X)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowCloseButtonHint)
        
        # Estilo de la ventana de login
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#3498db"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Usuario:"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        
        layout.addWidget(QLabel("Contraseña:"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_input)
        
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        self.login_button.clicked.connect(self.authenticate)
        layout.addWidget(self.login_button)
        
        self.setLayout(layout)
    
    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos")
            return
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nombre, rol FROM usuarios WHERE username = ? AND password = ? AND activo = 1",
                (username, password)
            )
            user = cursor.fetchone()
        
        if user:
            self.user_data = {
                'id': user[0],
                'nombre': user[1],
                'rol': user[2]
            }
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Credenciales incorrectas o usuario inactivo")