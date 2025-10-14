"""
Sistema de temas para Caja Registradora
Temas disponibles: claro, oscuro
"""

def obtener_tema_claro():
    """Tema claro - estilo moderno y limpio"""
    return """
    /* ====== TEMA CLARO ====== */
    QWidget {
        background-color: #f8f9fa;
        color: #212529;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 9pt;
    }
    
    QMainWindow, QDialog {
        background-color: #f8f9fa;
    }
    
    QLabel {
        color: #212529;
        background-color: transparent;
    }
    
    QPushButton {
        background-color: #007bff;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        margin: 2px;
    }
    
    QPushButton:hover {
        background-color: #0056b3;
    }
    
    QPushButton:pressed {
        background-color: #004085;
    }
    
    QGroupBox {
        background-color: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 20px;
        font-weight: bold;
        color: #495057;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        background-color: white;
    }
    
    QTableWidget {
        background-color: white;
        gridline-color: #dee2e6;
        border: 1px solid #dee2e6;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #f8f9fa;
    }
    
    QHeaderView::section {
        background-color: #e9ecef;
        color: #495057;
        padding: 10px;
        border: none;
        font-weight: bold;
    }
    
    QLineEdit, QComboBox {
        background-color: white;
        border: 2px solid #ced4da;
        padding: 8px;
        border-radius: 4px;
        min-height: 30px;
    }
    
    QLineEdit:focus, QComboBox:focus {
        border-color: #007bff;
    }
    
    QListWidget {
        background-color: white;
        border: 1px solid #ced4da;
        border-radius: 4px;
    }
    
    QTabWidget::pane {
        border: 1px solid #dee2e6;
        background-color: white;
    }
    
    QTabBar::tab {
        background-color: #e9ecef;
        color: #495057;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: white;
        color: #007bff;
        border-bottom: 2px solid #007bff;
    }
    
    /* Estilos específicos para labels importantes */
    QLabel[text*="Total"] {
        color: #dc3545;
        font-size: 18px;
        font-weight: bold;
        background-color: white;
        border: 2px solid #dc3545;
        border-radius: 6px;
        padding: 10px;
    }
    
    /* ====== CORRECCIONES PARA SELECCIONES ====== */
    QListWidget::item:selected,
    QTableWidget::item:selected {
        background-color: #007bff;
        color: #ffffff;
        border: 1px solid #0056b3;
        font-weight: bold;
    }
    
    QListWidget::item:focus,
    QTableWidget::item:focus {
        background-color: #007bff;
        color: #ffffff;
        border: 1px solid #0056b3;
        font-weight: bold;
    }
    
    QListWidget::item:hover,
    QTableWidget::item:hover {
        background-color: #e9ecef;
        color: #212529;
        border: 1px solid #dee2e6;
    }
    
    QTableWidget::item:selected {
        background-color: #007bff;
        color: #ffffff;
    }
    
    QListWidget::item:selected {
        background-color: #007bff;
        color: #ffffff;
    }
    """

def obtener_tema_oscuro():
    """Tema oscuro - elegante y moderno"""
    return """
    /* ====== TEMA OSCURO ====== */
    QWidget {
        background-color: #1a1d21;
        color: #e9ecef;
        font-family: "Segoe UI", Arial, sans-serif;
        font-size: 9pt;
    }
    
    QMainWindow, QDialog {
        background-color: #1a1d21;
    }
    
    QLabel {
        color: #e9ecef;
        background-color: transparent;
    }
    
    QPushButton {
        background-color: #0d6efd;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        font-weight: bold;
        margin: 2px;
    }
    
    QPushButton:hover {
        background-color: #0b5ed7;
    }
    
    QPushButton:pressed {
        background-color: #0a58ca;
    }
    
    QGroupBox {
        background-color: #2d3239;
        border: 2px solid #495057;
        border-radius: 8px;
        margin-top: 10px;
        padding-top: 20px;
        font-weight: bold;
        color: #e9ecef;
    }
    
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        background-color: #2d3239;
        color: #e9ecef;
    }
    
    QTableWidget {
        background-color: #2d3239;
        gridline-color: #495057;
        border: 1px solid #495057;
        color: #e9ecef;
    }
    
    QTableWidget::item {
        padding: 8px;
        border-bottom: 1px solid #3d4249;
        color: #e9ecef;
    }
    
    QHeaderView::section {
        background-color: #495057;
        color: #e9ecef;
        padding: 10px;
        border: none;
        font-weight: bold;
    }
    
    QLineEdit, QComboBox {
        background-color: #2d3239;
        color: #e9ecef;
        border: 2px solid #495057;
        padding: 8px;
        border-radius: 4px;
        min-height: 30px;
    }
    
    QLineEdit:focus, QComboBox:focus {
        border-color: #0d6efd;
    }
    
    QListWidget {
        background-color: #2d3239;
        color: #e9ecef;
        border: 1px solid #495057;
        border-radius: 4px;
    }
    
    QTabWidget::pane {
        border: 1px solid #495057;
        background-color: #2d3239;
    }
    
    QTabBar::tab {
        background-color: #495057;
        color: #e9ecef;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 4px;
        border-top-right-radius: 4px;
    }
    
    QTabBar::tab:selected {
        background-color: #1a1d21;
        color: #0d6efd;
        border-bottom: 2px solid #0d6efd;
    }
    
    /* Estilos específicos para labels importantes */
    QLabel[text*="Total"] {
        color: #ff6b6b;
        font-size: 18px;
        font-weight: bold;
        background-color: #2d3239;
        border: 2px solid #ff6b6b;
        border-radius: 6px;
        padding: 10px;
    }
    
    /* ====== CORRECCIONES PARA SELECCIONES ====== */
    QListWidget::item:selected,
    QTableWidget::item:selected {
        background-color: #0d6efd;
        color: #ffffff;
        border: 1px solid #0b5ed7;
        font-weight: bold;
    }
    
    QListWidget::item:focus,
    QTableWidget::item:focus {
        background-color: #0d6efd;
        color: #ffffff;
        border: 1px solid #0b5ed7;
        font-weight: bold;
    }
    
    QListWidget::item:hover,
    QTableWidget::item:hover {
        background-color: #3d4249;
        color: #e9ecef;
        border: 1px solid #495057;
    }
    
    QTableWidget::item:selected {
        background-color: #0d6efd;
        color: #ffffff;
    }
    
    QListWidget::item:selected {
        background-color: #0d6efd;
        color: #ffffff;
    }
    """

def obtener_tema(tema_nombre):
    """Obtener tema por nombre"""
    temas = {
        'claro': obtener_tema_claro,
        'oscuro': obtener_tema_oscuro
    }
    
    if tema_nombre in temas:
        return temas[tema_nombre]()
    else:
        print(f"⚠️ Tema '{tema_nombre}' no encontrado, usando tema claro")
        return obtener_tema_claro()

def listar_temas_disponibles():
    """Listar todos los temas disponibles"""
    return ['claro', 'oscuro']