CREATE DATABASE cruise;

CREATE TABLE general_chat(
    comment_id INT(20) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    content VARCHAR(1000) NOT NULL, 
    user_id INT(4) NOT NULL,
    time INT(11) NOT NULL
);

CREATE TABLE group_messages(
    group_id INT(5) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    group_name VARCHAR(40) NOT NULL
);

CREATE TABLE group_content(
    group_id INT(5) NOT NULL,
    user_id INT(4) NOT NULL,
    content VARCHAR(1000) NOT NULL,
    time INT(11)
);

CREATE TABLE group_rel(
    group_id INT(5) NOT NULL,
    user_id INT(4) NOT NULL
);

CREATE TABLE direct_messages(
    sender_id INT(4) NOT NULL,
    target_id INT(4) NOT NULL,
    time INT(11) NOT NULL,
    content VARCHAR(1000) NOT NULL
);

CREATE TABLE direct_rel(
    user_1 INT(4) NOT NULL,
    user_2 INT(4) NOT NULL
);