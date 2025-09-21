import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name='caja_registradora.db'):
        self.db_name = db_name
        self.is_first_time = not os.path.exists(db_name)
        
        print(f"📦 Base de datos: {db_name}")
        print(f"🆕 Primer uso: {self.is_first_time}")
        
        self.conn = self.create_connection()
        
        # Verificar SI las tablas existen aunque el archivo exista
        if not self.is_first_time:
            if not self.tablas_existen():
                print("⚠️ Archivo de DB existe pero tablas faltan, recreando...")
                self.is_first_time = True
        
        if self.is_first_time:
            print("🔄 Creando tablas e insertando datos iniciales...")
            self.create_tables()
            self.insert_initial_data()
            print("✅ Base de datos inicializada exitosamente")
        else:
            print("✅ Base de datos existente detectada")
    
    def tablas_existen(self):
        """Verifica si las tablas esenciales existen"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
            return cursor.fetchone() is not None
        except:
            return False

    def create_connection(self):
        """Crea conexión a la base de datos"""
        try:
            conn = sqlite3.connect(self.db_name)
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            print(f"❌ Error conectando a la base de datos: {e}")
            return None
        
    def get_connection(self):
        """Retorna la conexión para usar con 'with'"""
        return self.conn

    def create_tables(self):
        """Crea TODAS las tablas necesarias"""
        if not self.conn:
            return
            
        try:
            # Tabla de usuarios
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    nombre TEXT NOT NULL,
                    rol TEXT NOT NULL DEFAULT 'vendedor',
                    activo INTEGER DEFAULT 1,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de categorías
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    descripcion TEXT,
                    color TEXT DEFAULT '#3498db',
                    activa INTEGER DEFAULT 1
                )
            ''')
            
            # Tabla de productos
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    codigo TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    precio REAL NOT NULL,
                    costo REAL DEFAULT 0,
                    stock INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 5,
                    categoria_id INTEGER,
                    activo INTEGER DEFAULT 1,
                    codigo_barras TEXT UNIQUE,
                    FOREIGN KEY (categoria_id) REFERENCES categorias (id)
                )
            ''')
            
            # Tabla de clientes
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    telefono TEXT,
                    email TEXT,
                    direccion TEXT,
                    rfc TEXT,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de ventas
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total REAL NOT NULL,
                    iva REAL NOT NULL,
                    metodo_pago TEXT NOT NULL,
                    cliente_id INTEGER,
                    usuario_id INTEGER NOT NULL,
                    estado TEXT DEFAULT 'completada',
                    FOREIGN KEY (cliente_id) REFERENCES clientes (id),
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de detalle_ventas
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS detalle_ventas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    venta_id INTEGER NOT NULL,
                    producto_id INTEGER NOT NULL,
                    cantidad INTEGER NOT NULL,
                    precio_unitario REAL NOT NULL,
                    subtotal REAL NOT NULL,
                    FOREIGN KEY (venta_id) REFERENCES ventas (id) ON DELETE CASCADE,
                    FOREIGN KEY (producto_id) REFERENCES productos (id)
                )
            ''')
            
            # Tabla de cierres_caja
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS cierres_caja (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha_apertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_cierre TIMESTAMP,
                    usuario_id INTEGER NOT NULL,
                    monto_inicial REAL DEFAULT 0,
                    ventas_efectivo REAL DEFAULT 0,
                    ventas_tarjeta REAL DEFAULT 0,
                    ventas_transferencia REAL DEFAULT 0,
                    total_ventas REAL DEFAULT 0,
                    total_efectivo REAL DEFAULT 0,
                    diferencia REAL DEFAULT 0,
                    observaciones TEXT,
                    estado TEXT DEFAULT 'abierto',
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de backups
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS backups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    nombre_archivo TEXT NOT NULL,
                    tamaño REAL NOT NULL,
                    usuario_id INTEGER,
                    observaciones TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
                )
            ''')
            
            # Tabla de configuración
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS configuracion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clave TEXT UNIQUE NOT NULL,
                    valor TEXT NOT NULL,
                    descripcion TEXT
                )
            ''')
            
            self.conn.commit()
            print("✅ Todas las tablas creadas exitosamente")
            
        except sqlite3.Error as e:
            print(f"❌ Error creando tablas: {e}")

    def insert_initial_data(self):
        """Inserta datos iniciales para primer uso"""
        if not self.conn:
            return
            
        try:
            # Insertar usuario admin por defecto
            self.conn.execute('''
                INSERT INTO usuarios (username, password, nombre, rol)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin123', 'Administrador', 'admin'))
            
            # Insertar usuario vendedor por defecto
            self.conn.execute('''
                INSERT INTO usuarios (username, password, nombre, rol)
                VALUES (?, ?, ?, ?)
            ''', ('vendedor', 'vendedor123', 'Vendedor Principal', 'vendedor'))
            
            # Insertar categorías básicas con colores
            categorias = [
                ('Electrónicos', 'Productos electrónicos y tecnología', '#e74c3c'),
                ('Ropa', 'Prendas de vestir y accesorios', '#3498db'),
                ('Alimentos', 'Productos alimenticios y bebidas', '#2ecc71'),
                ('Hogar', 'Artículos para el hogar y decoración', '#e67e22'),
                ('Limpieza', 'Productos de limpieza y cuidado del hogar', '#9b59b6'),
                ('Oficina', 'Material de oficina y papelería', '#f1c40f')
            ]
            
            self.conn.executemany('''
                INSERT INTO categorias (nombre, descripcion, color)
                VALUES (?, ?, ?)
            ''', categorias)
            
            # Insertar algunos productos de ejemplo
            productos = [
                ('P001', 'Laptop HP 15"', 'Laptop HP 15 pulgadas, 8GB RAM, 256GB SSD', 12000.00, 9000.00, 10, 2, 1),
                ('P002', 'Mouse Inalámbrico', 'Mouse óptico inalámbrico', 250.00, 150.00, 25, 5, 1),
                ('P003', 'Teclado Mecánico', 'Teclado mecánico RGB', 800.00, 500.00, 15, 3, 1),
                ('P004', 'Camisa Casual', 'Camisa de algodón 100%', 350.00, 200.00, 30, 5, 2)
            ]
            
            self.conn.executemany('''
                INSERT INTO productos (codigo, nombre, descripcion, precio, costo, stock, stock_minimo, categoria_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', productos)
            
            # Insertar configuración inicial
            configuraciones = [
                ('iva', '0.16', 'Porcentaje de IVA (0.16 = 16%)'),
                ('moneda', '$', 'Símbolo de moneda'),
                ('empresa', 'Mi Tienda', 'Nombre de la empresa'),
                ('telefono', '', 'Teléfono de la empresa'),
                ('direccion', '', 'Dirección de la empresa'),
                ('backup_automatico', '1', 'Backup automático activado'),
                ('stock_minimo_alerta', '5', 'Stock mínimo para alertas')
            ]
            
            self.conn.executemany('''
                INSERT INTO configuracion (clave, valor, descripcion)
                VALUES (?, ?, ?)
            ''', configuraciones)
            
            self.conn.commit()
            print("✅ Datos iniciales insertados")
            print("   👤 Usuario admin: admin / admin123")
            print("   👤 Usuario vendedor: vendedor / vendedor123")
            print("   🏪 Configuración básica establecida")
            print("   📦 Categorías de ejemplo creadas")
            print("   🛒 Productos de ejemplo agregados")
            
        except sqlite3.Error as e:
            print(f"❌ Error insertando datos iniciales: {e}")

    # ===== MÉTODOS PARA VENTAS =====
    def registrar_venta(self, venta_data, detalle_venta):
        """Registra una venta y su detalle"""
        try:
            cursor = self.conn.cursor()
            
            # Insertar venta principal
            cursor.execute('''
                INSERT INTO ventas (total, iva, metodo_pago, cliente_id, usuario_id, estado)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                venta_data['total'],
                venta_data['iva'],
                venta_data['metodo_pago'],
                venta_data.get('cliente_id'),
                venta_data['usuario_id'],
                venta_data.get('estado', 'completada')
            ))
            
            venta_id = cursor.lastrowid
            
            # Insertar detalle de venta
            for item in detalle_venta:
                cursor.execute('''
                    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    venta_id,
                    item['producto_id'],
                    item['cantidad'],
                    item['precio_unitario'],
                    item['subtotal']
                ))
                
                # Actualizar stock
                cursor.execute('''
                    UPDATE productos SET stock = stock - ? WHERE id = ?
                ''', (item['cantidad'], item['producto_id']))
            
            self.conn.commit()
            return venta_id
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"❌ Error registrando venta: {e}")
            return None

    # ===== MÉTODOS PARA CIERRES DE CAJA =====
    def abrir_caja(self, usuario_id, monto_inicial=0):
        """Abre un turno de caja"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO cierres_caja (usuario_id, monto_inicial, estado)
                VALUES (?, ?, 'abierto')
            ''', (usuario_id, monto_inicial))
            
            self.conn.commit()
            return cursor.lastrowid
            
        except sqlite3.Error as e:
            print(f"❌ Error abriendo caja: {e}")
            return None

    def cerrar_caja(self, cierre_id, datos_cierre):
        """Cierra un turno de caja"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE cierres_caja 
                SET fecha_cierre = CURRENT_TIMESTAMP,
                    ventas_efectivo = ?,
                    ventas_tarjeta = ?,
                    ventas_transferencia = ?,
                    total_ventas = ?,
                    total_efectivo = ?,
                    diferencia = ?,
                    observaciones = ?,
                    estado = 'cerrado'
                WHERE id = ?
            ''', (
                datos_cierre['ventas_efectivo'],
                datos_cierre['ventas_tarjeta'],
                datos_cierre['ventas_transferencia'],
                datos_cierre['total_ventas'],
                datos_cierre['total_efectivo'],
                datos_cierre['diferencia'],
                datos_cierre.get('observaciones', ''),
                cierre_id
            ))
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"❌ Error cerrando caja: {e}")
            return False

    # ===== MÉTODOS GENERALES =====
    def ejecutar_consulta(self, consulta, parametros=()):
        """Ejecuta una consulta y retorna resultados"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(consulta, parametros)
            
            if consulta.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.conn.commit()
                return cursor.rowcount
                
        except sqlite3.Error as e:
            print(f"❌ Error en consulta: {e}")
            return None

    def cerrar_conexion(self):
        """Cierra la conexión a la base de datos"""
        if self.conn:
            self.conn.close()
            print("✅ Conexión a base de datos cerrada")

    def __del__(self):
        """Destructor - cierra la conexión automáticamente"""
        self.cerrar_conexion()