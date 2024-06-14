from flask import Flask, render_template, request, redirect, url_for, flash
from mysql_db import MySQL
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from models import User, Role
from role_rule import roles_required
import bleach
from image_data import get_md5_hash, get_mime_type

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
    books = [
        {
            'title': 'Book Title 1',
            'genres': ['Genre1', 'Genre2'],
            'year': 2021,
            'average_rating': 4.5,
            'review_count': 10
        },
        {
            'title': 'Book Title 2',
            'genres': ['Genre3'],
            'year': 2020,
            'average_rating': 3.8,
            'review_count': 5
        },
        {
            'title': 'Book Title 1',
            'genres': ['Genre1', 'Genre2'],
            'year': 2021,
            'average_rating': 4.5,
            'review_count': 10
        },
        {
            'title': 'Book Title 2',
            'genres': ['Genre3'],
            'year': 2020,
            'average_rating': 3.8,
            'review_count': 5
        },
        {
            'title': 'Book Title 1',
            'genres': ['Genre1', 'Genre2'],
            'year': 2021,
            'average_rating': 4.5,
            'review_count': 10
        },
        {
            'title': 'Book Title 2',
            'genres': ['Genre3'],
            'year': 2020,
            'average_rating': 3.8,
            'review_count': 5
        },
        {
            'title': 'Book Title 1',
            'genres': ['Genre1', 'Genre2'],
            'year': 2021,
            'average_rating': 4.5,
            'review_count': 10
        },
        {
            'title': 'Book Title 2',
            'genres': ['Genre3'],
            'year': 2020,
            'average_rating': 3.8,
            'review_count': 5
        },
        {
            'title': 'Book Title 1',
            'genres': ['Genre1', 'Genre2'],
            'year': 2021,
            'average_rating': 4.5,
            'review_count': 10
        },
        {
            'title': 'Book Title 2',
            'genres': ['Genre3'],
            'year': 2020,
            'average_rating': 3.8,
            'review_count': 5
        }
    ]
    return render_template("index.html", books=books)


@app.route('/login')
def login():
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


@app.route('/book/create', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def add_book():
    genres = ['Детектив', 'Хоррор', 'Фантастика']
    print(request.method)
    if request.method == 'POST':
        title = request.form['title']
        short_description = bleach.clean(request.form['short_description'])
        year_publish = request.form['year']
        publisher = request.form['publisher']
        author = request.form['author']
        size_book = request.form['size_book']
        genres_selected = request.form.getlist('genres')
        cover = request.files['cover']
        print(title)

        if not cover:
            # error
            ...

        mime_type = get_mime_type(cover)
        md5_hash = get_md5_hash(cover)

        if not mime_type.startswith('image'):
            # error
            ...

        cursor = db.connection().cursor(named_tuple=True)

        try:
            cursor.execute("START TRANSACTION")
            query = 'SELECT id FROM covers WHERE md5_hash = %s'
            cursor.execute(query, (md5_hash,))
            cover_row = cursor.fetchone()

            if cover_row:
                cover_id = cover_row[0]
            else:
                cover_filename = cover.filename
                query = 'INSERT INTO covers (file_path, mime_type, md5_hash) VALUES (%s, %s, %s)'
                cursor.execute(query, (cover_filename, mime_type, md5_hash))
                cover_id = cursor.lastrowid

            query = 'INSERT INTO description_book (title, short_description, year_publish, publisher, author, size_book, cover_id) VALUES (%s, %s, %s, %s, %s, %s, %s)'
            cursor.execute(query, (title, short_description, year_publish, publisher, author, size_book, cover_id))
            book_id = cursor.lastrowid

            for genre_name in genres_selected:
                query = 'SELECT id FROM genres WHERE name = %s'
                cursor.execute(query, (genre_name,))

                genre_id = cursor.fetchone()[0]

                query = 'INSERT INTO book_genre (book_id, genre_id) VALUES (%s, %s)'
                cursor.execute(query, (book_id, genre_id))

            db.connection().commit()

            end_name = mime_type.split('/')[1]

            cover.save(f'{app.config["UPLOAD_FOLDER"]}/{cover_id}.{end_name}')
            flash("УРАААА", 'success')

        except Exception as e:
            db.connection().rollback()
            flash(f'Ошибка при добавлении книги: {str(e)}', 'danger')

    return render_template('createbook.html', genres=genres)


@app.route('/book/edit/<int:book_id>')
@login_required
@roles_required('admin', 'moderator')
def edit_book(book_id):
    ...
