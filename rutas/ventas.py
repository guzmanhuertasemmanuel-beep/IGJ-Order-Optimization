from flask import Blueprint, render_template, request, jsonify, redirect, session
from postgres_manager import conectar_postgres
from impresora import imprimir_ticket, construir_datos_reimpresion
import datetime

ventas_bp = Blueprint('ventas', __name__)


def _ventas_por_metodo(cursor, fecha=None):
    if fecha:
        cursor.execute("""
            SELECT metodo_pago, COALESCE(SUM(total), 0)
            FROM Pedidos
            WHERE estado = 'Entregado' AND fecha_pedido = %s
            GROUP BY metodo_pago
        """, (fecha,))
    else:
        cursor.execute("""
            SELECT metodo_pago, COALESCE(SUM(total), 0)
            FROM Pedidos
            WHERE estado = 'Entregado'
            GROUP BY metodo_pago
        """)
    efectivo, tarjeta = 0.0, 0.0
    for metodo, monto in cursor.fetchall():
        if metodo == 'efectivo':
            efectivo = float(monto or 0)
        elif metodo == 'tarjeta':
            tarjeta = float(monto or 0)
    return efectivo, tarjeta


@ventas_bp.route("/ventas")
def ventas():
    if not session.get("logueado"):
        return redirect("/login")
    return render_template("ventas.html")


@ventas_bp.route("/api/ventas/resumen")
def api_resumen():
    if not session.get("logueado"):
        return jsonify({"error": "No autorizado"}), 403
    conexion = None
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM Pedidos
            WHERE estado = 'Entregado'
        """)
        acumulado = float(cursor.fetchone()[0] or 0)

        cursor.execute("""
            SELECT producto, COUNT(*) AS frecuencia
            FROM Pedidos
            WHERE estado = 'Entregado'
            GROUP BY producto
            ORDER BY frecuencia DESC
            LIMIT 1
        """)
        fila_top = cursor.fetchone()
        top_producto = {"nombre": fila_top[0], "unidades": int(fila_top[1])} if fila_top else {"nombre": "—", "unidades": 0}

        fecha_hoy = datetime.date.today()
        cursor.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM Pedidos
            WHERE estado = 'Entregado' AND fecha_pedido = %s
        """, (fecha_hoy,))
        total_dia = float(cursor.fetchone()[0] or 0)

        conexion.close()
        return jsonify({
            "acumulado_historico": acumulado,
            "top_producto": top_producto,
            "total_dia": total_dia,
            "fecha_hoy": str(fecha_hoy)
        })
    except Exception as e:
        if conexion:
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500


@ventas_bp.route("/api/ventas/metodos_pago")
def api_metodos_pago():
    if not session.get("logueado"):
        return jsonify({"error": "No autorizado"}), 403
    conexion = None
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()

        ef_hist, tar_hist = _ventas_por_metodo(cursor)
        ef_dia, tar_dia = _ventas_por_metodo(cursor, fecha=datetime.date.today())

        conexion.close()
        return jsonify({
            "historico": {
                "efectivo": ef_hist,
                "tarjeta": tar_hist,
                "total": ef_hist + tar_hist
            },
            "dia": {
                "efectivo": ef_dia,
                "tarjeta": tar_dia,
                "total": ef_dia + tar_dia,
                "fecha": str(datetime.date.today())
            }
        })
    except Exception as e:
        if conexion:
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500


@ventas_bp.route("/api/ventas/pedidos")
def api_pedidos():
    if not session.get("logueado"):
        return jsonify({"error": "No autorizado"}), 403
    conexion = None
    try:
        filtro_metodo = request.args.get("metodo_pago")
        filtro_fecha = request.args.get("fecha")
        filtro_id = request.args.get("id")
        filtro_estado = request.args.get("estado")

        condiciones = []
        parametros = []

        if filtro_metodo:
            condiciones.append("metodo_pago = %s")
            parametros.append(filtro_metodo)
        if filtro_fecha:
            condiciones.append("fecha_pedido = %s")
            parametros.append(filtro_fecha)
        if filtro_id:
            condiciones.append("id_pedido = %s")
            parametros.append(int(filtro_id))
        if filtro_estado:
            condiciones.append("estado = %s")
            parametros.append(filtro_estado)

        where = ("WHERE " + " AND ".join(condiciones)) if condiciones else ""

        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute(f"""
            SELECT id_pedido, fecha_pedido, hora_pedido, total, metodo_pago, producto, estado
            FROM Pedidos
            {where}
            ORDER BY fecha_pedido DESC, hora_pedido DESC
        """, parametros)

        pedidos = [
            {
                "id_pedido": int(row[0]),
                "fecha_hora": f"{row[1]} {str(row[2])[:8]}",
                "total": float(row[3] or 0),
                "metodo_pago": row[4],
                "detalle_productos": row[5],
                "estado": row[6]
            }
            for row in cursor.fetchall()
        ]
        conexion.close()
        return jsonify({"pedidos": pedidos, "total_registros": len(pedidos)})
    except Exception as e:
        if conexion:
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500


@ventas_bp.route("/api/imprimir_ticket/<int:id_pedido>", methods=["POST"])
def api_imprimir_ticket(id_pedido):
    if not session.get("logueado"):
        return jsonify({"error": "No autorizado"}), 403
    conexion = None
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT id_pedido, nombre_cliente, producto, fecha_pedido,
                   hora_pedido, total, metodo_pago
            FROM Pedidos
            WHERE id_pedido = %s
        """, (id_pedido,))
        fila = cursor.fetchone()
        if not fila:
            conexion.close()
            return jsonify({"error": "Pedido no encontrado", "impresion_ok": False}), 404

        datos_ticket = construir_datos_reimpresion(fila, cursor)
        conexion.close()
        imprimir_ticket(datos_ticket)
        return jsonify({"impresion_ok": True})
    except Exception as e:
        if conexion:
            try:
                conexion.close()
            except Exception:
                pass
        return jsonify({"error": str(e), "impresion_ok": False}), 500
