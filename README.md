
# InformationManagement2
def create_views_triggers_procedures():
    # Your SQL script for creating stored procedures
    sql_script = """
    DROP PROCEDURE IF EXISTS InsertUser;
    CREATE PROCEDURE InsertUser(
        IN p_username VARCHAR(255),
        IN p_password VARCHAR(255)
    )
    BEGIN
        INSERT INTO User (username, password) VALUES (p_username, p_password);
    END;
    """
    with app.app_context():
        execute(sql_script)