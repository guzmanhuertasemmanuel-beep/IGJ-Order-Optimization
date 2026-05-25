from flask import Blueprint, render_template, request, jsonify
from postgres_manager import conectar_postgres
import datetime

# ¡Solo creamos el Blueprint UNA VEZ!
cliente_bp = Blueprint('cliente', __name__)

# ==========================================
# RUTAS WEB (Para el navegador y HTML)
# ==========================================

@cliente_bp.route("/")
def inicio():
    conexion = conectar_postgres()
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre, precio FROM Productos WHERE disponible = True")
    productos = cursor.fetchall()
    conexion.close()
    return render_template("index.html", productos=productos)

@cliente_bp.route("/nuevo_pedido", methods=["POST"])
def nuevo_pedido():
    cliente = request.form["cliente"]
    metodo_pago = request.form["metodo_pago"]

    conexion = conectar_postgres()
    cursor = conexion.cursor()

    productos_pedidos = []
    total_pagar = 0.0

    for llave, valor in request.form.items():
        if llave.startswith("cantidad_") and valor.isdigit() and int(valor) > 0:
            nombre_producto = llave.replace("cantidad_", "")
            cantidad = int(valor)
            
            cursor.execute("SELECT precio FROM Productos WHERE nombre = %s", (nombre_producto,))
            resultado = cursor.fetchone()
            
            if resultado:
                precio_unitario = resultado[0]
                total_pagar += float(cantidad * precio_unitario)
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
    VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s)
    """, (cliente, producto_final, fecha, hora, metodo_pago, total_pagar))

    conexion.commit()
    conexion.close()

    return render_template("confirmacion.html", total=total_pagar)

# ==========================================
# RUTAS API (Para la aplicación móvil de Java)
# ==========================================

@cliente_bp.route("/api/menu", methods=["GET"])
def api_get_menu():
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        # Solo traemos productos disponibles
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
        # FIX: Forzar conversion a float. Si Java envia "15.50" como string, esto lo convierte.
        # Si ya es un numero, float() lo acepta sin problema.
        total = float(datos.get('total', 0))
        
        # FIX: Usar objetos nativos de Python en lugar de strings para que psycopg2
        # los mapee correctamente a los tipos DATE y TIME de PostgreSQL.
        fecha_actual = datetime.date.today()
        hora_actual = datetime.datetime.now().time()
        
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        
        cursor.execute("""
            INSERT INTO Pedidos (nombre_cliente, producto, fecha_pedido, hora_pedido, estado, metodo_pago, total)
            VALUES (%s, %s, %s, %s, 'Pendiente', %s, %s)
        """, (nombre_cliente, producto, fecha_actual, hora_actual, metodo_pago, total))
        
        conexion.commit()
        conexion.close()
        
        return jsonify({"mensaje": "Pedido recibido en la cocina del IGJ"}), 201
    except Exception as e:
        # FIX: Imprimir el error REAL en la consola del servidor para diagnosticar.
        print(f"[ERROR /api/nuevo_pedido] {type(e).__name__}: {e}")
        # FIX: Hacer rollback si la conexion fue abierta, para no dejar la transaccion corrupta.
        if conexion:
            conexion.rollback()
            conexion.close()
        # FIX: Retornar el error real al cliente (AppJava) en lugar de un exito falso.
        return jsonify({"error": f"{type(e).__name__}: {str(e)}"}), 500