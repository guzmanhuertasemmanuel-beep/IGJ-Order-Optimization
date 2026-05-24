import sqlite3
import psycopg2
from db_manager import conectar_db as conectar_sqlite
from postgres_manager import conectar_postgres

def verificar_migracion():
    print("--- Verificación de Migración ---")
    
    sqlite_conn = conectar_sqlite()
    sqlite_cursor = sqlite_conn.cursor()
    
    pg_conn = conectar_postgres()
    pg_cursor = pg_conn.cursor()
    
    # Conteo Productos
    sqlite_cursor.execute("SELECT COUNT(*) FROM Productos")
    count_prod_sq = sqlite_cursor.fetchone()[0]
    
    pg_cursor.execute("SELECT COUNT(*) FROM Productos")
    count_prod_pg = pg_cursor.fetchone()[0]
    
    print(f"Productos - SQLite: {count_prod_sq} | PostgreSQL: {count_prod_pg}")
    if count_prod_sq == count_prod_pg:
        print("[OK] Conteo de Productos coincide.")
    else:
        print("[ERROR] Conteo de Productos NO coincide.")
        
    # Conteo Pedidos
    sqlite_cursor.execute("SELECT COUNT(*) FROM Pedidos")
    count_ped_sq = sqlite_cursor.fetchone()[0]
    
    pg_cursor.execute("SELECT COUNT(*) FROM Pedidos")
    count_ped_pg = pg_cursor.fetchone()[0]
    
    print(f"Pedidos - SQLite: {count_ped_sq} | PostgreSQL: {count_ped_pg}")
    if count_ped_sq == count_ped_pg:
        print("[OK] Conteo de Pedidos coincide.")
    else:
        print("[ERROR] Conteo de Pedidos NO coincide.")
        
    sqlite_conn.close()
    pg_conn.close()

if __name__ == "__main__":
    verificar_migracion()
