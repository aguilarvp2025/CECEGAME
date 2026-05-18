from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from entidades.user import User
from enums.role import Role
from functools import wraps

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_Gamer"

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Decorador de control de accesos (RBAC) para Valeria
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Debes iniciar sesión primero.", "warning")
            return redirect(url_for('login_Gamer'))
        if getattr(current_user, 'role', '') != 'ADMINISTRADOR':
            flash("Acceso denegado: Se requieren permisos de Administrador.", "danger")
            return redirect(url_for('game_bp.iniciar_juego'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas de navegación frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginJugador', methods=['GET', 'POST'])
def login_Gamer():
    if request.method == 'POST':
        email = request.form.get('alias', '').strip()  # En el HTML se llama 'alias' pero se usa el correo para check_login
        password = request.form.get('password', '').strip()
        
        user = User.check_login(email, password)
        if user:
            login_user(user)
            if user.role == 'ADMINISTRADOR':
                return redirect(url_for('admin_bp.panel_admin'))
            return redirect(url_for('game_bp.iniciar_juego'))
        else:
            flash("Correo o contraseña incorrectos.", "warning")
    return render_template('loginJugador.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        alias = request.form.get('alias', '').strip()
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '').strip()
        
        if User.check_email_exists(correo):
            flash("El correo electrónico ya está registrado.", "warning")
        else:
            # Registramos al nuevo usuario como PLAYER
            exito = User.save(alias, correo, password, Role.PLAYER.value)
            if exito:
                flash("¡Cuenta creada con éxito! Inicia sesión.", "success")
                return redirect(url_for('login_Gamer'))
            else:
                flash("Ocurrió un error al registrar tu cuenta. Intenta de nuevo.", "danger")
                
    return render_template('signup.html')

@app.route('/loginAdmin')
def login_Admin():
    return render_template('loginAdmin.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# --- INTEGRACIÓN DE BLUEPRINTS DEL JUEGO (Izumy) ---
from game import game_bp, admin_bp
app.register_blueprint(game_bp)
app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)