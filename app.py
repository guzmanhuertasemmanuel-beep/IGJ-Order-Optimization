from flask import Flask
import threading
import time
import datetime
from postgres_manager import conectar_postgres

def limpieza_automatica_pedidos():
    while True:
        time.sleep(30)
        try:
            conexion = conectar_postgres()
            cursor = conexion.cursor()
            ahora = datetime.datetime.now()

            cursor.execute("SELECT id_pedido, timestamp_listo FROM Pedidos WHERE estado='Listo'")
            listos = cursor.fetchall()

            for pedido in listos:
                id_pedido = pedido[0]
                timestamp_listo = pedido[1]
                if timestamp_listo:
                    if isinstance(timestamp_listo, str):
                        timestamp_listo = datetime.datetime.strptime(timestamp_listo, "%Y-%m-%d %H:%M:%S")
                    if (ahora - timestamp_listo).total_seconds() >= 300:
                        cursor.execute(
                            "UPDATE Pedidos SET estado='Entregado' WHERE id_pedido=%s",
                            (id_pedido,)
                        )

            conexion.commit()
            conexion.close()
        except Exception as e:
            print(f"[Sistema de Limpieza] Error: {e}")

hilo_limpieza = threading.Thread(target=limpieza_automatica_pedidos, daemon=True)
hilo_limpieza.start()

from postgres_manager import crear_tablas_postgres
from rutas.cliente import cliente_bp
from rutas.cocina import cocina_bp
from rutas.admin import admin_bp

app = Flask(__name__)
app.secret_key = "super_secreta_igj_2026"

app.register_blueprint(cliente_bp)
app.register_blueprint(cocina_bp)
app.register_blueprint(admin_bp)

crear_tablas_postgres()

if __name__ == "__main__":
    app.run(debug=True)