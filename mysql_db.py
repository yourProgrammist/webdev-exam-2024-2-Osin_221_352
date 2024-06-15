import mysql.connector
from flask import g


class MySQL:
    def __init__(self, app):
        self.app = app
        app.teardown_appcontext(self.close_connection)

    def config(self):
        return {
            "user": self.app.config["MYSQL_USER"],
            "password": self.app.config["MYSQL_PASSWORD"],
            "database": self.app.config["MYSQL_DATABASE"],
            "host": self.app.config['MYSQL_HOST']
            # "port": self.app.config['MYSQL_PORT']
        }

    def connection(self):
        if 'db' not in g:
            try:
                g.db = mysql.connector.connect(**self.config())
            except mysql.connector.Error as error:
                print(f"mysql_db.py -> MySQL -> connection: {error}")
                g.db = None
        return g.db

    def close_connection(self, e=None):
        db = g.pop('db', None)
        if db is not None:
            db.close()
