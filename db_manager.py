import sqlite3

def conectar_db():
    # check_same_thread=False es vital para que SQLite funcione bien con Blueprints
    return sqlite3.connect("database.db", check_same_thread=False)

def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    # Tabla Productos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        categoria TEXT,
        disponible BOOLEAN
    )
    """)

    # Tabla Pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_cliente TEXT,
        producto TEXT,           
        fecha_pedido DATE,
        hora_pedido TIME,
        estado TEXT,
        metodo_pago TEXT,
        hora_pago TIME,
        total REAL,
        timestamp_listo TEXT
    )
    """)

    conexion.commit()
    conexion.close()