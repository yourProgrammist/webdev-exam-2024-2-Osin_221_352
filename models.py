from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, login, password_hash=None, surname=None, name=None, patronymic=None, role_id=None):
        self.id = user_id
        self.login = login
        self.password_hash = password_hash
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.role = role_id
