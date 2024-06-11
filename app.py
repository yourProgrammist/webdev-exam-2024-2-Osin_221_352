from flask import Flask
from mysql_db import MySQL

app = Flask(__name__)

app.config.from_pyfile('config.py')

db = MySQL(app)
