import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QListWidget, QProgressBar, QGroupBox, QCheckBox,
    QTimeEdit, QComboBox, QSpinBox, QFormLayout, QApplication
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
                config_files = ["config.json", "licencia.json"]
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
            self.crear_registro_backup(zip_path)
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

class RestoreWorker(QThread):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal(bool, str)

    def __init__(self, backup_path, db_path, app_dir):
        super().__init__()
        self.backup_path = backup_path
        self.db_path = db_path
        self.app_dir = app_dir

    def run(self):
        try:
            self.message.emit("Iniciando restauración...")
            self.progress.emit(10)

            # Crear directorio temporal para extracción
            temp_dir = os.path.join(self.app_dir, "temp_restore")
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            
            self.message.emit("Extrayendo archivos de backup...")
            shutil.unpack_archive(self.backup_path, temp_dir)
            self.progress.emit(30)

            # Cerrar todas las conexiones a la base de datos existente
            self.message.emit("Preparando base de datos...")
            self.progress.emit(50)

            # Copiar base de datos del backup
            db_backup_path = os.path.join(temp_dir, "caja_registradora.db")
            if os.path.exists(db_backup_path):
                # Hacer backup de la base de datos actual antes de reemplazar
                backup_actual = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                if os.path.exists(self.db_path):
                    shutil.copy2(self.db_path, backup_actual)
                
                # Reemplazar base de datos
                shutil.copy2(db_backup_path, self.db_path)
                self.progress.emit(70)

            # Restaurar archivos de configuración
            self.message.emit("Restaurando configuración...")
            for config_file in ["config.json", "licencia.json"]:
                config_backup_path = os.path.join(temp_dir, config_file)
                if os.path.exists(config_backup_path):
                    shutil.copy2(config_backup_path, os.path.join(self.app_dir, config_file))
            self.progress.emit(85)

            # Restaurar tickets
            self.message.emit("Restaurando tickets...")
            tickets_backup_path = os.path.join(temp_dir, "tickets")
            tickets_dir = os.path.join(self.app_dir, "tickets")
            if os.path.exists(tickets_backup_path):
                if os.path.exists(tickets_dir):
                    shutil.rmtree(tickets_dir)
                shutil.copytree(tickets_backup_path, tickets_dir)
            self.progress.emit(95)

            # Limpiar directorio temporal
            shutil.rmtree(temp_dir)
            self.progress.emit(100)

            self.message.emit("Restauración completada exitosamente")
            self.finished.emit(True, "Backup restaurado correctamente. Reinicie la aplicación.")

        except Exception as e:
            self.message.emit(f"Error en restauración: {str(e)}")
            self.finished.emit(False, f"Error durante la restauración: {str(e)}")

class AutoBackupConfigDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Configurar Auto-Backup")
        self.setGeometry(300, 200, 400, 350)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Formulario de configuración
        form_group = QGroupBox("Configuración de Auto-Backup")
        form_layout = QFormLayout()
        
        # Habilitar auto-backup
        self.cb_habilitado = QCheckBox("Habilitar backup automático")
        form_layout.addRow(self.cb_habilitado)
        
        # Hora del backup
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        form_layout.addRow("Hora del backup:", self.time_edit)
        
        # Frecuencia
        self.combo_frecuencia = QComboBox()
        self.combo_frecuencia.addItems(["Diario", "Semanal"])
        form_layout.addRow("Frecuencia:", self.combo_frecuencia)
        
        # Días a mantener backups
        self.spin_dias = QSpinBox()
        self.spin_dias.setRange(1, 365)
        self.spin_dias.setValue(7)
        form_layout.addRow("Días a mantener backups:", self.spin_dias)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        btn_guardar = QPushButton("Guardar Configuración")
        btn_guardar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_guardar.clicked.connect(self.guardar_configuracion)
        buttons_layout.addWidget(btn_guardar)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cancelar.clicked.connect(self.reject)
        buttons_layout.addWidget(btn_cancelar)
        
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Cargar configuración actual
        self.cargar_configuracion_actual()

    def cargar_configuracion_actual(self):
        """Carga la configuración actual desde la base de datos"""
        try:
            config = self.cargar_configuracion_auto_backup()
            
            self.cb_habilitado.setChecked(config["habilitado"])
            
            # Configurar hora
            hora_str = config["hora"]
            hora_obj = datetime.strptime(hora_str, "%H:%M").time()
            self.time_edit.setTime(hora_obj)
            
            # Configurar frecuencia
            index = self.combo_frecuencia.findText(config["frecuencia"].capitalize())
            if index >= 0:
                self.combo_frecuencia.setCurrentIndex(index)
            
            # Configurar días
            self.spin_dias.setValue(config["mantener_dias"])
            
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")

    def cargar_configuracion_auto_backup(self):
        """Carga la configuración de auto-backup desde la base de datos"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave, valor FROM configuracion 
                    WHERE clave LIKE 'auto_backup_%'
                """)
                config_data = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    "habilitado": config_data.get("auto_backup_habilitado", "0") == "1",
                    "hora": config_data.get("auto_backup_hora", "02:00"),
                    "frecuencia": config_data.get("auto_backup_frecuencia", "diario"),
                    "mantener_dias": int(config_data.get("auto_backup_mantener_dias", "7"))
                }
        except Exception as e:
            print(f"❌ Error cargando configuración auto-backup: {e}")
            return {
                "habilitado": False,
                "hora": "02:00",
                "frecuencia": "diario", 
                "mantener_dias": 7
            }

    def guardar_configuracion(self):
        """Guarda la configuración de auto-backup en la BD"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                
                configuraciones = [
                    ("auto_backup_habilitado", "1" if self.cb_habilitado.isChecked() else "0", "Auto-backup habilitado"),
                    ("auto_backup_hora", self.time_edit.time().toString("HH:mm"), "Hora del backup automático"),
                    ("auto_backup_frecuencia", self.combo_frecuencia.currentText().lower(), "Frecuencia del backup"),
                    ("auto_backup_mantener_dias", str(self.spin_dias.value()), "Días a mantener backups")
                ]
                
                for clave, valor, descripcion in configuraciones:
                    cursor.execute("""
                        INSERT OR REPLACE INTO configuracion (clave, valor, descripcion)
                        VALUES (?, ?, ?)
                    """, (clave, valor, descripcion))
                
                conn.commit()
                
            QMessageBox.information(self, "Éxito", "Configuración de auto-backup guardada correctamente")
            self.accept()
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {str(e)}")

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
        
        self.cb_config = QCheckBox("Incluir archivos de configuración (config.json, licencia.json)")
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
        
        btn_abrir_dir = QPushButton("Abrir Directorio de Backups")
        btn_abrir_dir.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        btn_abrir_dir.clicked.connect(self.abrir_directorio_backups)
        dir_layout.addWidget(btn_abrir_dir)
        
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
        
        # Botones para gestión de backups
        backup_buttons_layout = QHBoxLayout()
        
        btn_eliminar_backup = QPushButton("Eliminar Backup Seleccionado")
        btn_eliminar_backup.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        btn_eliminar_backup.clicked.connect(self.eliminar_backup)
        backup_buttons_layout.addWidget(btn_eliminar_backup)
        
        btn_limpiar_antiguos = QPushButton("Limpiar Backups Antiguos")
        btn_limpiar_antiguos.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        btn_limpiar_antiguos.clicked.connect(self.limpiar_backups_antiguos)
        backup_buttons_layout.addWidget(btn_limpiar_antiguos)
        
        backups_layout.addLayout(backup_buttons_layout)
        backups_group.setLayout(backups_layout)
        layout.addWidget(backups_group)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)
        
        self.cargar_backups()
        
        # Timer para backup automático (verificar cada minuto)
        self.auto_backup_timer = QTimer()
        self.auto_backup_timer.timeout.connect(self.verificar_auto_backup)
        self.auto_backup_timer.start(60000)
        
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

    def abrir_directorio_backups(self):
        """Abre el directorio de backups en el explorador de archivos"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.backup_dir)
            elif os.name == 'posix':  # Linux, macOS
                os.system(f'xdg-open "{self.backup_dir}"')
        except Exception as e:
            QMessageBox.warning(self, "Info", f"No se pudo abrir el directorio: {str(e)}")

    def cargar_backups(self):
        """Carga la lista de backups disponibles"""
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
            # Limpiar backups antiguos después de crear uno nuevo
            self.limpiar_backups_antiguos()
        else:
            QMessageBox.critical(self, "Error", message)
        
        self.progress_bar.setValue(0)
        self.lbl_status.setText("Listo para realizar backup")

    def restaurar_backup(self):
        selected = self.list_backups.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un backup para restaurar")
            return
        
        backup_name = selected.text().split(' ')[0]
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            "¿Está seguro de restaurar este backup?\n\n"
            "⚠️  Se sobreescribirán los datos actuales y la aplicación se cerrará."
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                self.lbl_status.setText("Preparando restauración...")
                self.btn_restore.setEnabled(False)
                
                self.restore_worker = RestoreWorker(
                    backup_path, 
                    self.db_path, 
                    get_app_directory()
                )
                
                self.restore_worker.progress.connect(self.progress_bar.setValue)
                self.restore_worker.message.connect(self.lbl_status.setText)
                self.restore_worker.finished.connect(self.restore_finalizado)
                self.restore_worker.start()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo iniciar la restauración: {str(e)}")

    def restore_finalizado(self, success, message):
        self.btn_restore.setEnabled(True)
        self.progress_bar.setValue(0)
        
        if success:
            QMessageBox.information(self, "Éxito", 
                f"{message}\n\nLa aplicación se cerrará ahora para completar la restauración.")
            # Cerrar la aplicación
            QApplication.quit()
        else:
            QMessageBox.critical(self, "Error", message)
            self.lbl_status.setText("Error en restauración")

    def configurar_auto_backup(self):
        """Abre el diálogo de configuración de auto-backup"""
        dialog = AutoBackupConfigDialog(self.db_manager, self)
        dialog.exec()

    def verificar_auto_backup(self):
        """Verifica si es hora de hacer backup automático"""
        ahora = datetime.now()
        
        # Cargar configuración de auto-backup
        config = self.cargar_configuracion_auto_backup()
        
        if not config.get("habilitado", False):
            return
        
        hora_programada = config.get("hora", "02:00")
        frecuencia = config.get("frecuencia", "diario")
        
        try:
            hora_obj = datetime.strptime(hora_programada, "%H:%M").time()
            ahora_time = ahora.time()
            
            # Verificar si es la hora programada (con margen de 1 minuto)
            if (abs(ahora_time.hour - hora_obj.hour) == 0 and 
                abs(ahora_time.minute - hora_obj.minute) <= 1):
                
                # Verificar que no hayamos hecho backup en la última hora
                ultimo_backup = self.obtener_ultimo_backup_tiempo()
                if ultimo_backup and (ahora - ultimo_backup).total_seconds() < 3600:
                    return
                
                # Verificar frecuencia
                if frecuencia == "diario":
                    self.ejecutar_backup_automatico()
                elif frecuencia == "semanal" and ahora.weekday() == 0:  # Lunes
                    self.ejecutar_backup_automatico()
                    
        except Exception as e:
            print(f"❌ Error verificando auto-backup: {e}")

    def ejecutar_backup_automatico(self):
        """Ejecuta backup automático sin interacción del usuario"""
        try:
            print("🔄 Iniciando backup automático...")
            self.worker = BackupWorker(
                self.db_path, 
                self.backup_dir,
                include_config=True,
                include_tickets=True
            )
            self.worker.finished.connect(self.auto_backup_finalizado)
            self.worker.start()
        except Exception as e:
            print(f"❌ Error iniciando backup automático: {e}")

    def auto_backup_finalizado(self, success, message):
        """Maneja la finalización del backup automático"""
        if success:
            print(f"✅ Backup automático completado: {message}")
            self.cargar_backups()
            self.limpiar_backups_antiguos()
        else:
            print(f"❌ Backup automático falló: {message}")

    def cargar_configuracion_auto_backup(self):
        """Carga la configuración de auto-backup desde la base de datos"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT clave, valor FROM configuracion 
                    WHERE clave LIKE 'auto_backup_%'
                """)
                config_data = {row[0]: row[1] for row in cursor.fetchall()}
                
                return {
                    "habilitado": config_data.get("auto_backup_habilitado", "0") == "1",
                    "hora": config_data.get("auto_backup_hora", "02:00"),
                    "frecuencia": config_data.get("auto_backup_frecuencia", "diario"),
                    "mantener_dias": int(config_data.get("auto_backup_mantener_dias", "7"))
                }
        except Exception as e:
            print(f"❌ Error cargando configuración auto-backup: {e}")
            return {
                "habilitado": False,
                "hora": "02:00",
                "frecuencia": "diario", 
                "mantener_dias": 7
            }

    def obtener_ultimo_backup_tiempo(self):
        """Obtiene el tiempo del último backup realizado"""
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT fecha FROM backups 
                    ORDER BY fecha DESC LIMIT 1
                """)
                result = cursor.fetchone()
                if result:
                    return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"❌ Error obteniendo último backup: {e}")
        return None

    def limpiar_backups_antiguos(self):
        """Elimina backups más antiguos que los días configurados"""
        try:
            config = self.cargar_configuracion_auto_backup()
            mantener_dias = config.get("mantener_dias", 7)
            fecha_limite = datetime.now() - timedelta(days=mantener_dias)
            
            if os.path.exists(self.backup_dir):
                eliminados = 0
                for archivo in os.listdir(self.backup_dir):
                    if archivo.endswith('.zip'):
                        archivo_path = os.path.join(self.backup_dir, archivo)
                        fecha_creacion = datetime.fromtimestamp(os.path.getctime(archivo_path))
                        if fecha_creacion < fecha_limite:
                            os.remove(archivo_path)
                            eliminados += 1
                            print(f"🗑️ Eliminado backup antiguo: {archivo}")
                
                if eliminados > 0:
                    self.cargar_backups()
                    print(f"✅ Eliminados {eliminados} backups antiguos")
                    
        except Exception as e:
            print(f"❌ Error limpiando backups antiguos: {e}")

    def eliminar_backup(self):
        """Elimina el backup seleccionado"""
        selected = self.list_backups.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un backup para eliminar")
            return
        
        backup_name = selected.text().split(' ')[0]
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que quiere eliminar el backup '{backup_name}'?"
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                os.remove(backup_path)
                QMessageBox.information(self, "Éxito", "Backup eliminado correctamente")
                self.cargar_backups()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el backup: {str(e)}")