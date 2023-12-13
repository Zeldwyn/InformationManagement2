import MySQLdb
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = MySQLdb.connect(
            host=current_app.config['MYSQL_HOST'],
            user=current_app.config['MYSQL_USER'],
            password=current_app.config['MYSQL_PASSWORD'],
            db=current_app.config['MYSQL_DB']
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)

def execute(query, params=None, fetch=False):
    db = get_db()
    cursor = db.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            results = cursor.fetchall()
            return results
        else:
            db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

