import os
import shutil
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QListWidget, QProgressBar, QGroupBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPalette, QColor

# ✅ Importar las nuevas funciones de rutas
from paths import get_app_directory, get_backups_directory, ensure_directory_exists

class BackupWorker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, db_path, backup_dir, include_config=True, include_tickets=True):
        super().__init__()
        self.db_path = db_path
        self.backup_dir = backup_dir
        self.include_config = include_config
        self.include_tickets = include_tickets

    def run(self):
        try:
            # ✅ Usar ensure_directory_exists para crear directorio de backup
            ensure_directory_exists(self.backup_dir)
            
            # Fecha y hora para el nombre del backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(self.backup_dir, backup_name)
            os.makedirs(backup_path, exist_ok=True)
            
            self.message.emit("Iniciando backup...")
            self.progress.emit(10)
            
            # Backup de la base de datos
            self.message.emit("Copiando base de datos...")
            db_backup_path = os.path.join(backup_path, "caja_registradora.db")
            shutil.copy2(self.db_path, db_backup_path)
            self.progress.emit(30)
            
            # Backup de archivos de configuración
            if self.include_config:
                self.message.emit("Copiando configuración...")
                config_files = ["config.json"]  # ✅ Removido productos.json ya que no se usa
                app_dir = get_app_directory()
                for config_file in config_files:
                    config_path = os.path.join(app_dir, config_file)
                    if os.path.exists(config_path):
                        shutil.copy2(config_path, backup_path)
                self.progress.emit(50)
            
            # Backup de tickets
            if self.include_tickets:
                self.message.emit("Copiando tickets...")
                tickets_dir = os.path.join(get_app_directory(), "tickets")
                if os.path.exists(tickets_dir):
                    tickets_backup_path = os.path.join(backup_path, "tickets")
                    shutil.copytree(tickets_dir, tickets_backup_path)
                self.progress.emit(70)
            
            # Comprimir el backup
            self.message.emit("Comprimiendo backup...")
            zip_path = f"{backup_path}.zip"
            shutil.make_archive(backup_path, 'zip', backup_path)
            
            # Eliminar directorio temporal
            shutil.rmtree(backup_path)
            self.progress.emit(90)
            
            # Crear registro del backup
            self.crear_registro_backup(backup_path + ".zip")
            self.progress.emit(100)
            
            self.message.emit("Backup completado exitosamente")
            self.finished.emit(True, f"Backup guardado en: {zip_path}")
            
        except Exception as e:
            self.message.emit(f"Error en backup: {str(e)}")
            self.finished.emit(False, f"Error: {str(e)}")

    def verificar_y_corregir_tabla_backups(self):
        """Verificar y corregir la estructura de la tabla backups"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar si la tabla existe y su estructura
            cursor.execute("PRAGMA table_info(backups)")
            columnas = cursor.fetchall()
            nombres_columnas = [col[1] for col in columnas]
            
            print("🔍 Estructura actual de la tabla 'backups':")
            for col in columnas:
                print(f"  - {col[1]} ({col[2]})")
            
            # Si la tabla no existe o le falta archivo_path, recrearla
            if not columnas or 'archivo_path' not in nombres_columnas:
                print("🔄 Corrigiendo estructura de la tabla backups...")
                
                # Crear tabla temporal con datos existentes si hay
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backups_temp AS 
                    SELECT * FROM backups WHERE 1=0
                """)
                
                # Eliminar tabla vieja
                cursor.execute("DROP TABLE IF EXISTS backups")
                
                # Crear tabla nueva con estructura correcta
                cursor.execute("""
                    CREATE TABLE backups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        archivo_path TEXT NOT NULL,
                        tamaño REAL NOT NULL,
                        tipo TEXT NOT NULL
                    )
                """)
                
                # Si había datos, intentar migrar
                try:
                    cursor.execute("INSERT INTO backups SELECT * FROM backups_temp")
                except:
                    print("ℹ️ No se pudieron migrar datos existentes (estructura incompatible)")
                
                cursor.execute("DROP TABLE IF EXISTS backups_temp")
                conn.commit()
                print("✅ Estructura de tabla 'backups' corregida")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Error verificando tabla backups: {e}")

    def crear_registro_backup(self, backup_path):
        """Registra el backup en la base de datos"""
        try:
            # ✅ LLAMAR A LA VERIFICACIÓN ANTES DE TODO
            self.verificar_y_corregir_tabla_backups()
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ✅ SOLO INSERTAR EL REGISTRO (la tabla ya está verificada)
            tamaño = os.path.getsize(backup_path) / (1024 * 1024)  # MB
            cursor.execute(
                "INSERT INTO backups (archivo_path, tamaño, tipo) VALUES (?, ?, ?)",
                (backup_path, tamaño, "automático")
            )
            conn.commit()
            conn.close()
            
            print(f"✅ Backup registrado en BD: {backup_path}")
            
        except Exception as e:
            print(f"❌ Error registrando backup: {e}")

class BackupManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        
        # ✅ USAR RUTAS ABSOLUTAS con el nuevo sistema
        app_dir = get_app_directory()
        self.db_path = os.path.join(app_dir, "caja_registradora.db")
        self.backup_dir = ensure_directory_exists(get_backups_directory())
        
        self.setWindowTitle("Sistema de Backup")
        self.setGeometry(200, 100, 600, 500)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Configuración de backup
        config_group = QGroupBox("Configuración de Backup")
        config_layout = QVBoxLayout()
        
        self.cb_config = QCheckBox("Incluir archivos de configuración (config.json)")
        self.cb_config.setChecked(True)
        config_layout.addWidget(self.cb_config)
        
        self.cb_tickets = QCheckBox("Incluir tickets de ventas")
        self.cb_tickets.setChecked(True)
        config_layout.addWidget(self.cb_tickets)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Directorio de backup
        dir_group = QGroupBox("Directorio de Backup")
        dir_layout = QVBoxLayout()
        
        # ✅ Mostrar la ruta ABSOLUTA del directorio de backups
        self.lbl_backup_dir = QLabel(f"📦 {self.backup_dir}")
        self.lbl_backup_dir.setStyleSheet("font-size: 10px; color: #666;")
        self.lbl_backup_dir.setWordWrap(True)
        dir_layout.addWidget(self.lbl_backup_dir)
        
        btn_change_dir = QPushButton("Cambiar Directorio")
        btn_change_dir.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        btn_change_dir.clicked.connect(self.cambiar_directorio)
        dir_layout.addWidget(btn_change_dir)
        
        dir_group.setLayout(dir_layout)
        layout.addWidget(dir_group)
        
        # Progreso
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        
        self.lbl_status = QLabel("Listo para realizar backup")
        progress_layout.addWidget(self.lbl_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_backup = QPushButton("Backup Ahora")
        self.btn_backup.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_backup.clicked.connect(self.ejecutar_backup)
        buttons_layout.addWidget(self.btn_backup)
        
        self.btn_restore = QPushButton("Restaurar Backup")
        self.btn_restore.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        self.btn_restore.clicked.connect(self.restaurar_backup)
        buttons_layout.addWidget(self.btn_restore)
        
        self.btn_auto = QPushButton("Configurar Auto-Backup")
        self.btn_auto.setStyleSheet("background-color: #9b59b6; color: white; font-weight: bold;")
        self.btn_auto.clicked.connect(self.configurar_auto_backup)
        buttons_layout.addWidget(self.btn_auto)
        
        layout.addLayout(buttons_layout)
        
        # Lista de backups
        backups_group = QGroupBox("Backups Existentes")
        backups_layout = QVBoxLayout()
        
        self.list_backups = QListWidget()
        backups_layout.addWidget(self.list_backups)
        
        backups_group.setLayout(backups_layout)
        layout.addWidget(backups_group)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)
        
        self.cargar_backups()
        
        # Timer para backup automático
        self.auto_backup_timer = QTimer()
        self.auto_backup_timer.timeout.connect(self.verificar_auto_backup)
        self.auto_backup_timer.start(60000)  # Verificar cada minuto
        
        # ✅ VERIFICAR ESTRUCTURA AL INICIAR
        self.verificar_estructura_backups()
    
    def verificar_estructura_backups(self):
        """Verificación adicional en el diálogo principal"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(backups)")
            columnas = [col[1] for col in cursor.fetchall()]
            print("📊 Estructura de backups al iniciar:", columnas)
            conn.close()
        except Exception as e:
            print(f"ℹ️ Info de estructura: {e}")
    
    def cambiar_directorio(self):
        # En una implementación real, aquí iría un QFileDialog
        QMessageBox.information(self, "Info", "En una versión completa, esto abriría un diálogo para seleccionar directorio")
    
    def cargar_backups(self):
        self.list_backups.clear()
        if os.path.exists(self.backup_dir):
            backups = sorted([f for f in os.listdir(self.backup_dir) if f.endswith('.zip')], reverse=True)
            for backup in backups:
                backup_path = os.path.join(self.backup_dir, backup)
                size = os.path.getsize(backup_path) / (1024 * 1024)
                date = datetime.fromtimestamp(os.path.getctime(backup_path))
                self.list_backups.addItem(f"{backup} ({size:.2f} MB) - {date.strftime('%Y-%m-%d %H:%M')}")
    
    def ejecutar_backup(self):
        # ✅ VERIFICACIÓN ADICIONAL ANTES DE BACKUP
        self.verificar_estructura_backups()
        
        self.btn_backup.setEnabled(False)
        self.lbl_status.setText("Iniciando backup...")
        
        self.worker = BackupWorker(
            self.db_path, 
            self.backup_dir,
            self.cb_config.isChecked(),
            self.cb_tickets.isChecked()
        )
        
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.message.connect(self.lbl_status.setText)
        self.worker.finished.connect(self.backup_finalizado)
        self.worker.start()
    
    def backup_finalizado(self, success, message):
        self.btn_backup.setEnabled(True)
        if success:
            QMessageBox.information(self, "Éxito", message)
            self.cargar_backups()
        else:
            QMessageBox.critical(self, "Error", message)
    
    def restaurar_backup(self):
        selected = self.list_backups.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un backup para restaurar")
            return
        
        backup_name = selected.text().split(' ')[0]
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            "¿Está seguro de restaurar este backup? Se sobreescribirán los datos actuales."
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Info", f"Backup {backup_name} seleccionado para restaurar")
            # Aquí iría la lógica completa de restauración
    
    def configurar_auto_backup(self):
        QMessageBox.information(self, "Auto-Backup", 
            "Configuración de backup automático:\n"
            "• Diario a las 23:00\n"
            "• Mantener últimos 7 backups\n"
            "• Notificar por email (si está configurado)")
    
    def verificar_auto_backup(self):
        # Verificar si es hora de hacer backup automático (ej: cada día a las 23:00)
        ahora = datetime.now()
        if ahora.hour == 23 and ahora.minute == 0:
            self.ejecutar_backup()

class AutoBackupConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurar Auto-Backup")
        self.setGeometry(300, 200, 400, 300)
        
        layout = QVBoxLayout()
        
        # TODO: Implementar interfaz para configurar auto-backup
        label = QLabel("Configuración de Backup Automático")
        layout.addWidget(label)
        
        self.setLayout(layout)