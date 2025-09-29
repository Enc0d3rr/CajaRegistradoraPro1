from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QListWidget, QListWidgetItem,
    QColorDialog, QInputDialog, QGroupBox, QTextEdit, QDialogButtonBox
)
from PyQt6.QtGui import QPalette, QColor, QBrush
from PyQt6.QtCore import Qt

class CategoryManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Gestión de Categorías")
        self.setGeometry(200, 100, 800, 600)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QHBoxLayout()
        
        # Lista de categorías
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Categorías:"))
        
        self.list_categorias = QListWidget()
        self.list_categorias.currentItemChanged.connect(self.cargar_detalles_categoria)
        left_layout.addWidget(self.list_categorias)
        
        # Botones de acción para categorías
        btn_layout = QHBoxLayout()
        
        btn_nueva = QPushButton("➕ Nueva")
        btn_nueva.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        btn_nueva.clicked.connect(self.nueva_categoria)
        btn_layout.addWidget(btn_nueva)
        
        btn_eliminar = QPushButton("🗑️ Eliminar")
        btn_eliminar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        btn_eliminar.clicked.connect(self.eliminar_categoria)
        btn_layout.addWidget(btn_eliminar)
        
        left_layout.addLayout(btn_layout)
        
        # Detalles de la categoría
        right_layout = QVBoxLayout()
        
        details_group = QGroupBox("Detalles de la Categoría")
        details_layout = QVBoxLayout()
        
        details_layout.addWidget(QLabel("Nombre:"))
        self.nombre_input = QLineEdit()
        details_layout.addWidget(self.nombre_input)
        
        details_layout.addWidget(QLabel("Descripción:"))
        self.descripcion_input = QTextEdit()
        self.descripcion_input.setMaximumHeight(100)
        details_layout.addWidget(self.descripcion_input)
        
        details_layout.addWidget(QLabel("Color:"))
        self.color_layout = QHBoxLayout()
        
        self.color_display = QLabel()
        self.color_display.setStyleSheet("background-color: #3498db; border: 2px solid #000; min-width: 50px; min-height: 30px;")
        self.color_layout.addWidget(self.color_display)
        
        self.btn_color = QPushButton("Seleccionar Color")
        self.btn_color.setStyleSheet("background-color: #3498db; color: white;")
        self.btn_color.clicked.connect(self.seleccionar_color)
        self.color_layout.addWidget(self.btn_color)
        
        details_layout.addLayout(self.color_layout)
        
        # Estadísticas
        details_layout.addWidget(QLabel("Estadísticas:"))
        self.stats_label = QLabel("0 productos en esta categoría")
        details_layout.addWidget(self.stats_label)
        
        # Botón guardar
        self.btn_guardar = QPushButton("💾 Guardar Cambios")
        self.btn_guardar.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold;")
        self.btn_guardar.clicked.connect(self.guardar_categoria)
        details_layout.addWidget(self.btn_guardar)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        # Productos de esta categoría
        products_group = QGroupBox("Productos en esta Categoría")
        products_layout = QVBoxLayout()
        
        self.list_productos = QListWidget()
        products_layout.addWidget(self.list_productos)
        
        products_group.setLayout(products_layout)
        right_layout.addWidget(products_group)
        
        # === BOTONES DE CERRAR (AGREGADOS) ===
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.reject)
        right_layout.addWidget(btn_cerrar)

        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)

        self.setLayout(layout)

        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        
        self.setLayout(layout)
        
        self.current_color = "#3498db"
        self.current_category_id = None
        self.cargar_categorias()
        self.limpiar_formulario()
    
    def cargar_categorias(self):
        self.list_categorias.clear()
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, color FROM categorias WHERE activa = 1 ORDER BY nombre")
            categorias = cursor.fetchall()
            
            for id_, nombre, color in categorias:
                item = QListWidgetItem(nombre)
                item.setData(Qt.ItemDataRole.UserRole, id_)
                if color:
                    item.setBackground(QBrush(QColor(color)))
                    item.setForeground(QBrush(QColor("white")))
                self.list_categorias.addItem(item)
    
    def cargar_detalles_categoria(self, current, previous):
        if not current:
            self.limpiar_formulario()
            return
        
        category_id = current.data(Qt.ItemDataRole.UserRole)
        self.current_category_id = category_id
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, descripcion, color FROM categorias WHERE id = ?", (category_id,))
            categoria = cursor.fetchone()
            
            if categoria:
                nombre, descripcion, color = categoria
                self.nombre_input.setText(nombre)
                self.descripcion_input.setPlainText(descripcion or "")
                self.current_color = color or "#3498db"
                self.color_display.setStyleSheet(f"background-color: {self.current_color}; border: 2px solid #000; min-width: 50px; min-height: 30px;")
                self.btn_color.setStyleSheet(f"background-color: {self.current_color}; color: white;")
                
                # Cargar estadísticas
                cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria_id = ? AND activo = 1", (category_id,))
                count = cursor.fetchone()[0]
                self.stats_label.setText(f"{count} productos en esta categoría")
                
                # Cargar productos
                self.cargar_productos_categoria(category_id)
    
    def cargar_productos_categoria(self, category_id):
        self.list_productos.clear()
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT codigo, nombre, precio, stock 
                FROM productos 
                WHERE categoria_id = ? AND activo = 1 
                ORDER BY nombre
            """, (category_id,))
            
            productos = cursor.fetchall()
            for codigo, nombre, precio, stock in productos:
                self.list_productos.addItem(f"{codigo} - {nombre} - ${precio:.2f} - Stock: {stock}")
    
    def seleccionar_color(self):
        color = QColorDialog.getColor(QColor(self.current_color), self, "Seleccionar Color")
        if color.isValid():
            self.current_color = color.name()
            self.color_display.setStyleSheet(f"background-color: {self.current_color}; border: 2px solid #000; min-width: 50px; min-height: 30px;")
            self.btn_color.setStyleSheet(f"background-color: {self.current_color}; color: white;")
    
    def nueva_categoria(self):
        nombre, ok = QInputDialog.getText(self, "Nueva Categoría", "Nombre de la nueva categoría:")
        if ok and nombre.strip():
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO categorias (nombre, color) VALUES (?, ?)",
                        (nombre.strip(), "#3498db")
                    )
                    conn.commit()
                
                QMessageBox.information(self, "Éxito", "Categoría creada correctamente")
                self.cargar_categorias()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la categoría: {str(e)}")
    
    def guardar_categoria(self):
        if not self.current_category_id:
            QMessageBox.warning(self, "Error", "Seleccione una categoría para editar")
            return
        
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre de la categoría es obligatorio")
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE categorias SET nombre = ?, descripcion = ?, color = ? WHERE id = ?",
                    (nombre, descripcion, self.current_color, self.current_category_id)
                )
                conn.commit()
            
            QMessageBox.information(self, "Éxito", "Categoría actualizada correctamente")
            self.cargar_categorias()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar la categoría: {str(e)}")
    
    def eliminar_categoria(self):
        selected = self.list_categorias.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione una categoría para eliminar")
            return
        
        category_id = selected.data(Qt.ItemDataRole.UserRole)
        category_name = selected.text()
        
        # Verificar si hay productos en esta categoría
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos WHERE categoria_id = ? AND activo = 1", (category_id,))
            product_count = cursor.fetchone()[0]
        
        if product_count > 0:
            QMessageBox.warning(self, "Error", 
                f"No se puede eliminar la categoría '{category_name}'\n"
                f"Tiene {product_count} productos asignados.\n"
                f"Reasigne los productos a otra categoría primero.")
            return
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de eliminar la categoría '{category_name}'?"
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE categorias SET activa = 0 WHERE id = ?",
                        (category_id,)
                    )
                    conn.commit()
                
                QMessageBox.information(self, "Éxito", "Categoría eliminada correctamente")
                self.cargar_categorias()
                self.limpiar_formulario()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la categoría: {str(e)}")
    
    def limpiar_formulario(self):
        self.nombre_input.clear()
        self.descripcion_input.clear()
        self.current_color = "#3498db"
        self.color_display.setStyleSheet("background-color: #3498db; border: 2px solid #000; min-width: 50px; min-height: 30px;")
        self.btn_color.setStyleSheet("background-color: #3498db; color: white;")
        self.stats_label.setText("0 productos en esta categoría")
        self.list_productos.clear()
        self.current_category_id = None