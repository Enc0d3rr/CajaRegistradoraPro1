from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QComboBox, QInputDialog, QGridLayout
)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt

class InventoryManagerDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("Gestión de Inventario")
        self.setGeometry(200, 100, 1000, 700)
        
        # Estilo de la ventana
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ecf0f1"))
        self.setPalette(palette)
        
        layout = QVBoxLayout()
        
        # Buscador
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar:"))
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.buscar_producto)
        search_layout.addWidget(self.search_input)
        
        # Filtro por categoría
        search_layout.addWidget(QLabel("Categoría:"))
        self.categoria_combo = QComboBox()
        search_layout.addWidget(self.categoria_combo)
        
        layout.addLayout(search_layout)
        
        # Tabla de productos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Precio", "Stock", "Stock Mín", "Categoría"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        
        # Formulario para agregar/editar productos
        form_layout = QVBoxLayout()
        
        # Campos de entrada
        fields_layout = QGridLayout()
        
        fields_layout.addWidget(QLabel("Código:"), 0, 0)
        self.codigo_input = QLineEdit()
        fields_layout.addWidget(self.codigo_input, 0, 1)
        
        fields_layout.addWidget(QLabel("Nombre:"), 1, 0)
        self.nombre_input = QLineEdit()
        fields_layout.addWidget(self.nombre_input, 1, 1)
        
        fields_layout.addWidget(QLabel("Precio:"), 2, 0)
        self.precio_input = QLineEdit()
        fields_layout.addWidget(self.precio_input, 2, 1)
        
        fields_layout.addWidget(QLabel("Stock:"), 3, 0)
        self.stock_input = QLineEdit()
        fields_layout.addWidget(self.stock_input, 3, 1)
        
        fields_layout.addWidget(QLabel("Stock Mínimo:"), 0, 2)
        self.stock_min_input = QLineEdit()
        self.stock_min_input.setText("5")
        fields_layout.addWidget(self.stock_min_input, 0, 3)
        
        fields_layout.addWidget(QLabel("Categoría:"), 1, 2)
        self.categoria_input = QComboBox()
        fields_layout.addWidget(self.categoria_input, 1, 3)
        
        form_layout.addLayout(fields_layout)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        self.btn_agregar = QPushButton("Agregar Producto")
        self.btn_agregar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")
        self.btn_agregar.clicked.connect(self.agregar_producto)
        buttons_layout.addWidget(self.btn_agregar)
        
        self.btn_editar = QPushButton("Editar Producto")
        self.btn_editar.setStyleSheet("background-color: #f39c12; color: white; font-weight: bold;")
        self.btn_editar.clicked.connect(self.editar_producto)
        buttons_layout.addWidget(self.btn_editar)
        
        self.btn_eliminar = QPushButton("Eliminar Producto")
        self.btn_eliminar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        self.btn_eliminar.clicked.connect(self.eliminar_producto)
        buttons_layout.addWidget(self.btn_eliminar)
        
        self.btn_ajustar_stock = QPushButton("Ajustar Stock")
        self.btn_ajustar_stock.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        self.btn_ajustar_stock.clicked.connect(self.ajustar_stock)
        buttons_layout.addWidget(self.btn_ajustar_stock)
        
        form_layout.addLayout(buttons_layout)
        layout.addLayout(form_layout)
        
        # Botón cerrar
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.setStyleSheet("background-color: #7f8c8d; color: white; font-weight: bold;")
        btn_cerrar.clicked.connect(self.accept)
        layout.addWidget(btn_cerrar)
        
        self.setLayout(layout)
        
        # CARGAR DATOS DESPUÉS de crear toda la interfaz
        self.cargar_categorias_combo()
        self.categoria_combo.currentTextChanged.connect(self.cargar_productos)
        self.cargar_categorias_combo(self.categoria_input)
        
        self.cargar_productos()
        self.limpiar_formulario()
    
    def cargar_categorias_combo(self, combo_box=None):
        """Carga las categorías en un ComboBox"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM categorias WHERE activa = 1 ORDER BY nombre")
            categorias = [row[0] for row in cursor.fetchall()]
            
            if combo_box is not None:
                combo_box.clear()
                combo_box.addItems(categorias)
            else:
                # Solo actualizar si el combo box ya existe
                if hasattr(self, 'categoria_combo'):
                    self.categoria_combo.clear()
                    self.categoria_combo.addItem("Todas")
                    self.categoria_combo.addItems(categorias)

    def codigo_existe(self, codigo):
        """Verifica si el código ya existe en productos ACTIVOS"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos WHERE codigo = ? AND activo = 1", (codigo,))
            return cursor.fetchone()[0] > 0
    
    def cargar_productos(self):
        categoria = self.categoria_combo.currentText()
        
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            if categoria == "Todas":
                cursor.execute("""
                    SELECT p.id, p.codigo, p.nombre, p.precio, p.stock, p.stock_minimo, 
                           c.nombre as categoria_nombre 
                    FROM productos p 
                    LEFT JOIN categorias c ON p.categoria_id = c.id 
                    WHERE p.activo = 1 
                    ORDER BY p.nombre
                """)
            else:
                cursor.execute("""
                    SELECT p.id, p.codigo, p.nombre, p.precio, p.stock, p.stock_minimo, 
                           c.nombre as categoria_nombre 
                    FROM productos p 
                    LEFT JOIN categorias c ON p.categoria_id = c.id 
                    WHERE c.nombre = ? AND p.activo = 1 
                    ORDER BY p.nombre
                """, (categoria,))
            
            productos = cursor.fetchall()
            
            self.table.setRowCount(len(productos))
            for row, (id_, codigo, nombre, precio, stock, stock_min, categoria_nombre) in enumerate(productos):
                self.table.setItem(row, 0, QTableWidgetItem(str(id_)))
                self.table.setItem(row, 1, QTableWidgetItem(codigo))
                self.table.setItem(row, 2, QTableWidgetItem(nombre))
                self.table.setItem(row, 3, QTableWidgetItem(f"${precio:.2f}"))
                self.table.setItem(row, 4, QTableWidgetItem(str(stock)))
                self.table.setItem(row, 5, QTableWidgetItem(str(stock_min)))
                self.table.setItem(row, 6, QTableWidgetItem(categoria_nombre or "Sin categoría"))
                
                # Colorear filas con stock bajo
                if stock <= stock_min:
                    for col in range(7):
                        item = self.table.item(row, col)
                        if item:
                            item.setBackground(QColor("#ffcccc"))
    
    def buscar_producto(self):
        texto = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            item_text = self.table.item(i, 1).text().lower() + " " + self.table.item(i, 2).text().lower()
            if texto in item_text:
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)
    
    def limpiar_formulario(self):
        self.codigo_input.clear()
        self.nombre_input.clear()
        self.precio_input.clear()
        self.stock_input.clear()
        self.stock_min_input.setText("5")
        if self.categoria_input.count() > 0:
            self.categoria_input.setCurrentIndex(0)
        self.current_product_id = None
    
    def get_selected_product(self):
        selected_row = self.table.currentRow()
        if selected_row >= 0:
            return (
                int(self.table.item(selected_row, 0).text()),  # ID
                self.table.item(selected_row, 1).text(),       # Código
                self.table.item(selected_row, 2).text()        # Nombre
            )
        return None
    
    def get_categoria_id(self, nombre_categoria):
        """Obtiene el ID de la categoría por su nombre"""
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM categorias WHERE nombre = ?", (nombre_categoria,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def agregar_producto(self):
        codigo = self.codigo_input.text().strip()
        nombre = self.nombre_input.text().strip()
        precio = self.precio_input.text().strip()
        stock = self.stock_input.text().strip()
        stock_min = self.stock_min_input.text().strip()
        categoria_nombre = self.categoria_input.currentText()
        
        if not all([codigo, nombre, precio, stock]):
            QMessageBox.warning(self, "Error", "Todos los campos son obligatorios")
            return
        
        if self.codigo_existe(codigo):
            QMessageBox.warning(self, "Error", f"El código '{codigo}' ya existe en productos activos. Use un código diferente.")
            return
        
        try:
            precio_val = float(precio)
            stock_val = int(stock)
            stock_min_val = int(stock_min) if stock_min else 5
            
            if precio_val <= 0 or stock_val < 0:
                QMessageBox.warning(self, "Error", "Precio y stock deben ser valores positivos")
                return
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Precio y stock deben ser números válidos")
            return
        
        # Obtener ID de la categoría
        categoria_id = self.get_categoria_id(categoria_nombre)
        if not categoria_id:
            QMessageBox.warning(self, "Error", "Categoría no válida")
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO productos (codigo, nombre, precio, stock, stock_minimo, categoria_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (codigo, nombre, precio_val, stock_val, stock_min_val, categoria_id)
                )
                conn.commit()
            
            QMessageBox.information(self, "Éxito", "Producto agregado correctamente")
            self.cargar_productos()
            self.limpiar_formulario()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo agregar el producto: {str(e)}")
    
    def editar_producto(self):
        selected = self.get_selected_product()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un producto para editar")
            return
        
        product_id, codigo, nombre = selected
        
        nuevo_precio = self.precio_input.text().strip()
        nuevo_stock = self.stock_input.text().strip()
        nuevo_stock_min = self.stock_min_input.text().strip()
        nueva_categoria_nombre = self.categoria_input.currentText()
        
        if not all([nuevo_precio, nuevo_stock]):
            QMessageBox.warning(self, "Error", "Precio y stock son obligatorios")
            return
        
        try:
            precio_val = float(nuevo_precio)
            stock_val = int(nuevo_stock)
            stock_min_val = int(nuevo_stock_min) if nuevo_stock_min else 5
            
            if precio_val <= 0 or stock_val < 0:
                QMessageBox.warning(self, "Error", "Precio y stock deben ser valores positivos")
                return
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Precio y stock deben ser números válidos")
            return
        
        # Obtener ID de la categoría
        categoria_id = self.get_categoria_id(nueva_categoria_nombre)
        if not categoria_id:
            QMessageBox.warning(self, "Error", "Categoría no válida")
            return
        
        try:
            with self.db_manager.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE productos SET precio = ?, stock = ?, stock_minimo = ?, categoria_id = ? WHERE id = ?",
                    (precio_val, stock_val, stock_min_val, categoria_id, product_id)
                )
                conn.commit()
            
            QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
            self.cargar_productos()
            self.limpiar_formulario()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo actualizar el producto: {str(e)}")
    
    def eliminar_producto(self):
        selected = self.get_selected_product()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un producto para eliminar")
            return
        
        product_id, codigo, nombre = selected
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de que quiere eliminar el producto '{nombre}'?"
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    # CAMBIO IMPORTANTE: DELETE en lugar de UPDATE
                    cursor.execute("DELETE FROM productos WHERE id = ?", (product_id,))
                    conn.commit()

                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.cargar_productos()
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar el producto: {str(e)}")
    
    def ajustar_stock(self):
        selected = self.get_selected_product()
        if not selected:
            QMessageBox.warning(self, "Error", "Seleccione un producto")
            return
        
        product_id, codigo, nombre = selected
        
        nuevo_stock, ok = QInputDialog.getInt(
            self, "Ajustar Stock", 
            f"Nuevo stock para '{nombre}':",
            int(self.table.item(self.table.currentRow(), 4).text()), 0, 10000
        )
        
        if ok:
            try:
                with self.db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE productos SET stock = ? WHERE id = ?",
                        (nuevo_stock, product_id)
                    )
                    conn.commit()
                
                QMessageBox.information(self, "Éxito", "Stock ajustado correctamente")
                self.cargar_productos()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo ajustar el stock: {str(e)}")