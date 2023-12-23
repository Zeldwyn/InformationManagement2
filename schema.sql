//CREATE TABLES

CREATE TABLE IF NOT EXISTS User (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL
);

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

//CREATE PROCEDURE

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


//CREATE TRIGGER

DROP TRIGGER IF EXISTS deleteAllContent;
CREATE TRIGGER deleteAllContent
BEFORE DELETE ON PostContent
FOR EACH ROW
BEGIN
    DELETE FROM ReplyContent WHERE content_id = OLD.content_id;
END;
