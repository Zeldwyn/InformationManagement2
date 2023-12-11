from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sample'

mysql = MySQL(app)

@app.route('/')
def hello():
    cur = mysql.connection.cursor()
    cur.execute("SELECT VERSION()")
    data = cur.fetchone()
    return f"MySQL Server Version: {data[0]}"

if __name__ == '__main__':
    app.run(debug=True)
