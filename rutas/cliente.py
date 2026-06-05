from flask import Blueprint, render_template, request, jsonify
from postgres_manager import conectar_postgres
from impresora import imprimir_ticket, construir_datos_reimpresion
import datetime

cliente_bp = Blueprint('cliente', __name__)


@cliente_bp.route("/")
def inicio():
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre, precio FROM Productos WHERE disponible = True")
        productos = cursor.fetchall()
        conexion.close()
        return render_template("index.html", productos=productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cliente_bp.route("/nuevo_pedido", methods=["POST"])
def nuevo_pedido():
    cliente = request.form["cliente"]
    metodo_pago = request.form["metodo_pago"]
    conexion = None
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()

        productos_pedidos = []
        detalle_productos = []
        total_pagar = 0.0

        for llave, valor in request.form.items():
            if llave.startswith("cantidad_") and valor.isdigit() and int(valor) > 0:
                nombre_producto = llave.replace("cantidad_", "")
                cantidad = int(valor)
                cursor.execute("SELECT precio FROM Productos WHERE nombre = %s", (nombre_producto,))
                resultado = cursor.fetchone()
                if resultado:
                    precio_unitario = float(resultado[0])
                    subtotal = cantidad * precio_unitario
                    total_pagar += subtotal
                    productos_pedidos.append(f"{cantidad}x {nombre_producto}")
                    detalle_productos.append({
                        "nombre": nombre_producto,
                        "cantidad": cantidad,
                        "subtotal": subtotal
                    })

        if not productos_pedidos:
            conexion.close()
            return """
                <div style="text-align: center; margin-top: 50px; font-family: 'Segoe UI', Tahoma, sans-serif;">
                    <h2 style="color: #C41230;">¡Ups! Pedido vacío</h2>
                    <p>No seleccionaste ninguna cantidad. Por favor, elige al menos un producto.</p>
                    <br>
                    <a href="/" style="padding: 10px 20px; background-color: #004581; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">← Volver al menú</a>
                </div>
            """

        fecha_actual = datetime.date.today()
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")

        cursor.execute("""
            INSERT INTO Pedidos (nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, total)
            VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s)
            RETURNING id_pedido
        """, (cliente, ", ".join(productos_pedidos), fecha_actual, hora_actual, metodo_pago, total_pagar))

        id_pedido = cursor.fetchone()[0]
        conexion.commit()
        conexion.close()

        try:
            imprimir_ticket({
                "id_pedido": id_pedido,
                "nombre_cliente": cliente,
                "fecha": fecha_actual.strftime("%d/%m/%Y"),
                "hora": hora_actual[:5],
                "productos": detalle_productos,
                "total": total_pagar,
                "metodo_pago": metodo_pago
            })
        except Exception:
            pass

        return render_template("confirmacion.html", total=total_pagar)
    except Exception as e:
        if conexion:
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500


@cliente_bp.route("/api/menu", methods=["GET"])
def api_get_menu():
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, precio, categoria FROM Productos WHERE disponible = True")
        columnas = [column[0] for column in cursor.description]
        productos = [dict(zip(columnas, row)) for row in cursor.fetchall()]
        conexion.close()
        return jsonify(productos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cliente_bp.route("/api/nuevo_pedido", methods=["POST"])
def api_nuevo_pedido():
    conexion = None
    try:
        datos = request.get_json()
        nombre_cliente = datos.get('nombre_cliente')
        producto = datos.get('producto')
        metodo_pago = datos.get('metodo_pago')
        total = float(datos.get('total', 0))
        fecha_actual = datetime.date.today()
        hora_actual = datetime.datetime.now().time()

        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Pedidos (nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, total)
            VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s)
            RETURNING id_pedido
        """, (nombre_cliente, producto, fecha_actual, hora_actual, metodo_pago, total))

        id_pedido = cursor.fetchone()[0]
        conexion.commit()

        impresion_ok = False
        try:
            datos_ticket = construir_datos_reimpresion(
                (id_pedido, nombre_cliente, producto, fecha_actual, hora_actual, total, metodo_pago),
                cursor
            )
            impresion_ok = imprimir_ticket(datos_ticket)
        except Exception:
            pass

        conexion.close()
        return jsonify({
            "mensaje": "Pedido recibido en la cocina del IGJ",
            "impresion_ok": impresion_ok
        }), 201
    except Exception as e:
        if conexion:
            conexion.rollback()
            conexion.close()
        return jsonify({"error": f"{type(e).__name__}: {str(e)}"}), 500