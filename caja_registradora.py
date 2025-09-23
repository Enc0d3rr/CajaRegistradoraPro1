import sys
import os
import json
import time 
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QHBoxLayout, QMessageBox, QInputDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QTabWidget,
    QComboBox, QLineEdit, QGridLayout, QGroupBox, QTextEdit, QDialog
)
from PyQt6.QtGui import QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt, QTimer
from datetime import datetime

from database import DatabaseManager
from auth_manager import LoginDialog
from ticket_generator import generar_ticket
from user_manager import UserManagerDialog
from inventory_manager import InventoryManagerDialog
from cash_close_manager import CashCloseManagerDialog
from backup_manager import BackupManagerDialog
from category_manager import CategoryManagerDialog
from sales_history import SalesHistoryDialog
from password_dialog import PasswordDialog
from config_panel import ConfigPanelDialog
from config_manager import config_manager

# DETECCIÓN DE PLATAFORMA - Agregar esto después de los imports existentes

def es_windows():
    return sys.platform.startswith('win')

def es_linux():
    return sys.platform.startswith('linux')

if es_windows():
    try:
        import ctypes
        ctypes.windll.shcore.SetprocessDpiAwareness(1)
        print("✅ Configuración DPI aplicada para Windows")
    except Exception as e:
        print(f"⚠️ No se pudo configurar DPI: {e}")

def obtener_estilos_windows():
    return """
    /* Estilos específicos para Windows */
    QMainWindow, QDialog, QWidget {
        background-color: #f0f0f0;
        font-family: "Segoe UI", Arial, sans-serif;
    }
    
    QGroupBox {
        background-color: white;
        border: 1px solid #cccccc;
        border-radius: 5px;
        margin-top: 10px;
        padding-top: 15px;
        font-weight: bold;
    }
    
    QTableWidget {
        background-color: white;
        gridline-color: #d0d0d0;
    }
    
    QHeaderView::section {
        background-color: #e1e1e1;
        padding: 5px;
        border: 1px solid #cccccc;
    }
    
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 3px;
    }
    """

def obtener_estilos_linux():
    return """
    /* Estilos para Linux (tus estilos originales) */
    QMainWindow {
        background-color: #ecf0f1;
    }
    """

class CajaGUI(QWidget):
    def __init__(self):
        super().__init__()

        self.db_manager = DatabaseManager()
        
         # MEJORAR CARGA DE CONFIGURACIÓN
        print("💾 CARGANDO CONFIGURACIÓN...")
        self.config = config_manager.load_config()
    
        if not self.config:
            QMessageBox.critical(None, "Error", "No se pudo cargar la configuración del sistema")
            sys.exit()
    
        # VERIFICAR CONFIGURACIÓN CARGADA
        print(f"🎨 Configuración cargada: {self.config.get('color_primario', 'NO HAY COLOR')}")
        
        # Autenticación
        self.show_login()
        
        if not hasattr(self, 'current_user'):
            sys.exit()
        
        self.init_ui()

        # Para windows
        if es_windows():
            from PyQt6.QtCore import QTimer
            print("🚀 INICIANDO CORRECCIONES WINDOWS...")
    
            # 1. Estilos inmediatos
            self.forzar_estilos_windows()
    
            # 2. Corrección de labels después de estilos
            QTimer.singleShot(500, self.corregir_labels_problematicos)
    
            # 3. Verificar persistencia
            QTimer.singleShot(1000, self.verificar_persistencia_configuracion)

        # Para Linux
        if es_linux():
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self.corregir_labels_problematicos)  # Solo 100ms
            print("⏱️  Correcciones programadas para 100ms")

    def show_login(self):
        """Sistema de login usando tu LoginDialog exacto"""
        try:
            print("🔐 Iniciando autenticación...")
        
            # USAR TU LoginDialog EXACTO
            from auth_manager import LoginDialog
        
            # Crear y mostrar el diálogo de login
            login_dialog = LoginDialog(self.db_manager)
        
            # Mostrar el diálogo y esperar respuesta
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                # Obtener los datos del usuario autenticado
                self.current_user = {
                    "id": login_dialog.user_data['id'],
                    "username": login_dialog.user_data['nombre'],  # Usar nombre como username
                    "nombre": login_dialog.user_data['nombre'],
                    "rol": login_dialog.user_data['rol']
                }
                print(f"✅ Login exitoso: {self.current_user['nombre']} ({self.current_user['rol']})")
            else:
                print("❌ Login cancelado o fallido")
                self.current_user = None
            
        except ImportError as e:
            print(f"❌ Error importando LoginDialog: {e}")
            self._login_emergencia()
        except Exception as e:
            print(f"❌ Error en autenticación: {e}")
            self._login_emergencia()

    def _login_emergencia(self):
        """Login de emergencia corregido"""
        try:
            from PyQt6.QtWidgets import QInputDialog, QMessageBox
        
            print("🚨 Usando sistema de login de emergencia...")
        
            # Dialogo de usuario
            usuario, ok = QInputDialog.getText(self, "Acceso al Sistema", "Usuario:")
            if not ok or not usuario:
                self.current_user = None
                return
            
            # CORRECCIÓN: Usar parámetro correcto 'echo'
            contraseña, ok = QInputDialog.getText(
                self, 
                "Acceso al Sistema", 
                "Contraseña:", 
                echo=QLineEdit.EchoMode.Password  # ← PARÁMETRO CORRECTO
            )
        
            if not ok or not contraseña:
                self.current_user = None
                return
        
            # Verificar credenciales
            if usuario == "admin" and contraseña == "admin123":
                self.current_user = {
                    "id": 1,
                    "username": "admin", 
                    "nombre": "Administrador",
                    "rol": "administrador"
                }
                QMessageBox.information(self, "Acceso Concedido", "Bienvenido Administrador")
                print("✅ Login de emergencia exitoso")
            else:
                QMessageBox.warning(self, "Acceso Denegado", "Credenciales incorrectas")
                self.current_user = None
            
        except Exception as e:
            print(f"❌ Error en login de emergencia: {e}")
            # Último recurso - usuario por defecto
            self.current_user = {
                "id": 1,
                "username": "admin", 
                "nombre": "Administrador",
                "rol": "administrador"
            }

    def gestionar_inventario(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar inventario")
            return
    
        dialog = InventoryManagerDialog(self.db_manager, self)
        dialog.exec()
        self.cargar_productos()  # Recargar productos después de cerrar el diálogo

    def gestionar_categorias(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar categorías")
            return
    
        dialog = CategoryManagerDialog(self.db_manager, self)
        dialog.exec()

    def gestionar_cierres(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar cierres de caja")
            return
    
        dialog = CashCloseManagerDialog(self.db_manager, self.current_user, self)
        dialog.exec()

    def gestionar_backups(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden gestionar backups")
            return
    
        dialog = BackupManagerDialog(self.db_manager, self)
        dialog.exec()

    def ver_historial_ventas(self):
        if self.current_user['rol'] != 'admin':
            QMessageBox.warning(self, "Error", "Solo los administradores pueden ver el historial de ventas")
            return
    
        dialog = SalesHistoryDialog(self.db_manager, self)
        dialog.exec()

    def abrir_panel_configuracion(self):
        """Abrir panel de configuración y reiniciar interfaz al guardar"""
        try:
            from config_panel import ConfigPanelDialog
            dialog = ConfigPanelDialog(self.db_manager, self.config, self)
        
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.config = dialog.get_updated_config()
                print("✅ Configuración actualizada correctamente")
            
                #  REINICIAR LA INTERFAZ COMPLETAMENTE
                self.reiniciar_interfaz()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir configuración: {str(e)}")

    def aplicar_configuracion(self):
        """Aplicar configuración - VERSIÓN CORREGIDA CON ESTILOS ESPECÍFICOS"""
        try:
            if es_linux():
                color_primario = self.config.get('color_primario', '#3498db')
                color_secundario = self.config.get('color_secundario', '#2ecc71')
                '''
                estilo = f"""
                    /* ESTILOS GENERALES */
                    QPushButton {{
                        background-color: {color_primario};
                        color: white;
                        border: none;
                        padding: 10px;
                        border-radius: 5px;
                        font-weight: bold;
                        margin: 2px;
                    }}
                    QPushButton:hover {{
                        background-color: {color_secundario};
                    }}
                
                    QLabel {{
                        color: {color_primario};
                        font-weight: bold;
                    }}
                
                    /* ✅ ESTILO ESPECÍFICO PARA EL TOTAL DE VENTAS */
                    /* Target por contenido de texto */
                    QLabel[text*="Total: $"] {{
                        color: #e74c3c !important;  /* Rojo */
                        font-size: 18px !important;
                        font-weight: bold !important;
                        background-color: #ffffff !important;
                        border: 2px solid #c0392b !important;
                        border-radius: 5px !important;
                        padding: 5px !important;
                    }}
                
                    /* ✅ ESTILO PARA LABELS CON "total" en el texto (case insensitive) */
                    QLabel[text*="total" i] {{
                        color: #000000 !important;
                        background-color: #f8f9fa !important;
                        border: 1px solid #cccccc !important;
                        padding: 3px !important;
                    }}
                
                    /* ✅ HACER VISIBLE EL LABEL DE VENTAS HOY */
                    QLabel[text*="VENTAS HOY"] {{
                        color: #000000 !important;
                        background-color: #e8f4f8 !important;
                        border: 2px solid #3498db !important;
                        border-radius: 5px !important;
                        padding: 10px !important;
                        font-size: 11px !important;
                    }}
                
                    QGroupBox {{
                        border: 2px solid {color_secundario};
                        border-radius: 8px;
                    }}
                """
                self.setStyleSheet(estilo)
                print("✅ Estilos Linux aplicados")
                '''
                print("ℹ️ Estilos generales temporalmente desactivados")

            elif es_windows():
                self._aplicar_personalizacion_windows()

            # Actualizar título
            nombre_negocio = self.config.get('nombre_negocio', 'Caja Registradora')
            self.setWindowTitle(f"{nombre_negocio} - Sistema de Ventas")
        
        except Exception as e:  # ✅ ESTA LÍNEA DEBE ESTAR PRESENTE
            print(f"⚠️ Error al aplicar configuración: {e}")

        
    def diagnosticar_total(self):
        """Diagnóstico específico del label Total"""
        print("🔍 DIAGNÓSTICO DEL TOTAL:")
    
        # Buscar todos los labels
        from PyQt6.QtWidgets import QLabel
        labels = self.findChildren(QLabel)
    
        total_encontrado = False
        for label in labels:
            texto = label.text()
            if texto and ("total" in texto.lower() or "Total" in texto or "TOTAL" in texto):
                print(f"🎯 LABEL TOTAL ENCONTRADO: '{texto}'")
                print(f"   - ObjectName: {label.objectName()}")
                print(f"   - Estilo actual: {label.styleSheet()}")
                print(f"   - Visible: {label.isVisible()}")
                print(f"   - Posición: {label.pos()}")
                print(f"   - Tamaño: {label.size()}")
            
                # Aplicar estilo de emergencia para hacerlo visible
                label.setStyleSheet("color: #ff0000 !important; font-size: 20pt !important; background-color: yellow !important; border: 3px solid red !important;")
                print("   ✅ Estilo de emergencia aplicado (debería verse ROJO sobre AMARILLO)")
                total_encontrado = True
    
        if not total_encontrado:
            print("❌ NO se encontró ningún label con 'total'")
            print("📋 Todos los labels encontrados:")
            for i, label in enumerate(labels[:10]):  # Mostrar primeros 10
                print(f"   {i+1}. '{label.text()}' - {label.objectName()}")

    def forzar_todos_los_textos_visibles(self):
        """Hacer visibles TODOS los textos temporalmente"""
        print("🚨 APLICANDO VISIBILIDAD FORZADA A TODOS LOS TEXTOS")
    
        from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox
    
        # Hacer visibles todos los labels
        for label in self.findChildren(QLabel):
            label.setStyleSheet("color: #000000 !important; background-color: yellow !important; font-size: 12pt !important;")
    
        # Hacer visibles todos los campos de texto
        for lineedit in self.findChildren(QLineEdit):
            lineedit.setStyleSheet("color: #000000 !important; background-color: #ffffcc !important; border: 2px solid blue !important;")
    
        print("✅ Todos los textos forzados a ser visibles")
    
    def corregir_labels_problematicos(self):
        """Versión RÁPIDA - Correcciones inmediatas"""
        print("⚡ Aplicando correcciones RÁPIDAS...")
    
        inicio = time.time()  # Medir tiempo
        labels_corregidos = 0
    
        for label in self.findChildren(QLabel):
            texto = label.text() if label.text() else ""
        
            # Label de VENTAS HOY
            if "VENTAS HOY" in texto:
                label.setVisible(True)
                label.setStyleSheet("color: #000000; background-color: #e8f4f8; border: 1px solid #3498db; border-radius: 5px; padding: 8px;")
                labels_corregidos += 1
        
            # Label del Total
            elif "Total: $" in texto:
                label.setStyleSheet("color: #e74c3c; font-size: 18px; font-weight: bold; background-color: #ffffff; border: 2px solid #c0392b; border-radius: 5px; padding: 5px;")
                labels_corregidos += 1
    
        # Medir tiempo de ejecución
        tiempo = time.time() - inicio
        print(f"✅ Correcciones aplicadas: {labels_corregidos} labels en {tiempo:.3f} segundos")

    def verificar_persistencia_configuracion(self):
        """Verificar y corregir problemas de persistencia"""
        print("💾 VERIFICANDO PERSISTENCIA DE CONFIGURACIÓN...")
    
        try:
            # Verificar si el archivo de configuración existe y es accesible
            config_path = 'data/config.json'
            if os.path.exists(config_path):
                print(f"✅ Archivo de configuración existe: {config_path}")
            
                # Verificar permisos
                if os.access(config_path, os.W_OK):
                    print("✅ Permisos de escritura OK")
                else:
                    print("❌ Sin permisos de escritura")
                
                # Leer contenido actual
                with open(config_path, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    print(f"📄 Contenido actual: {len(contenido)} caracteres")
            else:
                print("❌ Archivo de configuración NO existe")
            
            # Verificar configuración cargada
            print(f"🎨 Configuración en memoria: {self.config}")
        
        except Exception as e:
            print(f"❌ Error verificando persistencia: {e}")

    def verificacion_nuclear(self):
        """Verificación EXTREMA"""
        print("💥 VERIFICACIÓN NUCLEAR:")
    
        for label in self.findChildren(QLabel):
            texto = label.text() if label.text() else ""
            if "VENTAS HOY" in texto or "Total: $" in texto:
                print(f"💥 '{texto[:30]}...'")
                print(f"   - Visible: {label.isVisible()}")
                print(f"   - isHidden: {label.isHidden()}")
                print(f"   - isEnabled: {label.isEnabled()}")
                print(f"   - Opacidad: {label.windowOpacity()}")
    
        print("💥 VERIFICACIÓN NUCLEAR COMPLETADA")

    def actualizar_interfaz_completa(self):
        """Actualización COMPLETA y forzada de toda la interfaz"""
        print("🔄 FORZANDO ACTUALIZACIÓN COMPLETA DE LA INTERFAZ...")
    
        # 1. Forzar actualización de todos los widgets
        for widget in self.findChildren(QWidget):
            widget.update()
            widget.repaint()
    
     # 2. Actualizar la ventana principal
        self.update()
        self.repaint()
    
        # 3. Forzar procesamiento de eventos
        from PyQt6.QtCore import QCoreApplication
        QCoreApplication.processEvents()
    
        print("✅ Interfaz completamente actualizada")


    def _aplicar_estilos_windows_suaves(self):
        """Estilos suaves para Windows que no afectan Linux"""
        try:
            color_primario = self.config.get('color_primario', '#0078d4')
        
            estilo_windows = f"""
                /* Estilos mínimos para Windows */
                QWidget {{
                    background-color: #f0f0f0;
                    color: #000000;
                }}
            
                QLabel {{
                    color: #000000;
                }}
            
                QPushButton {{
                    background-color: {color_primario};
                    color: white;
                }}
            """
        
            self.setStyleSheet(estilo_windows)
            print("✅ Estilos Windows suaves aplicados")
        
        except Exception as e:
            print(f"⚠️ Error en estilos Windows: {e}")

    def _aplicar_personalizacion_windows(self):
        """Personalización específica para Windows"""
        try:
            color_primario = self.config.get('color_primario', '#0078d4')
            color_secundario = self.config.get('color_secundario', '#106ebe')
        
            # Solo personalizar botones y elementos clave en Windows
            estilo_personalizado = f"""
                /* BOTONES PRINCIPALES */
                QPushButton[objectName*="btn_"] {{
                    background-color: {color_primario} !important;
                    color: #ffffff !important;
                }}
            
                QPushButton[objectName*="btn_"]:hover {{
                    background-color: {color_secundario} !important;
                }}
            
                /* TÍTULOS */
                QLabel[objectName*="titulo"], QLabel[objectName*="Titulo"] {{
                    color: {color_primario} !important;
                }}
            
                /* GROUP BOX TITLES */
                QGroupBox::title {{
                    color: {color_primario} !important;
                }}
            """
        
            # Combinar con estilos base
            estilo_base = self.styleSheet()
            self.setStyleSheet(estilo_base + estilo_personalizado)
        
            print(f"✅ Personalización aplicada: {color_primario}")
        
        except Exception as e:
            print(f"⚠️ Error en personalización Windows: {e}")

    def forzar_estilos_windows(self):
        """SOLUCIÓN DEFINITIVA para Windows - Estilos INMEDIATOS"""
        if not es_windows():
            return
        
        print("🎨 APLICANDO ESTILOS WINDOWS DEFINITIVOS...")
    
        # Estilo nuclear para Windows
        estilo_windows = """
        /* ====== ESTILOS WINDOWS DEFINITIVOS ====== */
    
        /* RESET COMPLETO - Forzar visibilidad */
        * {
            background-color: #f0f0f0 !important;
            color: #000000 !important;
            font-family: "Segoe UI", Arial, sans-serif !important;
            font-size: 9pt !important;
        }
    
        /* VENTANA PRINCIPAL */
        QMainWindow, QWidget, QDialog {
            background-color: #f0f0f0 !important;
            color: #000000 !important;
        }
    
        /* LABELS - Hacerlos VISIBLES inmediatamente */
        QLabel {
            background-color: transparent !important;
            color: #000000 !important;
            font-weight: normal !important;
            border: none !important;
            padding: 2px !important;
            margin: 1px !important;
        }
    
        /* LABELS ESPECÍFICOS que vimos en las capturas */
        QLabel[text*="Total"],
        QLabel[text*="total"],
        QLabel[text*="TOTAL"] {
            color: #e74c3c !important;
            font-size: 16px !important;
            font-weight: bold !important;
            background-color: #ffffff !important;
            border: 2px solid #c0392b !important;
            border-radius: 5px !important;
            padding: 8px !important;
            margin: 5px !important;
        }
    
        /* GROUP BOX - Corregir textos amontonados */
        QGroupBox {
            background-color: #ffffff !important;
            border: 2px solid #cccccc !important;
            border-radius: 8px !important;
            margin-top: 15px !important;
            padding-top: 25px !important; /* ↑ Más espacio para el título */
            font-weight: bold !important;
            color: #000000 !important;
        }
    
        QGroupBox::title {
            background-color: #ffffff !important;
            color: #0078d4 !important;
            subcontrol-origin: margin !important;
            subcontrol-position: top left !important;
            left: 10px !important;
            padding: 5px 10px !important;
            margin-top: -10px !important;
            font-weight: bold !important;
            font-size: 10pt !important;
        }
    
        /* BOTONES */
        QPushButton {
            background-color: #0078d4 !important;
            color: #ffffff !important;
            border: none !important;
            padding: 10px 15px !important;
            border-radius: 5px !important;
            font-weight: bold !important;
            min-height: 30px !important;
            min-width: 100px !important;
        }
    
        QPushButton:hover {
            background-color: #106ebe !important;
        }
    
        /* CAMPOS DE TEXTO */
        QLineEdit, QComboBox, QSpinBox {
            background-color: #ffffff !important;
            color: #000000 !important;
            border: 2px solid #cccccc !important;
            padding: 8px !important;
            border-radius: 4px !important;
            min-height: 30px !important;
            font-size: 10pt !important;
        }
    
        /* TABLAS */
        QTableWidget {
            background-color: #ffffff !important;
            color: #000000 !important;
            gridline-color: #d0d0d0 !important;
            border: 1px solid #cccccc !important;
        }
    
        QTableWidget::item {
            padding: 8px !important;
            border-bottom: 1px solid #f0f0f0 !important;
        }
    
        QHeaderView::section {
            background-color: #e1e1e1 !important;
            color: #000000 !important;
            padding: 10px !important;
            border: none !important;
            font-weight: bold !important;
        }
        """
    
        # Aplicar estilos de manera AGRESIVA
        self.setStyleSheet(estilo_windows)
    
        # Forzar actualización INMEDIATA de todos los widgets
        for widget in self.findChildren(QWidget):
            widget.setStyleSheet(estilo_windows)
            widget.update()
            widget.repaint()
    
        print("✅ Estilos Windows aplicados DEFINITIVAMENTE")

    def respaldo_estilos_windows(self):
        """Respaldo por si el primer método falla"""
        if not es_windows():
            return
        
        print("🔧 EJECUTANDO RESPALDO PARA WINDOWS")
    
        # Verificar si los estilos se aplicaron
        if not self.styleSheet():
            print("⚠️ Los estilos no se aplicaron, usando respaldo...")
            self.forzar_estilos_windows()
    
        # Forzar actualización de todos los widgets hijos
        for widget in self.findChildren(QWidget):
            widget.update()
            widget.repaint()

    def aplicar_estilo_final(self, estilo):
        """Aplicar estilo después de una pequeña pausa"""
        self.setStyleSheet(estilo)
    
        # Forzar actualización de todos los widgets hijos
        for widget in self.findChildren(QWidget):
            widget.update()
            widget.repaint()
    
        self.update()
        self.repaint()
    
        # Actualizar título
        nombre_negocio = self.config.get('nombre_negocio', 'Caja Registradora')
        self.setWindowTitle(f"{nombre_negocio} - Sistema de Ventas")
    
        print("✅ Configuración aplicada con actualización forzada")
        

    def reiniciar_interfaz(self):
        """Reinicio CORREGIDO - Guarda configuración antes de reiniciar"""
        try:
            # GUARDAR CONFIGURACIÓN PRIMERO (ESTO ES LO QUE FALTA)
            print("💾 GUARDANDO CONFIGURACIÓN ANTES DE REINICIAR...")
        
            # Usar el config_manager para guardar
            from config_manager import config_manager
            success = config_manager.update_config(self.config)
        
            if success:
                print("✅ Configuración guardada exitosamente antes del reinicio")
            
                # Verificar que se guardó correctamente
                import time
                time.sleep(0.5)  # Pequeña pausa para asegurar guardado
            
                # Leer el archivo para verificar
                try:
                    with open('data/config.json', 'r', encoding='utf-8') as f:
                        contenido = json.load(f)
                        print(f"📄 Configuración guardada: {contenido.get('color_primario', 'NO HAY COLOR')}")
                except Exception as e:
                    print(f"❌ Error leyendo configuración guardada: {e}")
            else:
                print("❌ ERROR: No se pudo guardar la configuración")
                QMessageBox.critical(self, "Error", "No se pudo guardar la configuración")
                return
        
            # MENSAJE AL USUARIO
            respuesta = QMessageBox.question(
                self, 
                "Reiniciar Interfaz", 
                "La interfaz se reiniciará para aplicar los cambios.\n\n¿Continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
        
            if respuesta == QMessageBox.StandardButton.Yes:
                print("🔄 INICIANDO REINICIO...")
            
                # CERRAR VENTANA ACTUAL
                self.close()
            
                # CREAR NUEVA INSTANCIA después de un pequeño delay
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(500, self.crear_nueva_instancia)
            
            else:
                print("❌ Reinicio cancelado por el usuario")
            
        except Exception as e:
            print(f"❌ Error en reinicio: {e}")
            QMessageBox.critical(self, "Error", f"No se pudo reiniciar: {str(e)}")

    def crear_nueva_instancia(self):
        """Crear nueva instancia de la aplicación"""
        try:
            print("🚀 CREANDO NUEVA INSTANCIA...")
        
            # Importar aquí para evitar ciclos
            from caja_registradora import CajaGUI
        
            # Crear nueva ventana
            nueva_ventana = CajaGUI()
            nueva_ventana.show()
        
            print("✅ Nueva instancia creada exitosamente")
        
        except Exception as e:
            print(f"❌ Error creando nueva instancia: {e}")
            QMessageBox.critical(None, "Error", "No se pudo reiniciar la aplicación")

    def reinicio_directo(self):
        """Reinicio directo y simple"""
        try:
            # Mensaje de confirmación
            QMessageBox.information(
                self, 
                "Reiniciando", 
                "La interfaz se reiniciará para aplicar los cambios..."
            )
        
            # Guardar configuración
            from config_manager import config_manager
            config_manager.update_config(self.config)
        
            # Cerrar y preparar reinicio
            self.hide()  # Ocultar en lugar de cerrar
        
            # Crear nueva ventana
            from caja_registradora import CajaGUI
            self.nueva_ventana = CajaGUI()
            self.nueva_ventana.show()
        
            # Cerrar ventana anterior después de un delay
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(500, self.close)
        
        except Exception as e:
            print(f"Error en reinicio directo: {e}")
    
    def init_ui(self):
        # === Configuración ya cargada en __init__ con ConfigManager ===
        
        self.carrito = []
        self.metodos_pago = ["Efectivo", "Tarjeta", "Transferencia"]
        
        # === Configurar ventana principal ===
        # CORRECCIÓN: Verificar que current_user tenga 'nombre'
        if hasattr(self, 'current_user') and self.current_user and 'nombre' in self.current_user:
            self.setWindowTitle(f"{self.config.get('nombre_negocio', 'Caja Registradora')} - Usuario: {self.current_user['nombre']}")
        else:
            self.setWindowTitle(f"{self.config.get('nombre_negocio', 'Caja Registradora')} - Usuario: Desconocido")
        self.setGeometry(100, 50, 1000, 800)

        # Aplicar color de fondo
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.config["color_primario"]))
        self.setPalette(palette)

        main_layout = QVBoxLayout()

        # === Header ===
        header_layout = QHBoxLayout()
        
        # Logo o nombre del negocio - CORREGIDO
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setMinimumSize(100, 100)
        logo_label.setMaximumSize(100, 100)

        # DEBUG: Ver qué hay en la configuración
        print(f"🔍 Config: {self.config}")

        logo_path = self.config.get("logo_path", "")
        nombre_negocio = self.config.get("nombre_negocio", "").strip()

        print(f"📁 Logo path: {logo_path}")
        print(f"🏪 Nombre negocio: {nombre_negocio}")

        # Si hay logo intentar cargarlo
        if logo_path:
            try:
                logo_full_path = os.path.join("data", logo_path)
                print(f"📂 Intentando cargar: {logo_full_path}")
                print(f"📂 Existe archivo: {os.path.exists(logo_full_path)}")
        
                if os.path.exists(logo_full_path):
                    pixmap = QPixmap(logo_full_path)
                    if not pixmap.isNull():
                        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                        print("✅ Logo cargado exitosamente")
                        logo_label.setStyleSheet("border: 2px solid #ffffff; border-radius: 5px;")
                    else:
                        print("❌ El archivo de logo no es una imagen válida")
                        logo_label.setText(nombre_negocio or "Caja\nRegistradora")
                        logo_label.setStyleSheet("""
                            font-size: 14px; 
                            font-weight: bold; 
                            color: white;
                            background-color: rgba(0,0,0,0.3);
                            padding: 5px;
                            border-radius: 5px;
                            border: 1px solid #ffffff;
                        """)
                else:
                    print("❌ El archivo de logo no existe")
                    logo_label.setText(nombre_negocio or "Caja\nRegistradora")
                    logo_label.setStyleSheet("""
                        font-size: 14px; 
                        font-weight: bold; 
                        color: white;
                        background-color: rgba(0,0,0,0.3);
                        padding: 5px;
                        border-radius: 5px;
                    """)
            except Exception as e:
                print(f"❌ Error cargando logo: {e}")
                logo_label.setText(nombre_negocio or "Caja\nRegistradora")
                logo_label.setStyleSheet("""
                    font-size: 14px; 
                    font-weight: bold; 
                    color: white;
                    background-color: rgba(0,0,0,0.3);
                    padding: 5px;
                    border-radius: 5px;
                """)
        else:
            print("ℹ️ No hay logo configurado")
            logo_label.setText(nombre_negocio or "Caja\nRegistradora")
            logo_label.setStyleSheet("""
                font-size: 14px; 
                font-weight: bold; 
                color: white;
                background-color: rgba(0,0,0,0.3);
                padding: 5px;
                border-radius: 5px;
            """)

        # ✅ AGREGAR LOGO AL LAYOUT
        header_layout.addWidget(logo_label)
        print("✅ Logo label agregado al layout")

        # ✅ ESPACIO FLEXIBLE
        header_layout.addStretch(1)

        # Info usuario y hora
        user_info = QLabel(f"Usuario: {self.current_user['nombre']}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        user_info.setStyleSheet("""
            color: white; 
            font-size: 12px; 
            background-color: rgba(0,0,0,0.3); 
            padding: 8px;
            border-radius: 5px;
            border: 1px solid #ffffff;
        """)
        header_layout.addWidget(user_info)

        # ✅ ESPACIO FLEXIBLE
        header_layout.addStretch(1)

        # Panel de configuración (solo admin) - ✅ CORREGIDO
        if self.current_user['rol'] == 'admin':
            btn_config = QPushButton("⚙️ Panel Configuración")
            btn_config.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6; 
                    color: white; 
                    font-weight: bold; 
                    padding: 10px;
                    border: 2px solid #ffffff;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #8e44ad;
                }
                QPushButton:pressed {
                    background-color: #6c3483;
                }
            """)
            btn_config.clicked.connect(self.abrir_panel_configuracion)
            header_layout.addWidget(btn_config)
            print("✅ Botón de configuración agregado (admin)")
        
        # Actualizar hora cada segundo
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: user_info.setText(
            f"Usuario: {self.current_user['nombre']}\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ))
        self.timer.start(1000)
        
        main_layout.addLayout(header_layout)

        # === Sistema de pestañas ===
        self.tabs = QTabWidget()
        
        # Pestaña de ventas
        ventas_tab = QWidget()
        ventas_layout = QVBoxLayout()
        self.setup_ventas_tab(ventas_layout)
        ventas_tab.setLayout(ventas_layout)
        self.tabs.addTab(ventas_tab, "Ventas")
        
        # Pestaña de inventario (solo admin)
        if self.current_user['rol'] == 'admin':
            inventario_tab = QWidget()
            inventario_layout = QVBoxLayout()
            self.setup_inventario_tab(inventario_layout)
            inventario_tab.setLayout(inventario_layout)
            self.tabs.addTab(inventario_tab, "Inventario")
            
            # Pestaña de reportes
            reportes_tab = QWidget()
            reportes_layout = QVBoxLayout()
            self.setup_reportes_tab(reportes_layout)
            reportes_tab.setLayout(reportes_layout)
            self.tabs.addTab(reportes_tab, "Reportes")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)
        
        self.cargar_productos()

    def setup_ventas_tab(self, layout):
        # Lista de productos
        product_group = QGroupBox("Productos Disponibles")
        product_layout = QVBoxLayout()
        
        self.lista = QListWidget()
        product_layout.addWidget(self.lista)
        
        # Buscador
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.buscar_producto)
        search_layout.addWidget(self.search_input)
        product_layout.addLayout(search_layout)
        
        product_group.setLayout(product_layout)
        layout.addWidget(product_group)

        # Botones de acción
        botones_layout = QHBoxLayout()
        
        btn_agregar = QPushButton("Agregar producto")
        btn_agregar.setStyleSheet(f"background-color: {self.config['color_secundario']}; color: white; font-weight: bold;")
        btn_agregar.clicked.connect(self.agregar_producto)
        botones_layout.addWidget(btn_agregar)

        btn_eliminar = QPushButton("Eliminar producto")
        btn_eliminar.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_eliminar.clicked.connect(self.eliminar_producto)
        botones_layout.addWidget(btn_eliminar)

        btn_finalizar = QPushButton("Finalizar venta")
        btn_finalizar.setStyleSheet(f"background-color: {self.config['color_secundario']}; color: white; font-weight: bold;")
        btn_finalizar.clicked.connect(self.finalizar_venta)
        botones_layout.addWidget(btn_finalizar)

        btn_cancelar = QPushButton("Cancelar venta")
        btn_cancelar.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        btn_cancelar.clicked.connect(self.cancelar_venta)
        botones_layout.addWidget(btn_cancelar)

        layout.addLayout(botones_layout)

        # Tabla del carrito
        self.tabla_carrito = QTableWidget()
        self.tabla_carrito.setColumnCount(5)
        self.tabla_carrito.setHorizontalHeaderLabels(["Código", "Producto", "Precio", "Cantidad", "Subtotal"])
        self.tabla_carrito.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.tabla_carrito)

        # Total y método de pago
        footer_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: $ 0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        footer_layout.addWidget(self.total_label)
        
        footer_layout.addWidget(QLabel("Método de pago:"))
        self.metodo_pago_combo = QComboBox()
        self.metodo_pago_combo.addItems(self.metodos_pago)
        footer_layout.addWidget(self.metodo_pago_combo)
        
        layout.addLayout(footer_layout)

    def setup_inventario_tab(self, layout):
        # Layout de botones superiores
        top_buttons = QHBoxLayout()
    
        btn_abrir_inventario = QPushButton("📦 Gestor de Inventario")
        btn_abrir_inventario.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        btn_abrir_inventario.clicked.connect(self.gestionar_inventario)
        top_buttons.addWidget(btn_abrir_inventario)
    
        btn_categorias = QPushButton("🏷️ Gestor de Categorías")
        btn_categorias.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold;")
        btn_categorias.clicked.connect(self.gestionar_categorias)
        top_buttons.addWidget(btn_categorias)

        layout.addLayout(top_buttons)
    
    # Información de resumen
        summary_group = QGroupBox("Resumen de Inventario")
        summary_layout = QVBoxLayout()
    
        self.inventory_summary = QLabel("Cargando información...")
        self.inventory_summary.setStyleSheet("font-size: 12px;")
        summary_layout.addWidget(self.inventory_summary)
    
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
    
        self.actualizar_resumen_inventario()

    def actualizar_resumen_inventario(self):
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Productos con stock bajo
            cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo AND activo = 1")
            stock_bajo = cursor.fetchone()[0]
        
            # Total de productos
            cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
            total_productos = cursor.fetchone()[0]
        
            # Productos sin stock
            cursor.execute("SELECT COUNT(*) FROM productos WHERE stock = 0 AND activo = 1")
            sin_stock = cursor.fetchone()[0]
    
        summary_text = f"""
        📊 Resumen de Inventario:
        • Productos activos: {total_productos}
        • Productos con stock bajo: {stock_bajo}
        • Productos sin stock: {sin_stock}
    
        ⚠️ Atención: {stock_bajo} productos necesitan reposición
    """
    
        self.inventory_summary.setText(summary_text)

    def setup_reportes_tab(self, layout):
        # Layout de botones superiores
        top_buttons = QHBoxLayout()
    
        btn_abrir_reportes = QPushButton("📊 Cierres de Caja")
        btn_abrir_reportes.setStyleSheet("background-color: #16a085; color: white; font-weight: bold;")
        btn_abrir_reportes.clicked.connect(self.gestionar_cierres)
        top_buttons.addWidget(btn_abrir_reportes)
    
        btn_backups = QPushButton("💾 Sistema de Backup")
        btn_backups.setStyleSheet("background-color: #8e44ad; color: white; font-weight: bold;")
        btn_backups.clicked.connect(self.gestionar_backups)
        top_buttons.addWidget(btn_backups)

        btn_historial = QPushButton("📈 Historial de Ventas")
        btn_historial.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        btn_historial.clicked.connect(self.ver_historial_ventas)
        top_buttons.addWidget(btn_historial)
    
        layout.addLayout(top_buttons)
    
        # Información de resumen de ventas
        sales_group = QGroupBox("Resumen de Ventas Hoy")
        sales_layout = QVBoxLayout()
    
        self.sales_today_summary = QLabel("Cargando información...")
        self.sales_today_summary.setStyleSheet("font-size: 12px;")
        sales_layout.addWidget(self.sales_today_summary)

        sales_group.setLayout(sales_layout)
        layout.addWidget(sales_group)
    
        self.actualizar_resumen_ventas_hoy()

    def actualizar_resumen_ventas_hoy(self):
        hoy = datetime.now().strftime("%Y-%m-%d")
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
        
            # Ventas de hoy
            cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE DATE(fecha) = ?", (hoy,))
            count, total = cursor.fetchone()
            count = count or 0
            total = total or 0
        
            # Por método de pago
            cursor.execute("""
                SELECT metodo_pago, SUM(total) 
                FROM ventas 
                WHERE DATE(fecha) = ?
                GROUP BY metodo_pago
            """, (hoy,))
        
            metodos_pago = {}
            for metodo, total_metodo in cursor.fetchall():
                metodos_pago[metodo] = total_metodo or 0
    
        summary_text = f"""
        📊 VENTAS HOY ({hoy})
        • Total ventas: ${total:.2f}
        • N° de ventas: {count}
        • Efectivo: ${metodos_pago.get('Efectivo', 0):.2f}
        • Tarjeta: ${metodos_pago.get('Tarjeta', 0):.2f}
        • Transferencia: ${metodos_pago.get('Transferencia', 0):.2f}
        """
    
        self.sales_today_summary.setText(summary_text)

    def cargar_productos(self):
        self.lista.clear()
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE activo = 1 ORDER BY nombre")
            productos = cursor.fetchall()
            
            for codigo, nombre, precio, stock in productos:
                item_text = f"{codigo} - {nombre} - $ {precio:.2f} - Stock: {stock}"
                self.lista.addItem(item_text)

    def buscar_producto(self):
        if hasattr(self, 'search_input') and self.search_input:
            texto = self.search_input.text().lower()
        for i in range(self.lista.count()):
            item = self.lista.item(i)
            if texto and texto in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def agregar_producto(self):
        item = self.lista.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un producto de la lista.")
            return

        codigo = item.text().split(" - ")[0]
        
        # Verificar stock
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, precio, stock FROM productos WHERE codigo = ?", (codigo,))
            producto = cursor.fetchone()
            
            if not producto:
                QMessageBox.warning(self, "Error", "Producto no encontrado.")
                return
                
            nombre, precio, stock = producto
            
        if stock <= 0:
            QMessageBox.warning(self, "Error", "Producto sin stock disponible.")
            return

        cantidad, ok = QInputDialog.getInt(
            self, "Cantidad", f"Ingrese cantidad (Stock disponible: {stock}):", 
            1, 1, stock
        )
        if not ok:
            return

        # Verificar si ya está en el carrito
        for item in self.carrito:
            if item['codigo'] == codigo:
                item['cantidad'] += cantidad
                self.actualizar_tabla()
                return

        # Agregar nuevo producto
        self.carrito.append({
            'codigo': codigo,
            'nombre': nombre,
            'precio': precio,
            'cantidad': cantidad
        })

        self.actualizar_tabla()

    def eliminar_producto(self):
        fila = self.tabla_carrito.currentRow()
        if fila >= 0:
            del self.carrito[fila]
            self.actualizar_tabla()
        else:
            QMessageBox.warning(self, "Eliminar producto", "Seleccione un producto del carrito para eliminar.")

    def calcular_total(self):
        return sum(item['precio'] * item['cantidad'] for item in self.carrito)

    def actualizar_tabla(self):
        self.tabla_carrito.setRowCount(0)
        for item in self.carrito:
            row = self.tabla_carrito.rowCount()
            self.tabla_carrito.insertRow(row)
            self.tabla_carrito.setItem(row, 0, QTableWidgetItem(item['codigo']))
            self.tabla_carrito.setItem(row, 1, QTableWidgetItem(item['nombre']))
            self.tabla_carrito.setItem(row, 2, QTableWidgetItem(f"$ {item['precio']:.2f}"))
            self.tabla_carrito.setItem(row, 3, QTableWidgetItem(str(item['cantidad'])))
            subtotal = item['precio'] * item['cantidad']
            self.tabla_carrito.setItem(row, 4, QTableWidgetItem(f"$ {subtotal:.2f}"))

        iva = self.config.get("iva", 0.18)
        total = self.calcular_total() * (1 + iva)
        self.total_label.setText(f"Total: $ {total:.2f}")

    def cancelar_venta(self):
        self.carrito = []
        self.actualizar_tabla()
        QMessageBox.information(self, "Venta cancelada", "🛑 Carrito vacío.")

    def finalizar_venta(self):
        if not self.carrito:
            QMessageBox.warning(self, "Atención", "⚠️ No hay productos en el carrito.")
            return
        
        iva = self.config.get("iva", 0.18)
        total = self.calcular_total() * (1 + iva)
        metodo_pago = self.metodo_pago_combo.currentText()
        
        # Guardar venta en base de datos
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Insertar venta
            cursor.execute(
                "INSERT INTO ventas (total, iva, metodo_pago, usuario_id) VALUES (?, ?, ?, ?)",
                (total, iva, metodo_pago, self.current_user['id'])
            )
            venta_id = cursor.lastrowid
            
            # Insertar detalles de venta y actualizar stock
            for item in self.carrito:
                # Obtener ID del producto
                cursor.execute("SELECT id FROM productos WHERE codigo = ?", (item['codigo'],))
                producto_id = cursor.fetchone()[0]
                
                cursor.execute(
                    "INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)",
                    (venta_id, producto_id, item['cantidad'], item['precio'], item['precio'] * item['cantidad'])
                )
                
                # Actualizar stock
                cursor.execute(
                    "UPDATE productos SET stock = stock - ? WHERE codigo = ?",
                    (item['cantidad'], item['codigo'])
                )
            
            conn.commit()
        
        # Generar ticket
        ticket_path = generar_ticket(
            self.carrito, 
            iva, 
            total,
            metodo_pago,
            self.config.get("nombre_negocio", ""),
            venta_id
        )
        
        self.carrito = []
        self.actualizar_tabla()
        self.cargar_productos()  # Actualizar lista de productos
        
        QMessageBox.information(
            self, 
            "Venta finalizada", 
            f"🧾 Total a pagar: $ {total:.2f}\nMétodo: {metodo_pago}\n\nTicket guardado en:\n{ticket_path}"
        )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CajaGUI()
    window.show()
    sys.exit(app.exec())