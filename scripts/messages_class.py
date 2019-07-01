from time import time
from django.utils.html import escape

class Messages:
    def __init__(self, user, conn):
        self.user = user
        self.conn = conn
        self.db = self.conn.cursor()

    def createGroupChat(self, users):
        if not isinstance(users, list):
            return False

        #removes duplicate users from the chat
        users = list(dict.fromkeys(users))

        #creates a new group chat and returns the id of the chat
        sql = "INSERT INTO group_messages (group_name) VALUES ('New Group');"
        self.db.execute(sql)
        self.conn.commit()
        group_id = self.db.lastrowid
        
        #adds a row in the group relational table that relates the user id and the group id
        for user_id in users:
            if not self.user.checkIfIdExists(user_id):
                return False

            sql = "INSERT INTO group_rel (group_id, user_id) VALUES (%s, %s);" % (group_id, user_id,)
            self.db.execute(sql)

        self.conn.commit()
        return True

    def addGeneralChat(self, content, user_id):
        if not self.user.checkIfIdExists(user_id):
            return False

        if not self.validate(content):
            return False

        content = self.sanitize(content)

        sql = "INSERT INTO general_chat (content, user_id, time) VALUES ('%s', %s, %s);" % (str(content), user_id, time(),)

        self.db.execute(sql)
        self.conn.commit()

    #loads chats after certain id that defaults to None
    def loadGeneralChat(self, comment_id = None):
        sql = ""
        if not comment_id:
            sql = "SELECT * FROM general_chat;"
        else:
            sql = "SELECT * FROM general_chat WHERE comment_id > %s;" % (comment_id,)

        self.db.execute(sql)
        return self.db.fetchall()

    def addDirectChat(self, sender_id, target_id, content):
        if not self.user.checkIfIdExists(sender_id) or not self.user.checkIfIdExists(target_id):
            return False

        if not self.validate(content):
            return False

        content = self.sanitize(content)

        sql = "INSERT INTO direct_messages (sender_id, target_id, content, time) VALUES (%s, %s, '%s', %s);" % (sender_id, target_id, content, int(time()),)

        self.db.execute(sql)
        self.conn.commit()

    def loadDirectChat(self, sender_id, target_id, given_time = None):
        if not self.user.checkIfIdExists(sender_id) or not self.user.checkIfIdExists(target_id):
            return False

        sql = ""
        if not given_time:
            sql = "SELECT * FROM direct_messages WHERE sender_id = %s AND target_id = %s;" % (sender_id, target_id,)
        else:
            sql = "SELECT * FROM direct_messages WHERE sender_id = %s AND target_id = %s AND time > %s;" % (sender_id, target_id, given_time,)

        self.db.execute(sql)
        return self.db.fetchall()

    def listGroupChats(self, user_id):
        if not self.user.checkIfIdExists(user_id):
            return False

        sql = "SELECT group_id FROM group_rel WHERE user_id = %s;" % (user_id,)
        self.db.execute(sql)

        chats = self.db.fetchall()

        data = []

        for chat in chats:
            data.append(list(self.loadGroupName(chat[0])) + [self.loadGroupUsers(chat[0])])

        return data

    def loadGroupUsers(self, group_id):
        if not self.checkGroupChatExists(group_id):
            return False

        #loads user id from group id
        sql = "SELECT user_id FROM group_rel WHERE group_id = %s;" % (group_id,)

        self.db.execute(sql)
        users = self.db.fetchall()
        data = []

        #appends the user's username to a list
        for user in users:
            username, user_level = self.user.loadUserData(self.user.getUsernameById(user[0])[0])[0]
            data.append(username)

        return data

    def loadGroupName(self, group_id):
        if not self.checkGroupChatExists(group_id):
            return False

        sql = "SELECT group_name FROM group_messages WHERE group_id = %s;" % (group_id,)

        self.db.execute(sql)

        return self.db.fetchone()

    def checkGroupChatExists(self, group_id):
        sql = "SELECT group_id FROM group_messages WHERE group_id = %s;" % (group_id,)

        self.db.execute(sql)

        return len(self.db.fetchall()) > 0

    def sendGroupChat(self, group_id, user_id, content):
        if not self.user.checkIfIdExists(user_id):
            return False

        if not self.checkGroupChatExists(group_id):
            return False

        if not self.validate(content):
            return False

        content = self.sanitize(content)

        sql = "INSERT INTO group_content (group_id, user_id, content, time) VALUES (%s, %s, '%s', %s);" % (group_id, user_id, content, int(time()))

        self.db.execute(sql)
        self.conn.commit()

    #loads chats after certain unix timestamp
    def loadGroupChat(self, group_id, given_time = None):
        sql = ""
        if not given_time:
            sql = "SELECT * FROM group_content WHERE group_id = %s;" % (group_id,)
        else:
            sql = "SELECT * FROM group_content WHERE group_id = %s AND time > %s" % (group_id, given_time)

        self.db.execute(sql)

        return self.db.fetchall()

    def validate(self, content):
        if len(content) > 250:
            return False
        
        return True
    
    def sanitize(self, content):
        return escape(content)

    def getTime(self, timestamp):
		currtime = int(time())
		
		diff = currtime - timestamp
		
		if diff < 60:
			return "Less than a minute ago"
		elif diff < 3600:
			return "About %s minutes ago" % (int(diff / 60))
		elif diff < 86400:
			return "About %s hours ago" % (int(diff / 3600))
		elif diff < 31536000:
			print "About %s days ago" & (int(diff / 86400))
		else:
			print "More than a year ago"