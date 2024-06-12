from flask import Flask, render_template, request, redirect, url_for, flash
from mysql_db import MySQL
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from models import User, Role
from role_rule import roles_required

app = Flask(__name__)

app.config.from_pyfile('config.py')

login_manager = LoginManager()
login_manager.init_app(app)

db = MySQL(app)


@app.context_processor
def inject_user():
    return dict(current_user=current_user)


@app.context_processor
def inject_roles():
    def is_admin():
        return current_user.is_authenticated and current_user.role == 'admin'

    def is_moderator():
        return current_user.is_authenticated and current_user.role == 'moderator'

    def is_user():
        return current_user.is_authenticated and current_user.role == 'user'

    return dict(is_admin=is_admin, is_moderator=is_moderator, is_user=is_user)


@login_manager.user_loader
def load_user(user_id):
    cursor = db.connection().cursor(named_tuple=True)
    query = 'SELECT * FROM users WHERE users.id = %s'
    cursor.execute(query, (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if not user:
        return None
    return User(user.id, user.login, user.password_hash, user.surname, user.name, user.patronymic, user.role_id,
                load_role(user.role_id))


def load_role(role_id):
    cursor = db.connection().cursor(named_tuple=True)
    query = 'SELECT * FROM roles WHERE roles.id = %s'
    cursor.execute(query, (role_id,))
    role = cursor.fetchone()
    cursor.close()
    if not role:
        return None
    return Role(role.id, role.role, role.description)


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/tmp')
def tmp():
    print(current_user.role)
    return render_template("login.html")

@app.route('/login/auth', methods=['POST'])
def authentication():
    login = request.form["login"]
    password = request.form["password"]

    remember = request.form.get("remember_user") == "on"

    cursor = db.connection().cursor(named_tuple=True)

    query = 'SELECT * FROM users WHERE users.login = %s and users.password_hash = SHA2(%s, 256)'
    cursor.execute(query, (login, password))
    user = cursor.fetchone()

    cursor.close()

    if not user:
        flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
        return render_template('login.html')

    login_user(User(user.id, user.login), remember)
    next_page = request.args.get("next")
    return redirect(next_page) if next_page else redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
