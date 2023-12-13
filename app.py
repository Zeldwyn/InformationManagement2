import datetime
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from database import init_db, execute
from functions import register_user, get_user, display_posts



app = Flask(__name__)
app.secret_key = 'hatdog'

# MySQL database configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'sample'

mysql = MySQL(app)
init_db(app)

def create_tables():
    sql_script = """
    -- Create the User table
    CREATE TABLE IF NOT EXISTS User (
        user_id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL
    );

    -- Create the PostContent table
    CREATE TABLE IF NOT EXISTS PostContent (
        content_id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        message VARCHAR(255) NOT NULL,
        date DATE,
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );

    CREATE TABLE IF NOT EXISTS ReplyContent (
        reply_id INT AUTO_INCREMENT PRIMARY KEY,
        content_id INT,
        user_id INT,
        message VARCHAR(255) NOT NULL,
        date DATE,
        FOREIGN KEY (content_id) REFERENCES PostContent(content_id),
        FOREIGN KEY (user_id) REFERENCES User(user_id)
    );
    """
    with app.app_context():
        execute(sql_script)
        

def procedures():
    script = """
    DROP PROCEDURE IF EXISTS InsertUser;

    CREATE PROCEDURE InsertUser(IN p_username VARCHAR(255), IN p_password VARCHAR(255))
    BEGIN
        INSERT INTO User (username, password) VALUES (p_username, p_password);
    END;
    
    DROP PROCEDURE IF EXISTS InsertPost;

    CREATE PROCEDURE InsertPost(IN p_username VARCHAR(255),IN p_message VARCHAR(255),IN p_date DATE)
    BEGIN
        DECLARE p_user_id INT;
        SELECT user_id INTO p_user_id FROM User WHERE username = p_username;

        INSERT INTO postcontent (user_id, message, date) VALUES (p_user_id, p_message, p_date);
    END;

    DROP PROCEDURE IF EXISTS InsertReply;

    CREATE PROCEDURE InsertReply(IN p_content_id INT,IN p_message VARCHAR(255),IN p_date DATE)
    BEGIN
        INSERT INTO ReplyContent (content_id, message, date) VALUES (p_content_id, p_message, p_date);
    END;

   DROP PROCEDURE IF EXISTS GetAllPosts;

    CREATE PROCEDURE GetAllPosts()
    BEGIN
        SELECT PC.content_id, PC.message, PC.date, U.username
        FROM PostContent PC
        JOIN User U ON PC.user_id = U.user_id;
    END;

    DROP PROCEDURE IF EXISTS GetUserByUsername;
    CREATE PROCEDURE GetUserByUsername(IN p_username VARCHAR(255))
    BEGIN
        SELECT * FROM User WHERE username = p_username;
    END;
    """
    with app.app_context():
        execute(script)

def view():
    script = """
    DROP VIEW IF EXISTS UserPostReplyView;
    CREATE VIEW UserPostReplyView AS
    SELECT
        U.user_id AS user_id,
        U.username AS username,
        PC.content_id AS post_id,
        PC.message AS post_message,
        PC.date AS post_date,
        RC.reply_id AS reply_id,
        RC.message AS reply_message,
        RC.date AS reply_date
    FROM
        User U
    LEFT JOIN
        PostContent PC ON U.user_id = PC.user_id
    LEFT JOIN
        ReplyContent RC ON PC.content_id = RC.content_id;
    """
    with app.app_context():
        execute(script)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    show_alert = False
    alert_message = ""

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        existing_user = get_user(username)
        if existing_user:
            alert_message = 'Username is already taken. Please choose a different one.'
            return render_template('register.html', show_alert=True, alert_message=alert_message)
        else:
            success = register_user(username, password)

            if success:
                alert_message = 'Registration successful!'
                return render_template('index.html', show_alert=True, alert_message=alert_message)
            else:
                alert_message = 'Registration failed!'    
                return render_template('register.html', show_alert=True, alert_message=alert_message)

    return render_template('register.html')
        
@app.route('/login', methods=['GET', 'POST'])
def login():
    alert_message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        existing_user = get_user(username)
        if existing_user is not None:
            if password == existing_user[2]:
                session['username'] = username  
                alert_message = "Login Successful!"
                posts = display_posts()
                return render_template('home.html', show_alert=True, alert_message=alert_message,posts=posts)
            else:
                alert_message = "Invalid Credentials!"
                return render_template('index.html', show_alert=True, alert_message=alert_message)
        else:
            alert_message = "User does not exist!"
            return render_template('index.html', show_alert=True, alert_message=alert_message)
        
    return render_template('index.html', show_alert=True, alert_message=alert_message)

@app.route('/post_content', methods=['POST'])
def post_content():
    if request.method == 'POST':
        if 'username' not in session:
            alert_message = "User does not exist!"
            return render_template('home.html', show_alert=True, alert_message=alert_message)

        username = session['username']
        message = request.form.get('message')
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
        try:
            with app.app_context():
                execute("CALL InsertPost(%s, %s, %s)", (username, message, date))
                posts = display_posts()
                return render_template('home.html', posts=posts)
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
    return render_template('home.html')
        
if __name__ == '__main__':
    create_tables()
    procedures()
    view()
    
    app.run(debug=True)