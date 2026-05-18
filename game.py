from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from typing import List, Dict, Any
from flask_login import login_required
from utils.decorators import admin_required
from entidades.level import Level
from utils.crypto_utils import cifrar_palabra, descifrar_palabra

# Criptografía
def descifrar_palabra_real(palabra_cifrada: str) -> str:
    """Descifra la palabra secreta del nivel usando Fernet AES."""
    try:
        return descifrar_palabra(palabra_cifrada).lower()
    except Exception as e:
        print(f"Error al descifrar: {e}")
        return palabra_cifrada.lower()

# Panel de Administración
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

@admin_bp.route('/', methods=['GET'])
@admin_required
def panel_admin() -> str:
    """Muestra la lista de niveles del panel de administración."""
    niveles: List[Dict[str, Any]] = Level.get_all()
    return render_template('admin_panel.html', niveles=niveles)

@admin_bp.route('/agregar_nivel', methods=['GET', 'POST'])
@admin_required
def agregar_nivel() -> str:
    """Procesa el formulario para agregar un nuevo nivel."""
    if request.method == 'POST':
        image: str = request.form.get('image', '').strip()
        hint: str = request.form.get('hint', '').strip()
        secret_word: str = request.form.get('secret_word', '').strip().lower()
        level_number: int = int(request.form.get('level_number', 0))

        # El guardado en la base de datos cifra la palabra internamente
        exito: bool = Level.save(image, hint, secret_word, level_number)

        if exito:
            flash(f"Nivel {level_number} guardado correctamente.", "success")
        else:
            flash("Error al guardar el nivel. Verifica que el número de nivel no se repita.", "warning")

        return redirect(url_for('admin_bp.panel_admin'))

    return render_template('admin_agregar.html')

# Motor de Gameplay
game_bp = Blueprint('game_bp', __name__, url_prefix='/juego')

@game_bp.route('/iniciar', methods=['GET'])
@login_required
def iniciar_juego() -> str:
    """Inicializa la partida del jugador desde el nivel 1 y con 3 vidas."""
    session['nivel_actual'] = 1
    session['vidas'] = 3
    return redirect(url_for('game_bp.mostrar_juego'))

@game_bp.route('/', methods=['GET'])
@login_required
def mostrar_juego() -> str:
    """Renderiza el nivel actual del jugador o la pantalla de victoria."""
    nivel_actual: int = session.get('nivel_actual', 1)
    vidas: int = session.get('vidas', 3)

    niveles: List[Dict[str, Any]] = Level.get_all()
    nivel_data = next((n for n in niveles if n['level_number'] == nivel_actual), None)

    if not nivel_data:
        session.clear()
        return render_template('victoria.html')

    return render_template(
        'juego.html',
        nivel=nivel_data['level_number'],
        imagen=nivel_data['image'],
        pista=nivel_data['hint'],
        vidas=vidas
    )

@game_bp.route('/procesar', methods=['POST'])
@login_required
def procesar_juego() -> str:
    """Valida la palabra ingresada por el jugador y gestiona el progreso o pérdida de vidas."""
    palabra_usuario: str = request.form.get('palabra_usuario', '').strip().lower()
    nivel_actual: int = session.get('nivel_actual', 1)

    niveles: List[Dict[str, Any]] = Level.get_all()
    nivel_data = next((n for n in niveles if n['level_number'] == nivel_actual), None)

    if not nivel_data:
        return redirect(url_for('game_bp.iniciar_juego'))

    palabra_secreta: str = descifrar_palabra_real(nivel_data['secret_word']).lower()

    if palabra_usuario == palabra_secreta:
        session['nivel_actual'] += 1
        flash("¡Correcto! Avanzas al siguiente nivel.", "success")
        return redirect(url_for('game_bp.mostrar_juego'))
    else:
        session['vidas'] -= 1
        vidas_restantes: int = session['vidas']

        if vidas_restantes <= 0:
            session.clear()
            return render_template('game_over.html')
        else:
            flash(f"Incorrecto. Te quedan {vidas_restantes} vidas.", "warning")
            return redirect(url_for('game_bp.mostrar_juego'))
