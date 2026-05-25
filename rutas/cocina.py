from flask import Blueprint, render_template, redirect, jsonify
from postgres_manager import conectar_postgres
import datetime

cocina_bp = Blueprint('cocina', __name__)

@cocina_bp.route("/pedidos")
def ver_pedidos():
    # Abrimos la base de datos
    conexion = conectar_postgres()
    cursor = conexion.cursor()
    
    # Traemos de forma directa solo los pedidos activos para mostrarlos en la UI de la web
    cursor.execute("SELECT id_pedido, nombre_cliente, producto, estado FROM Pedidos WHERE estado != 'Entregado' ORDER BY id_pedido ASC")
    pedidos = cursor.fetchall()
    conexion.close()
    
    # Renderizamos la plantilla con los datos actualizados
    return render_template("pedidos.html", pedidos=pedidos)

@cocina_bp.route("/api/pedidos")
def api_pedidos():
    conexion = conectar_postgres()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id_pedido, nombre_cliente, producto, estado FROM Pedidos WHERE estado != 'Entregado' ORDER BY id_pedido ASC")
    pedidos = cursor.fetchall()
    conexion.close()

    pedidos_datos = []
    for p in pedidos:
        pedidos_datos.append({
            "id": p[0],
            "cliente": p[1],
            "producto": p[2],
            "estado": p[3]
        })
    
    return jsonify(pedidos_datos)

@cocina_bp.route("/pedido_listo/<int:id>", methods=["POST"])
def pedido_listo(id):
    conexion = conectar_postgres()
    cursor = conexion.cursor()
    
    ahora_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "UPDATE Pedidos SET estado='Listo', timestamp_listo=%s WHERE id_pedido=%s",
        (ahora_str, id)
    )
    conexion.commit()
    conexion.close()

    return redirect("/cocina")

@cocina_bp.route("/cocina")
def cocina():
    conexion = conectar_postgres()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id_pedido, nombre_cliente, producto FROM Pedidos WHERE estado='Pendiente' LIMIT 10")
    pedidos = cursor.fetchall()
    cantidad = len(pedidos)
    conexion.close()
    return render_template("cocina.html", pedidos=pedidos, cantidad=cantidad)