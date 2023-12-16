import datetime
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask_mysqldb import MySQL
from database import init_db, execute
from functions import register_user, get_user, display_posts, display_reply



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

    CREATE PROCEDURE InsertReply(IN p_username VARCHAR(255), IN p_content_id INT,IN p_message VARCHAR(255),IN p_date DATE)
    BEGIN
        DECLARE p_user_id INT;
        SELECT user_id INTO p_user_id FROM User WHERE username = p_username;
        INSERT INTO ReplyContent (content_id, user_id,message, date) VALUES (p_content_id, p_user_id, p_message, p_date);
    END;

    DROP PROCEDURE IF EXISTS GetAllPosts;

    CREATE PROCEDURE GetAllPosts()
    BEGIN
        SELECT PC.content_id, PC.message, PC.date, U.username
        FROM PostContent PC
        JOIN User U ON PC.user_id = U.user_id;
    END;

    DROP PROCEDURE IF EXISTS GetRepliesByContentId;

    CREATE PROCEDURE GetRepliesByContentId(IN p_content_id INT)
    BEGIN
        SELECT U.username, RC.message, RC.date
        FROM ReplyContent RC 
        JOIN User U ON RC.user_id = U.user_id
        WHERE RC.content_id = p_content_id;   
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
    DROP VIEW IF EXISTS UserPostView;
    CREATE VIEW UserPostView AS
    SELECT
        PC.content_id AS post_id,
        PC.message AS post,
        PC.date AS date,
        U.user_id AS user_id
    FROM
        PostContent PC
    JOIN
        User U ON PC.user_id = U.user_id;

    DROP VIEW IF EXISTS UserReplyView;
    CREATE VIEW UserReplyView AS
    SELECT
        PC.content_id AS post_id,
        RC.message AS reply,
        RC.date AS date,
        RC.reply_id AS reply_id,
        U.user_id AS user_id
    FROM
        PostContent PC
    LEFT JOIN
        ReplyContent RC ON PC.content_id = RC.content_id
    LEFT JOIN
        User U ON RC.user_id = U.user_id;
    """
    with app.app_context():
        execute(script)

def trigger():
    script = """
    DROP TRIGGER IF EXISTS deleteAllContent;
    CREATE TRIGGER deleteAllContent
    BEFORE DELETE ON PostContent
    FOR EACH ROW
    BEGIN
        DELETE FROM ReplyContent WHERE content_id = OLD.content_id;
    END;
    """
    with app.app_context():
        execute(script)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    username = session.get('username')
    posts = display_posts()
    reply = []
    for post in posts:
        replies = display_reply(post[0])
        reply.append(replies)
    
    return render_template('home.html', posts = posts,reply = reply, username = username)

@app.route('/display')
def display():
    user_id = session.get('user_id')
    try:
        user_posts = execute("SELECT * FROM userpostview WHERE user_id = %s", (user_id,), fetch=True)
        user_replies = execute("SELECT * FROM userreplyview WHERE user_id = %s", (user_id,), fetch=True)
        session['viewpost'] = user_posts
        session['viewreply'] = user_replies
        print(user_posts)
        print(user_replies)
        return render_template('display.html', user_posts=user_posts, user_replies=user_replies)
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return render_template('display.html', user_posts = user_posts, user_replies = user_replies)


@app.route('/register', methods=['GET', 'POST'])
def register():
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
        session['user_id'] = existing_user[0]
        if existing_user is not None:
            if password == existing_user[2]:
                session['username'] = username  
                alert_message = "Login Successful!"
                posts = display_posts()
                reply = []
                for post in posts:
                    replies = display_reply(post[0])
                    reply.append(replies)

                return render_template('home.html', show_alert=True, alert_message=alert_message, posts=posts, reply=reply, username = username)
            else:
                alert_message = "Invalid Credentials!"
                return render_template('index.html', show_alert=True, alert_message=alert_message)
        else:
            alert_message = "User does not exist!"
            return render_template('index.html', show_alert=True, alert_message=alert_message)
        
    return render_template('index.html', show_alert=True, alert_message=alert_message)

@app.route('/post_content', methods=['POST'])
def post_content():
    print("Reached /post_content route")
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
                reply = []
                for post in posts:
                    replies = display_reply(post[0])
                    reply.append(replies)
                return redirect(url_for('home', posts = posts, reply = reply, username = username))
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
    return render_template('home.html')

@app.route('/reply/<int:content_id>', methods=['GET', 'POST'])
def add_reply(content_id):
    if 'username' not in session:
        return render_template('index.html')  
    if request.method == 'POST':
        username = session['username']
        message = request.form.get('message')
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')  
        try:
            with app.app_context():
                execute("CALL InsertReply(%s, %s, %s, %s)", (username,content_id, message, date))
                posts = display_posts()
                session['posts'] = posts
                reply = []
                for post in posts:
                    replies = display_reply(post[0])
                    reply.append(replies)
                return redirect(url_for('home', posts = posts, reply = reply, username = username))  
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})
        
    return redirect(url_for('home'))

@app.route('/delete_post/<int:content_id>', methods=['GET', 'POST'])
def delete_post(content_id):
    try:
        with app.app_context():
            execute("DELETE FROM PostContent WHERE content_id = %s", (content_id,))
            return redirect(url_for('display'))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/delete_reply/<int:reply_id>', methods=['GET', 'POST'])
def delete_reply(reply_id):
    print("Reply_ID", reply_id)
    try:
        with app.app_context():
            execute("DELETE FROM ReplyContent WHERE reply_id = %s", (reply_id,))
            return redirect(url_for('display'))
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


    

if __name__ == '__main__':
    create_tables()
    procedures()
    view()
    trigger()
    
    app.run(debug=True)