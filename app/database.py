# app/database.py
from flask_mysqldb import MySQL

mysql = MySQL()

def configure_database(app):
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'root'
    app.config['MYSQL_DB'] = 'sample'

    mysql.init_app(app)
