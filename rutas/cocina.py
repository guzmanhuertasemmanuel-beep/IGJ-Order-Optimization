from flask import Blueprint, render_template, redirect, jsonify
from postgres_manager import conectar_postgres
import datetime

cocina_bp = Blueprint('cocina', __name__)

_QUERY_PEDIDOS_ACTIVOS = """
    SELECT id_pedido, nombre_cliente, producto, estado
    FROM Pedidos
    WHERE estado != 'Entregado'
    ORDER BY id_pedido ASC
"""


@cocina_bp.route("/pedidos")
def ver_pedidos():
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute(_QUERY_PEDIDOS_ACTIVOS)
        pedidos = cursor.fetchall()
        conexion.close()
        return render_template("pedidos.html", pedidos=pedidos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocina_bp.route("/api/pedidos")
def api_pedidos():
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute(_QUERY_PEDIDOS_ACTIVOS)
        pedidos = cursor.fetchall()
        conexion.close()
        return jsonify([
            {"id": p[0], "cliente": p[1], "producto": p[2], "estado": p[3]}
            for p in pedidos
        ])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cocina_bp.route("/pedido_listo/<int:id>", methods=["POST"])
def pedido_listo(id):
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE Pedidos SET estado='Listo', timestamp_listo=%s WHERE id_pedido=%s",
            (datetime.datetime.now(), id)
        )
        conexion.commit()
        conexion.close()
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500
    return redirect("/cocina")


@cocina_bp.route("/cocina")
def cocina():
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_pedido, nombre_cliente, producto FROM Pedidos WHERE estado='Pendiente' LIMIT 10")
        pedidos = cursor.fetchall()
        conexion.close()
        return render_template("cocina.html", pedidos=pedidos, cantidad=len(pedidos))
    except Exception as e:
        return jsonify({"error": str(e)}), 500