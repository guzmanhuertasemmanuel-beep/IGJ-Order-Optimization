from flask import Blueprint, render_template, redirect, jsonify
from db_manager import conectar_db
import sqlite3
import datetime

cocina_bp = Blueprint('cocina', __name__)

@cocina_bp.route("/pedidos")
def ver_pedidos():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    # Auto-limpieza
    cursor.execute("SELECT id_pedido, timestamp_listo FROM Pedidos WHERE estado='Listo'")
    listos = cursor.fetchall()
    ahora = datetime.datetime.now()
    
    for pedido in listos:
        id_pedido = pedido[0]
        timestamp_str = pedido[1]
        if timestamp_str:
            tiempo_listo = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            if (ahora - tiempo_listo).total_seconds() >= 300: 
                cursor.execute("UPDATE Pedidos SET estado='Entregado' WHERE id_pedido=?", (id_pedido,))
    
    conexion.commit()
    
    cursor.execute("SELECT id_pedido, nombre_cliente, producto, estado FROM Pedidos WHERE estado != 'Entregado' ORDER BY id_pedido ASC")
    pedidos = cursor.fetchall()
    conexion.close()
    
    return render_template("pedidos.html", pedidos=pedidos)

@cocina_bp.route("/api/pedidos")
def api_pedidos():
    conexion = conectar_db()
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
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    ahora_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute(
        "UPDATE Pedidos SET estado='Listo', timestamp_listo=? WHERE id_pedido=?",
        (ahora_str, id)
    )
    conexion.commit()
    conexion.close()

    return redirect("/cocina")

@cocina_bp.route("/cocina")
def cocina():
    conexion = conectar_db()
    cursor = conexion.cursor()
    
    cursor.execute("SELECT id_pedido, nombre_cliente, producto FROM Pedidos WHERE estado='Pendiente' LIMIT 10")
    pedidos = cursor.fetchall()
    cantidad = len(pedidos)
    conexion.close()
    return render_template("cocina.html", pedidos=pedidos, cantidad=cantidad)