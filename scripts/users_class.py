import re
import bcrypt

class User:
	db = None
	
	def __init__(self, conn):
		self.conn = conn
		self.db = self.conn.cursor()
	
	def checkIfIdExists(self, user_id):
		sql = "SELECT COUNT(*) FROM users WHERE id = %s;"
		self.db.execute(sql, (user_id,))
		
		result = self.db.fetchone()
		
		#if id already exists
		if result[0] > 0:
			return True
			
		return False
		
	def checkUsername(self, username):
		username = username.lower()
		
		if not username:
			return False
		
		if len(username) > 20:
			return False
		
		#if username includes spaces
		if (' ' in username) == True:
			return False
			
		#if username contains anything besides alphanumeric values
		if re.compile('[\W_]+').match(username):
			return False
		
		if self.checkUsernameExists(username):
			return False
		
		return True
	
	def checkUsernameExists(self, username):
		sql = "SELECT COUNT(*) FROM users WHERE username = %s;"
		self.db.execute(sql, (username,))
		
		result = self.db.fetchone()
		
		#if user already exists
		if result[0] > 0:
			return True
			
		return False
		
	def hashPassword(self, password):
		return bcrypt.hashpw(password, bcrypt.gensalt(12))
		
	def checkPassword(self, password, hashed):
		return bcrypt.checkpw(password, str(hashed))
		
	def createUser(self, username, password):
		#if username is not valid
		if not self.checkUsername(username):
			return False
			
		password = self.hashPassword(password)
		
		sql = "INSERT INTO users (username, password, user_level) VALUES (%s, %s, 0);"
		self.db.execute(sql, (username, password, ))
		self.conn.commit()
		return True
		
	def login(self, username, password):
		sql = "SELECT password FROM users WHERE username = %s;"
		self.db.execute(sql, (username, ))
		result = self.db.fetchall()
		
		if len(result) == 0:
			return False
			
		hashed = result[0][0]
		
		if self.checkPassword(password, hashed):
			return True
		
		return False
		
	def changePassword(self, user_id, password):
		password = self.hashPassword(password)
		
		sql = "UPDATE users SET password = %s WHERE id = %s;"
		self.db.execute(sql, (password, user_id))
		return True
	
	def changeUsername(self, user_id, username):
		if not self.checkUsername(username):
			return False
			
		sql = "UPDATE users set username = %s WHERE id = %s;"
		self.db.execute(sql, (username, user_id))
		return True
	
	def loadUserData(self, username):
		sql = "SELECT username, user_level FROM users WHERE username = %s;"
		self.db.execute(sql, (username,))
		
		return self.db.fetchall()
	
	def listUsers(self):
		sql = "SELECT username, user_level FROM users;"
		
		self.db.execute(sql)
		return self.db.fetchall()
	
	def editUserRights(self, username, new_level):
		self_data = self.loadUserData(session["username"])
		
		#if the user is trying to give a level over themselves
		if new_level > self_data["user_level"]:
			return False
		
		user_data = self.loadUserData(username)
		
		if self_data["user_level"] < user_data["user_level"]:
			return False
			
		sql = "UPDATE users SET user_level = %s WHERE username = %s;"
		self.db.execute()
	def getUsernameById(self, user_id):
		sql = "SELECT username FROM users WHERE id = %s;"
		
		self.db.execute(sql, (user_id,))
		username = self.db.fetchone()
		return username
		
	def getIdByUsername(self, username):
		if not self.checkUsernameExists(username):
			return False
		
		sql = "SELECT id FROM users WHERE username = %s;"
		
		self.db.execute(sql, (username,))
		username = self.db.fetchone()
		return username