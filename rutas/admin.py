from flask import Blueprint, render_template, request, redirect, session, jsonify
from db_manager import conectar_db
import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin123": 
            session["logueado"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="Contraseña incorrecta")
    return render_template("login.html")

@admin_bp.route("/logout")
def logout():
    session.pop("logueado", None)
    return redirect("/")

@admin_bp.route("/admin")
def admin():
    if not session.get("logueado"):
        return redirect("/login")

    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_producto, nombre, precio, categoria, disponible FROM Productos")
    productos = cursor.fetchall()
    conexion.close()
    return render_template("admin.html", productos=productos)

@admin_bp.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    if not session.get("logueado"):
        return redirect("/login")

    nombre = request.form["nombre"]
    precio = request.form["precio"]
    categoria = request.form["categoria"]
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO Productos (nombre, precio, categoria, disponible) 
        VALUES (?, ?, ?, 1)
    """, (nombre, precio, categoria))
    conexion.commit()
    conexion.close()
    return redirect("/admin")

@admin_bp.route("/estado_producto/<int:id>", methods=["POST"])
def estado_producto(id):
    if not session.get("logueado"):
        return redirect("/login")
    
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("SELECT disponible FROM Productos WHERE id_producto = ?", (id,))
    estado_actual = cursor.fetchone()[0]
    
    nuevo_estado = 0 if estado_actual == 1 else 1
    
    cursor.execute("UPDATE Productos SET disponible = ? WHERE id_producto = ?", (nuevo_estado, id))
    conexion.commit()
    conexion.close()
    return redirect("/admin")

@admin_bp.route("/eliminar_producto/<int:id>", methods=["POST"])
def eliminar_producto(id):
    if not session.get("logueado"):
        return redirect("/login")
        
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM Productos WHERE id_producto = ?", (id,))
    conexion.commit()
    conexion.close()
    return redirect("/admin")

@admin_bp.route("/ventas")
def ventas():
    if not session.get("logueado"):
        return redirect("/login")

    conexion = conectar_db()
    cursor = conexion.cursor()
    fecha_hoy = datetime.date.today()

    cursor.execute("""
        SELECT metodo_pago, SUM(total) 
        FROM Pedidos 
        WHERE fecha_pedido = ? 
        GROUP BY metodo_pago
    """, (fecha_hoy,))
    
    resultados = cursor.fetchall()
    conexion.close()

    total_efectivo = 0.0
    total_tarjeta = 0.0

    for fila in resultados:
        if fila[0] == 'efectivo':
            total_efectivo = fila[1] if fila[1] else 0.0
        elif fila[0] == 'tarjeta':
            total_tarjeta = fila[1] if fila[1] else 0.0

    total_dia = total_efectivo + total_tarjeta

    return render_template("ventas.html", 
                           fecha=fecha_hoy, 
                           total_efectivo=total_efectivo, 
                           total_tarjeta=total_tarjeta, 
                           total_dia=total_dia)
@admin_bp.route("/api/ventas")
def api_ventas():
    # Candado de seguridad para que nadie vea las ventas si no está logueado
    if not session.get("logueado"):
        return jsonify({"error": "No autorizado"}), 403

    conexion = conectar_db()
    cursor = conexion.cursor()
    fecha_hoy = datetime.date.today()

    # Calculamos los totales
    cursor.execute("""
        SELECT metodo_pago, SUM(total) 
        FROM Pedidos 
        WHERE fecha_pedido = ? 
        GROUP BY metodo_pago
    """, (fecha_hoy,))
    
    resultados = cursor.fetchall()
    conexion.close()

    total_efectivo = 0.0
    total_tarjeta = 0.0

    for fila in resultados:
        if fila[0] == 'efectivo':
            total_efectivo = fila[1] if fila[1] else 0.0
        elif fila[0] == 'tarjeta':
            total_tarjeta = fila[1] if fila[1] else 0.0

    # Enviamos los datos listos para que JavaScript los consuma
    return jsonify({
        "efectivo": total_efectivo,
        "tarjeta": total_tarjeta,
        "total_dia": total_efectivo + total_tarjeta
    })