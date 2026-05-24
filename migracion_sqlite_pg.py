import sqlite3
import psycopg2
from psycopg2.extras import execute_values
from db_manager import conectar_db as conectar_sqlite
from postgres_manager import conectar_postgres, crear_tablas_postgres

def migrar_datos():
    # 1. Asegurar que las tablas existen en destino
    crear_tablas_postgres()
    
    # 2. Conectar a ambas bases de datos
    sqlite_conn = conectar_sqlite()
    sqlite_cursor = sqlite_conn.cursor()
    
    pg_conn = conectar_postgres()
    pg_cursor = pg_conn.cursor()
    
    # === MIGRACIÓN DE PRODUCTOS ===
    print("Migrando Productos...")
    sqlite_cursor.execute("SELECT id_producto, nombre, precio, categoria, disponible FROM Productos")
    productos_sqlite = sqlite_cursor.fetchall()
    
    # Transformar data (disponible: 1/0 a True/False)
    productos_data = []
    for row in productos_sqlite:
        id_prod, nombre, precio, categoria, disponible = row
        disponible_bool = True if disponible else False
        productos_data.append((id_prod, nombre, precio, categoria, disponible_bool))
    
    if productos_data:
        # Usamos execute_values para inserción masiva
        execute_values(
            pg_cursor,
            "INSERT INTO Productos (id_producto, nombre, precio, categoria, disponible) VALUES %s ON CONFLICT (id_producto) DO NOTHING",
            productos_data
        )
        # Actualizar secuencia (ya que forzamos los IDs)
        pg_cursor.execute("SELECT setval('productos_id_producto_seq', (SELECT MAX(id_producto) FROM Productos));")
    
    # === MIGRACIÓN DE PEDIDOS ===
    print("Migrando Pedidos...")
    sqlite_cursor.execute("SELECT id_pedido, nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, hora_pago, total, timestamp_listo FROM Pedidos")
    pedidos_sqlite = sqlite_cursor.fetchall()
    
    # En SQLite a veces las fechas o campos null vienen raros, los pasamos tal cual porque PostgreSQL casteará o aceptará nulos,
    # siempre que estén bien formados.
    if pedidos_sqlite:
        execute_values(
            pg_cursor,
            """INSERT INTO Pedidos (
                id_pedido, nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, hora_pago, total, timestamp_listo
            ) VALUES %s ON CONFLICT (id_pedido) DO NOTHING""",
            pedidos_sqlite
        )
        # Actualizar secuencia
        pg_cursor.execute("SELECT setval('pedidos_id_pedido_seq', (SELECT MAX(id_pedido) FROM Pedidos));")
    
    # 3. Commit y cierre
    pg_conn.commit()
    print("Migración completada con éxito.")
    
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    migrar_datos()
