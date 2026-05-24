import os
import shutil
import zipfile
from datetime import datetime

SQLITE_DB = "database.db"
BACKUP_DIR = "backups_post_migracion"

def respaldar_y_eliminar():
    if not os.path.exists(SQLITE_DB):
        print(f"El archivo {SQLITE_DB} no existe. No hay nada que limpiar.")
        return

    # 1. Crear directorio de backups
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"Directorio {BACKUP_DIR} creado.")
        
    # 2. Comprimir el archivo SQLite
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"database_backup_{timestamp}.zip")
    
    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(SQLITE_DB)
    print(f"Backup creado exitosamente: {backup_file}")
    
    # 3. Eliminar físicamente la base de datos de SQLite
    try:
        os.remove(SQLITE_DB)
        print(f"Archivo original {SQLITE_DB} eliminado con éxito.")
    except Exception as e:
        print(f"Error al intentar eliminar {SQLITE_DB}: {e}")

if __name__ == "__main__":
    # Este script NO debe ejecutarse automáticamente
    # Solo cuando el usuario envíe la frase clave.
    respaldar_y_eliminar()
