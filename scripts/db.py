import mysql.connector
from users_class import User
from messages_class import Messages

def db_connect():
	connection = mysql.connector.connect(
		host = "localhost",
		user = "cruise",
		passwd = "cruise-chat",
		db = "cruise"
	)
	
	return connection

user = User(db_connect())

messages = Messages(user, db_connect())
#messages.sendGroupChat(2, 1, "test group chat")
#messages.addDirectChat(2, 2, "test direct chat")
#messages.addGeneralChat("test general chat", 1)