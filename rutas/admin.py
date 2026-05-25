from flask import Blueprint, render_template, request, redirect, session, jsonify
from postgres_manager import conectar_postgres
import datetime

admin_bp = Blueprint('admin', __name__)





@admin_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == "admin123":
            session["logueado"] = True
            return redirect("/admin")
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
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_producto, nombre, precio, categoria, disponible FROM Productos")
        productos = cursor.fetchall()
        conexion.close()
        return render_template("admin.html", productos=productos)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/agregar_producto", methods=["POST"])
def agregar_producto():
    if not session.get("logueado"):
        return redirect("/login")
    try:
        nombre = request.form["nombre"]
        precio = float(request.form["precio"])
        categoria = request.form["categoria"]
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO Productos (nombre, precio, categoria, disponible)
            VALUES (%s, %s, %s, True)
        """, (nombre, precio, categoria))
        conexion.commit()
        conexion.close()
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500
    return redirect("/admin")


@admin_bp.route("/estado_producto/<int:id>", methods=["POST"])
def estado_producto(id):
    if not session.get("logueado"):
        return redirect("/login")
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("SELECT disponible FROM Productos WHERE id_producto = %s", (id,))
        estado_actual = cursor.fetchone()[0]
        cursor.execute(
            "UPDATE Productos SET disponible = %s WHERE id_producto = %s",
            (not estado_actual, id)
        )
        conexion.commit()
        conexion.close()
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500
    return redirect("/admin")


@admin_bp.route("/eliminar_producto/<int:id>", methods=["POST"])
def eliminar_producto(id):
    if not session.get("logueado"):
        return redirect("/login")
    try:
        conexion = conectar_postgres()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM Productos WHERE id_producto = %s", (id,))
        conexion.commit()
        conexion.close()
    except Exception as e:
        if 'conexion' in locals():
            conexion.rollback()
            conexion.close()
        return jsonify({"error": str(e)}), 500
    return redirect("/admin")

