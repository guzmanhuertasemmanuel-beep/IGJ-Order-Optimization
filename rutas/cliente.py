from flask import Blueprint, render_template, request, jsonify
from db_manager import conectar_db
import datetime

cliente_bp = Blueprint('cliente', __name__)

@cliente_bp.route("/")
def inicio():
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, precio FROM Productos WHERE disponible = 1")
    productos = cursor.fetchall()
    conexion.close()
    return render_template("index.html", productos=productos)

@cliente_bp.route("/nuevo_pedido", methods=["POST"])
def nuevo_pedido():
    cliente = request.form["cliente"]
    metodo_pago = request.form["metodo_pago"]

    conexion = conectar_db()
    cursor = conexion.cursor()

    productos_pedidos = []
    total_pagar = 0.0

    for llave, valor in request.form.items():
        if llave.startswith("cantidad_") and valor.isdigit() and int(valor) > 0:
            nombre_producto = llave.replace("cantidad_", "")
            cantidad = int(valor)
            
            cursor.execute("SELECT precio FROM Productos WHERE nombre = ?", (nombre_producto,))
            resultado = cursor.fetchone()
            
            if resultado:
                precio_unitario = resultado[0]
                total_pagar += (cantidad * precio_unitario)
                productos_pedidos.append(f"{cantidad}x {nombre_producto}")

    if len(productos_pedidos) == 0:
        conexion.close()
        return """
            <div style="text-align: center; margin-top: 50px; font-family: 'Segoe UI', Tahoma, sans-serif;">
                <h2 style="color: #C41230;">¡Ups! Pedido vacío</h2>
                <p>No seleccionaste ninguna cantidad. Por favor, elige al menos un producto.</p>
                <br>
                <a href="/" style="padding: 10px 20px; background-color: #004581; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">← Volver al menú</a>
            </div>
        """

    producto_final = ", ".join(productos_pedidos)
    fecha = datetime.date.today()
    hora = datetime.datetime.now().strftime("%H:%M:%S")

    cursor.execute("""
    INSERT INTO Pedidos (nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, total)
    VALUES (?, ?, ?, ?, 'Pendiente', ?, ?)
    """, (cliente, producto_final, fecha, hora, metodo_pago, total_pagar))

    conexion.commit()
    conexion.close()

    return render_template("confirmacion.html", total=total_pagar)
from flask import jsonify # Añade esto a tus importaciones arriba

# ... código existente ...

@cliente_bp.route("/api/nuevo_pedido", methods=["POST"])
def api_nuevo_pedido():
    # request.get_json() convierte el texto JSON de Java en un diccionario de Python
    datos = request.get_json()

    if not datos:
        return jsonify({"error": "No se recibió información en formato JSON"}), 400

    # Extraemos los datos enviados desde el App.java
    cliente = datos.get("nombre_cliente")
    producto = datos.get("producto")
    metodo_pago = datos.get("metodo_pago")
    total = datos.get("total")

    # Generamos la fecha y hora actuales
    fecha = datetime.date.today()
    hora = datetime.datetime.now().strftime("%H:%M:%S")

    # Guardamos en la base de datos usando tu db_manager
    conexion = conectar_db()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
        INSERT INTO Pedidos (nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, total)
        VALUES (?, ?, ?, ?, 'Pendiente', ?, ?)
        """, (cliente, producto, fecha, hora, metodo_pago, total))
        
        conexion.commit()
    except Exception as e:
        conexion.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        conexion.close()

    # Respondemos a la app de Java confirmando la operación
    return jsonify({
        "mensaje": "¡Pedido registrado exitosamente en la base de datos!",
        "cliente": cliente,
        "total": total
    }), 201

# ... código existente ...
