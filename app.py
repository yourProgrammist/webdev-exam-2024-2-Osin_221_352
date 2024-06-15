import os

from flask import Flask, render_template, request, redirect, url_for, flash, make_response
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


def load_books(cur_page, per_page):
    offset = (cur_page - 1) * per_page

    cursor = db.connection().cursor(dictionary=True)
    query = 'SELECT COUNT(*) FROM description_book'
    cursor.execute(query)
    count_pages = (cursor.fetchone()['COUNT(*)'] + per_page - 1) // per_page

    query = """
            WITH book_genres AS (
                SELECT bg.book_id, GROUP_CONCAT(g.name SEPARATOR ', ') as genres
                FROM book_genre bg
                JOIN genres g ON bg.genre_id = g.id
                GROUP BY bg.book_id
            ),
            book_reviews AS (
                SELECT r.book_id, ROUND(AVG(r.mark), 1) as average_mark, COUNT(r.id) as review_count
                FROM reviews r
                GROUP BY r.book_id
            )
            SELECT b.id, b.title, b.year_publish, bg.genres, br.average_mark, br.review_count
            FROM description_book b
            LEFT JOIN book_genres bg ON b.id = bg.book_id
            LEFT JOIN book_reviews br ON b.id = br.book_id
            ORDER BY b.year_publish DESC
            LIMIT %s OFFSET %s;
       """
    cursor.execute(query, (per_page, offset))
    books = cursor.fetchall()

    return books, count_pages


def load_book(book_id):
    cursor = db.connection().cursor(dictionary=True)

    query = """
                SELECT
                    db.id,
                    db.title,
                    db.author,
                    db.publisher,
                    db.year_publish AS year,
                    db.size_book,
                    GROUP_CONCAT(g.name SEPARATOR ', ') AS genres,
                    db.short_description
                FROM
                    description_book db
                LEFT JOIN
                    book_genre bg ON db.id = bg.book_id
                LEFT JOIN
                    genres g ON bg.genre_id = g.id
                WHERE
                    db.id = %s
                GROUP BY
                    db.id
        """

    cursor.execute(query, (book_id,))
    book = cursor.fetchone()
    book['genres'] = book['genres'].split(', ')

    return book


def load_genres():
    cursor = db.connection().cursor(named_tuple=True)
    query = 'SELECT name FROM genres'
    cursor.execute(query)
    genres = cursor.fetchall()
    genres = [genre.name for genre in genres]
    return genres


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    books, count_pages = load_books(page, app.config["POSTS_PER_PAGE"])
    return render_template("index.html", books=books, page=page, count_pages=count_pages)


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
    genres = load_genres()

    if request.method == 'POST':
        title = request.form['title']
        short_description = bleach.clean(request.form['short_description'])
        year_publish = request.form['year']
        publisher = request.form['publisher']
        author = request.form['author']
        size_book = request.form['size_book']
        genres_selected = request.form.getlist('genres')
        cover = request.files['cover']

        if not cover:
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return redirect(request.url)

        mime_type = get_mime_type(cover)
        md5_hash = get_md5_hash(cover)

        if not mime_type.startswith('image'):
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            return redirect(request.url)

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

            ######### ПЕРЕХОД НА ПРОСМОТР

        except Exception as e:
            db.connection().rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            print(f'Ошибка при добавлении книги: {str(e)}')
            return redirect(request.url)

    return render_template('createbook.html', genres=genres)


@app.route('/book/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'moderator')
def edit_book(book_id):
    genres = load_genres()

    book = load_book(book_id)

    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        publisher = request.form['publisher']
        year_publish = request.form['year']
        size_book = request.form['size_book']
        short_description = bleach.clean(request.form['short_description'])

        genres_selected = request.form.getlist('genres')

        cursor = db.connection().cursor(named_tuple=True)

        try:
            cursor.execute("START TRANSACTION")

            query = '''UPDATE description_book 
                                   SET title = %s, short_description = %s, year_publish = %s, publisher = %s, author = %s, size_book = %s 
                                   WHERE id = %s'''
            cursor.execute(query, (title, short_description, year_publish, publisher, author, size_book, book_id))

            query = 'DELETE FROM book_genre WHERE book_id = %s'
            cursor.execute(query, (book_id,))

            for genre_name in genres_selected:
                query = 'SELECT id FROM genres WHERE name = %s'
                cursor.execute(query, (genre_name,))
                genre_id = cursor.fetchone()[0]

                query = 'INSERT INTO book_genre (book_id, genre_id) VALUES (%s, %s)'
                cursor.execute(query, (book_id, genre_id))

            db.connection().commit()

            ######### ПЕРЕХОД НА ПРОСМОТР

        except Exception as e:
            db.connection().rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
            print(f'Ошибка при редактировании книги: {str(e)}')
            return redirect(request.url)

    return render_template('editbook.html', book=book, genres=genres)


@app.route('/book/delete/<int:book_id>', methods=['POST'])
@login_required
@roles_required('admin')
def delete_book(book_id):
    cursor = db.connection().cursor(named_tuple=True)

    try:
        cursor.execute("START TRANSACTION")
        query = 'SELECT cover_id FROM description_book WHERE id = %s'
        cursor.execute(query, (book_id,))
        file_name = cursor.fetchone()[0]

        query = 'SELECT mime_type FROM covers WHERE id = %s'
        cursor.execute(query, (file_name,))
        file_mime = cursor.fetchone()[0].split('/')[1]

        file_path = f'{app.config["UPLOAD_FOLDER"]}/{file_name}.{file_mime}'

        query = 'DELETE FROM covers WHERE id = %s'
        cursor.execute(query, (book_id,))

        query = 'DELETE FROM description_book WHERE id = %s'
        cursor.execute(query, (book_id,))
        db.connection().commit()

        os.remove(file_path)

        flash('Книга успешно удалена!', 'success')
    except Exception as e:
        db.connection().rollback()
        flash('Ошибка. Книга не удалена!', 'danger')
        print('Ошибка в удалении книги: ' + str(e))

    return redirect(url_for('index'))
