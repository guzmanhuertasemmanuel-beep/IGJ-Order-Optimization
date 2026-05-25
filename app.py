from flask import Flask
import threading  # Permite ejecutar tareas en segundo plano sin congelar Flask
import time       # Nos sirve para pausar el ciclo y que no sature el procesador
import datetime   # Para comparar las horas y fechas de los pedidos
from postgres_manager import conectar_postgres  # Necesitamos conectar con PostgreSQL desde aquí

def limpieza_automatica_pedidos():
    while True:
        # 1. Pausa de seguridad: Espera 30 segundos antes de volver a revisar la BD.
        # Esto evita que el servidor consuma el 100% del procesador en un bucle infinito.
        time.sleep(30) 
        
        try:
            # 2. Abrimos una conexión exclusiva para este hilo secundario
            conexion = conectar_postgres()
            cursor = conexion.cursor()
            ahora = datetime.datetime.now()
            
            # 3. Buscamos únicamente los pedidos que ya estén marcados como 'Listo'
            cursor.execute("SELECT id_pedido, timestamp_listo FROM Pedidos WHERE estado='Listo'")
            listos = cursor.fetchall()
            
            # 4. Evaluamos cada uno de los pedidos encontrados
            for pedido in listos:
                id_pedido = pedido[0]
                timestamp_str = pedido[1]
                
                if timestamp_str:
                    # Convertimos el texto de la BD a un objeto de tiempo real en Python
                    tiempo_listo = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    # 5. Restamos el tiempo actual menos el tiempo en que se marcó listo.
                    # Si la diferencia es de 300 segundos (5 minutos) o más, se cambia el estado.
                    if (ahora - tiempo_listo).total_seconds() >= 300: 
                        cursor.execute(
                            "UPDATE Pedidos SET estado='Entregado' WHERE id_pedido=%s", 
                            (id_pedido,)
                        )
            
            # 6. Guardamos los cambios y cerramos la conexión de forma limpia
            conexion.commit()
            conexion.close()
            
        except Exception as e:
            # Si ocurre algún error (por ejemplo, base de datos ocupada), 
            # lo muestra en la consola para que te enteres, pero NO tumba el servidor.
            print(f"[Sistema de Limpieza] Error: {e}")

            # Creamos el hilo y lo configuramos como 'daemon=True'.
# Esto es vital: significa que si tú apagas Flask (Ctrl+C), el hilo de limpieza también muere.
hilo_limpieza = threading.Thread(target=limpieza_automatica_pedidos, daemon=True)

# Arranca el proceso en paralelo de inmediato
hilo_limpieza.start()

from postgres_manager import crear_tablas_postgres

# Importamos los módulos (Blueprints)
from rutas.cliente import cliente_bp
from rutas.cocina import cocina_bp
from rutas.admin import admin_bp

app = Flask(__name__)
app.secret_key = "super_secreta_igj_2026"

# Registramos las rutas en la aplicación principal
# Agregamos el prefijo /api para que actúe como paraguas de las rutas móviles
app.register_blueprint(cliente_bp)
app.register_blueprint(cocina_bp)
app.register_blueprint(admin_bp)

# Aseguramos que las tablas existan al iniciar
crear_tablas_postgres()

if __name__ == "__main__":
    app.run(debug=True)