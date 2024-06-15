import os
import markdown2
from flask import Flask, render_template, request, redirect, url_for, flash
from mysql_db import MySQL
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from models import User, Role
from role_rule import roles_required
import bleach
from image_data import get_md5_hash, get_mime_type

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = MySQL(app)


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


def init_login_manager():
    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)


init_login_manager()


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


@app.context_processor
def inject_review():
    def check_review(book_id):
        if not current_user.is_authenticated:
            return False

        cursor = db.connection().cursor(named_tuple=True)
        query = 'SELECT id FROM reviews WHERE book_id = %s AND user_id = %s'
        cursor.execute(query, (book_id, current_user.id))
        review = cursor.fetchone()
        if review:
            return review[0]
        return False

    def check_review_status(book_id):
        review_id = check_review(book_id)
        cursor = db.connection().cursor(named_tuple=True)
        query = '''
            SELECT
                rs.status
            FROM
                reviews r
            JOIN
                review_status rs ON r.status_id = rs.id
            WHERE
                r.id = %s;
        '''

        cursor.execute(query, (review_id,))
        review_status = cursor.fetchone()
        if review_status:
            return review_status[0]

        return False

    return dict(check_review=check_review, check_review_status=check_review_status)


def check_review_def(book_id):
    cursor = db.connection().cursor(named_tuple=True)
    query = 'SELECT id FROM reviews WHERE book_id = %s AND user_id = %s'
    cursor.execute(query, (book_id, current_user.id))
    review = cursor.fetchone()
    if review:
        return review[0]
    return False


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
    cursor = db.connection().cursor(dictionary=True)
    query = 'SELECT COUNT(*) FROM description_book'
    cursor.execute(query)
    count_pages = (cursor.fetchone()['COUNT(*)'] + per_page - 1) // per_page

    if cur_page > count_pages != 0:
        cur_page = count_pages
    elif cur_page < 1:
        cur_page = 1

    offset = (cur_page - 1) * per_page

    query = '''
            SELECT 
                b.id, 
                b.title, 
                b.year_publish, 
                bg.genres, 
                br.average_mark, 
                br.review_count, 
                b.cover_id, 
                c.mime_type
            FROM 
                description_book b
            LEFT JOIN (
                SELECT 
                    bg.book_id, 
                    GROUP_CONCAT(g.name SEPARATOR ', ') AS genres
                FROM 
                    book_genre bg
                JOIN 
                    genres g ON bg.genre_id = g.id
                GROUP BY 
                    bg.book_id
            ) bg ON b.id = bg.book_id
            LEFT JOIN (
                SELECT 
                    r.book_id, 
                    ROUND(AVG(r.mark), 1) AS average_mark, 
                    COUNT(r.id) AS review_count
                FROM 
                    reviews r
                WHERE 
                    r.status_id = 2
                GROUP BY 
                    r.book_id
            ) br ON b.id = br.book_id
            LEFT JOIN 
                covers c ON b.cover_id = c.id
            ORDER BY 
                b.year_publish DESC
            LIMIT %s OFFSET %s;
       '''
    cursor.execute(query, (per_page, offset))
    books = cursor.fetchall()

    for book in books:
        mime_type = book['mime_type'].split('/')[1]
        file_name = book['cover_id']
        book['cover'] = f'{app.config["UPLOAD_FOLDER"]}/{file_name}.{mime_type}'

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
                    db.short_description,
                    db.cover_id,
                    c.mime_type
                FROM
                    description_book db
                LEFT JOIN
                    book_genre bg ON db.id = bg.book_id
                LEFT JOIN
                    genres g ON bg.genre_id = g.id
                LEFT JOIN
                    covers c ON db.cover_id = c.id
                WHERE
                    db.id = %s
                GROUP BY
                    db.id, c.mime_type
        """

    try:
        cursor.execute(query, (book_id,))
        book = cursor.fetchone()

        if book:
            if book['mime_type']:
                book['mime_type'] = book['mime_type'].split('/')
                cover_id = book['cover_id']
                mime_type = book['mime_type'][1] if len(book['mime_type']) > 1 else ''
                folder = app.config["UPLOAD_FOLDER"].split('/')[1]
                book['cover'] = f'{folder}/{cover_id}.{mime_type}' if cover_id and mime_type else None
            else:
                book['cover'] = None

            if not book['genres']:
                book['genres'] = ''

            return book
        else:
            return None

    except Exception as e:
        print(f"Ошибка при загрузке(РЕДАКТИРОВАНИЕ) книги: {e}")
        return None


def load_reviews(book_id, status_id):
    cursor = db.connection().cursor(dictionary=True)
    query = '''
        SELECT
            users.login,
            reviews.id,
            reviews.user_id,
            reviews.mark,
            reviews.body_text
        FROM
            reviews
        JOIN
            users ON reviews.user_id = users.id
        WHERE
            reviews.book_id = %s AND reviews.status_id = %s
        '''
    cursor.execute(query, (book_id, status_id))
    reviews = cursor.fetchall()
    current_user_review = None

    for review in reviews:
        review['body_text'] = markdown2.markdown(review['body_text'])
        if current_user.is_authenticated and review['user_id'] == current_user.id:
            current_user_review = review

    if current_user_review is not None:
        reviews.append(current_user_review)

    return reviews


def load_genres():
    cursor = db.connection().cursor(named_tuple=True)
    query = 'SELECT name FROM genres'
    cursor.execute(query)
    genres = cursor.fetchall()
    genres = [genre.name for genre in genres]
    return genres


def load_moderation_reviews(cur_page, per_page):

    cursor = db.connection().cursor(dictionary=True)
    query = 'SELECT COUNT(*) FROM reviews WHERE status_id = 1'
    cursor.execute(query)
    count_pages = (cursor.fetchone()['COUNT(*)'] + per_page - 1) // per_page

    if cur_page > count_pages != 0:
        cur_page = count_pages
    elif cur_page < 1:
        cur_page = 1

    offset = (cur_page - 1) * per_page

    query = """
                SELECT
                    b.title,
                    u.name,
                    r.add_date,
                    r.id
                FROM
                    reviews r
                JOIN
                    description_book b ON r.book_id = b.id
                JOIN
                    users u ON r.user_id = u.id
                WHERE r.status_id = 1
                ORDER BY
                    r.add_date DESC
                LIMIT %s OFFSET %s;
           """

    cursor.execute(query, (per_page, offset))
    reviews = cursor.fetchall()

    return reviews, count_pages


def load_review(review_id):
    cursor = db.connection().cursor(dictionary=True)
    query = '''
            SELECT
                u.login,
                r.id,
                r.mark,
                r.body_text,
                r.status_id
            FROM
                reviews r
            JOIN
                users u ON r.user_id = u.id
            WHERE
                r.id = %s;
    '''
    cursor.execute(query, (review_id,))
    review = cursor.fetchone()
    review['body_text'] = markdown2.markdown(review['body_text'])
    return review


def load_user_reviews(cur_page, per_page):
    cursor = db.connection().cursor(dictionary=True)
    query = '''
        SELECT COUNT(*)
        FROM reviews
        WHERE user_id = %s;
    '''
    cursor.execute(query, (current_user.id,))
    count_pages = (cursor.fetchone()['COUNT(*)'] + per_page - 1) // per_page

    if cur_page > count_pages != 0:
        cur_page = count_pages
    elif cur_page < 1:
        cur_page = 1

    offset = (cur_page - 1) * per_page

    query = '''
            SELECT
            b.title,
            r.mark,
            r.body_text,
            rs.status
        FROM
            reviews r
        JOIN
            description_book b ON r.book_id = b.id
        JOIN
            review_status rs ON r.status_id = rs.id
        WHERE
            r.user_id = %s
        LIMIT %s OFFSET %s;
     '''
    cursor.execute(query, (current_user.id, per_page, offset))
    reviews = cursor.fetchall()
    for review in reviews:
        review['body_text'] = markdown2.markdown(review['body_text'])

    return reviews, count_pages


@app.route('/')
@app.route('/index')
@app.route('/index/<int:page>')
def index(page=1):
    books, count_pages = load_books(page, app.config["POSTS_PER_PAGE"])
    return render_template("index.html", books=books, page=page, count_pages=count_pages)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

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

            query = '''
                INSERT INTO
                description_book
                (
                    title,
                    short_description,
                    year_publish,
                    publisher,
                    author,
                    size_book,
                    cover_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            '''
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

            return redirect(url_for('view_book', book_id=book_id))

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

            query = '''
                UPDATE description_book
                SET
                    title = %s,
                    short_description = %s,
                    year_publish = %s,
                    publisher = %s,
                    author = %s,
                    size_book = %s
                WHERE id = %s
            '''
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

            return redirect(url_for('view_book', book_id=book_id))

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

        query = '''
            SELECT COUNT(*) AS count_use_cover
            FROM description_book
            WHERE cover_id = %s;
        '''

        cursor.execute(query, (file_name,))
        count_use_cover = cursor.fetchone().count_use_cover

        if count_use_cover == 1:
            query = 'DELETE FROM covers WHERE id = %s'
            cursor.execute(query, (file_name,))
            try:
                os.remove(file_path)
            except Exception as e:
                print(f'Ошибка при удаление файла в системе: {e}')

        query = 'DELETE FROM description_book WHERE id = %s'
        cursor.execute(query, (book_id,))
        db.connection().commit()

        flash('Книга успешно удалена!', 'success')
    except Exception as e:
        db.connection().rollback()
        flash('Ошибка. Книга не удалена!', 'danger')
        print('Ошибка в удалении книги: ' + str(e))

    return redirect(url_for('index'))


@app.route('/book/view/<int:book_id>')
def view_book(book_id):
    book = load_book(book_id)
    book['short_description'] = markdown2.markdown(book['short_description'])

    reviews = load_reviews(book_id, 2)

    return render_template('viewbook.html', book=book, reviews=reviews)


@app.route('/book/view/<int:book_id>/review/add', methods=['GET', 'POST'])
@login_required
def add_review(book_id):
    if check_review_def(book_id):
        flash("Вы уже написали рецензию!!!", "danger")
        return redirect(url_for('index'))

    book = load_book(book_id)

    if request.method == 'POST':
        mark = request.form['mark']
        body_text = bleach.clean(request.form['body_text'])
        try:
            cursor = db.connection().cursor(named_tuple=True)
            query = 'INSERT INTO reviews (book_id, user_id, mark, body_text, status_id) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(query, (book_id, current_user.id, mark, body_text, 1))

            db.connection().commit()

            flash('Сохранение выполнено успешно!', 'success')

            return redirect(url_for('view_book', book_id=book_id))
        except Exception as e:
            print(f'Ошибка при сохранении рецензии {e}')
            flash('Произошла ошибка при сохранение. Проверьте данные', 'danger')
            return redirect(request.url)

    return render_template('createreview.html', book_id=book_id, book=book)


@app.route('/view/reviews')
@app.route('/view/reviews/<int:page>')
@login_required
@roles_required('admin', 'moderator')
def view_reviews(page=1):
    reviews, count_pages = load_moderation_reviews(page, app.config["POSTS_PER_PAGE"])
    return render_template("viewreviewmoder.html", reviews=reviews, page=page, count_pages=count_pages)


@app.route('/view/reviews/change-status/<int:review_id>', methods=['GET', 'POST'])
@login_required
@roles_required('admin', 'moderator')
def change_status_review(review_id):
    review = load_review(review_id)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'approve':
            review['status_id'] = 2
        elif action == 'reject':
            review['status_id'] = 3

        cursor = db.connection().cursor(named_tuple=True)
        try:
            query = 'UPDATE reviews SET status_id = %s WHERE id = %s'
            cursor.execute(query, (review['status_id'], review_id))

            db.connection().commit()

            flash('Статус рецензии успешно обновлен!', 'success')

            return redirect(url_for('view_reviews'))
        except Exception as e:
            print(f'Ошибка при изменении статуса рецензии: {e}')
            flash('Ошибка при изменении статуса рецензии!', 'danger')
            return redirect(request.url)

    return render_template("reviewchangestatus.html", review=review)


@app.route('/view/my-reviews')
@app.route('/view/my-reviews/<int:page>')
@login_required
def get_my_reviews(page=1):
    reviews, count_pages = load_user_reviews(page, app.config["POSTS_PER_PAGE"])
    return render_template('viewreviewuser.html', reviews=reviews, page=page, count_pages=count_pages)
