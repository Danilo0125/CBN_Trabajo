from flask import Blueprint, render_template

# Crear blueprint
web_blueprint = Blueprint('web', __name__)

@web_blueprint.route('/')
def index():
    """Ruta principal que muestra el dashboard"""
    return render_template('index.html')

@web_blueprint.route('/IA/dashboard')
def dashboard():
    """Ruta principal que muestra el dashboard"""
    return render_template('dashboard.html')

