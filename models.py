from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, login, password_hash=None, surname=None, name=None, patronymic=None, role_id=None,
                 role=None):
        self.id = user_id
        self.login = login
        self.password_hash = password_hash
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.role_id = role_id

        self.role = role if role is None else role.role


class Role:
    def __init__(self, role_id, role, description):
        self.id = role_id
        self.role = role
        self.description = description


# class Book:
#     def __init__(self, book_id, short_description, year_publish, publisher, author, size_book, cover_id):
#         self.id = book_id
#         self.short_description = short_description
#         self.year_publish = year_publish
#         self.publisher = publisher
#         self.author = author
#         self.size_book = size_book
#         self.cover_id = cover_id
#
#
# class Review:
#     def __init__(self, review_id, book_id, user_id, mark, body_text, add_date):
#         self.id = review_id
#         self.book_id = book_id
#         self.user_id = user_id
#         self.mark = mark
#         self.body_text = body_text
#         self.add_date = add_date
