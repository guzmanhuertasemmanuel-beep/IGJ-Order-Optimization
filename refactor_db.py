import os

files = ['rutas/admin.py', 'rutas/cliente.py', 'rutas/cocina.py']

for f_name in files:
    with open(f_name, 'r', encoding='utf-8') as f:
        content = f.read()

    # Reemplazos de conexión
    content = content.replace('from db_manager import conectar_db', 'from postgres_manager import conectar_postgres')
    content = content.replace('conectar_db()', 'conectar_postgres()')
    content = content.replace('import sqlite3\n', '')
    
    # Ajustes booleanos (SQLite maneja 0/1, Postgres maneja True/False para BOOLEAN)
    content = content.replace('VALUES (?, ?, ?, 1)', 'VALUES (%s, %s, %s, True)')
    content = content.replace('disponible = 1', 'disponible = True')
    content = content.replace('estado_actual == 1', 'estado_actual is True')
    content = content.replace('nuevo_estado = 0 if estado_actual == 1 else 1', 'nuevo_estado = False if estado_actual is True else True')
    
    # Reemplazo general de marcadores SQLite (?) a PostgreSQL (%s)
    content = content.replace('?', '%s')

    with open(f_name, 'w', encoding='utf-8') as f:
        f.write(content)

print("Archivos de rutas actualizados exitosamente.")
