import sqlite3

def conectar_db():
    return sqlite3.connect("database.db", check_same_thread=False)

def crear_tablas():
    conexion = conectar_db()
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Productos (
        id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        precio REAL NOT NULL,
        categoria TEXT,
        disponible BOOLEAN
    )
    """)

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