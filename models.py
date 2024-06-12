from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, user_id, login, password_hash=None, surname=None, name=None, patronymic=None, role_id=None, role=None):
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
