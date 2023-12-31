from flask import current_app
from database import execute

def register_user(username, password):
    try:
        with current_app.app_context():
            execute("CALL InsertUser(%s, %s)", (username, password))
        return True, None  
    except Exception as e:
        return False, str(e)
    
def get_user(username):
    try:
        with current_app.app_context():
            user = execute("CALL GetUserByUsername(%s)", (username,), fetch=True)
        return user[0] if user else None
    except Exception as e:
        print("Error fetching user:", str(e))
        return None
    
def display_posts():
    try:
        with current_app.app_context():
            posts = execute("CALL GetAllPosts()", fetch=True)
        return posts
    except Exception as e:
        print("Error fetching posts:", str(e))
        return [{'message': 'Error fetching posts', 'date': str(e)}]
    
def display_reply(content_id):
    try:
        with current_app.app_context():
            reply = execute("CALL GetRepliesByContentId(%s)", (content_id,), fetch=True)
            return reply
    except Exception as e:
        print(f"Error fetching replies for post {content_id}: {str(e)}")
        return [{'message': 'Error fetching replies', 'date': str(e)}]
