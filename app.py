from flask import Flask, render_template, request, jsonify
from flask_login import LoginManager, login_user, logout_user
from entidades.user import User
from enums.role import Role

app = Flask(__name__)

#rutas de navegacion frontend
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/loginJugador')
def login_Gamer():
    return render_template('loginJugador.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')
@app.route('/loginAdmin')

def login_Admin():
    return render_template('loginAdmin.html')

#ruta para el registro de usuarios


app.secret_key = "super_secret_key"


login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)


@app.route('/api/user', methods=['POST'])
def create_user():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    if User.check_email_exists(email):
        return jsonify({
            "success": False,
            "message": "Email already exists"
        }), 409

    success = User.save(
        name,
        email,
        password,
        Role.PLAYER.value
    )

    if success:
        return jsonify({"success": True}), 201

    return jsonify({"success": False}), 500


@app.route('/api/login', methods=['POST'])
def loginJugador():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.check_login(email, password)

    if user:
        login_user(user)

        return jsonify({
            "success": True,
            "role": user.role
        }), 200

    return jsonify({
        "success": False,
        "message": "Invalid credentials"
    }), 401


if __name__ == '__main__':
    app.run(debug=True)