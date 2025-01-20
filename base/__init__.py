from flask import Flask, render_template
from base.controllers import usuarios
from base.controllers import vista
from datetime import datetime

# Definir el filtro
def format_date(value, format='%Y-%m-%d'):
    if isinstance(value, str):
        value = datetime.strptime(value, '%Y-%m-%d')
    return value.strftime(format)

def create_app():
    app = Flask(__name__)


    app.config.from_mapping(
        SECRET_KEY='dev',
        DEBUG=True,
    )

    app.register_blueprint(usuarios.bp)

    app.register_blueprint(vista.bp)

    # Registrar el filtro
    # Registrar el filtro en la aplicación
    app.add_template_filter(format_date, 'format_date')

    @app.route('/')
    def index():
        return render_template('auth.html')
    


    return app
