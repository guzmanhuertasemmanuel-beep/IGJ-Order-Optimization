import os
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def conectar_postgres():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres_pass"),
        dbname=os.getenv("DB_NAME", "igj_optimization_bd")
    )

def crear_tablas_postgres():
    conexion = conectar_postgres()
    cursor = conexion.cursor()

    # Tabla Productos (PostgreSQL DDL)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Productos (
        id_producto SERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        precio NUMERIC(10, 2) NOT NULL,
        categoria TEXT,
        disponible BOOLEAN
    )
    """)

    # Tabla Pedidos (PostgreSQL DDL)
    # Se mantiene el campo producto como TEXT según lo solicitado.
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pedidos (
        id_pedido SERIAL PRIMARY KEY,
        nombre_cliente TEXT,
        producto TEXT,
        fecha_pedido DATE,
        hora_pedido TIME,
        estado TEXT,
        metodo_pago TEXT,
        hora_pago TIME,
        total NUMERIC(10, 2),
        timestamp_listo TIMESTAMP
    )
    """)

    conexion.commit()
    cursor.close()
    conexion.close()

if __name__ == "__main__":
    crear_tablas_postgres()
    print("Tablas creadas en PostgreSQL correctamente.")
