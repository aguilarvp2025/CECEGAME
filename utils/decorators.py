from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

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
