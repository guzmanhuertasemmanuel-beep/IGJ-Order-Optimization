from flask import Flask
from db_manager import crear_tablas

# Importamos los módulos (Blueprints)
from rutas.cliente import cliente_bp
from rutas.cocina import cocina_bp
from rutas.admin import admin_bp

app = Flask(__name__)
app.secret_key = "super_secreta_igj_2026"

# Registramos las rutas en la aplicación principal
# Agregamos el prefijo /api para que actúe como paraguas de las rutas móviles
app.register_blueprint(cliente_bp)
app.register_blueprint(cocina_bp)
app.register_blueprint(admin_bp)

# Aseguramos que las tablas existan al iniciar
crear_tablas()

if __name__ == "__main__":
    app.run(debug=True)