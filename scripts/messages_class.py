from time import time
from django.utils.html import escape

class Messages:
    def __init__(self, user, conn):
        self.user = user
        self.conn = conn
        self.db = self.conn.cursor()

    def createGroupChat(self, self_user_id, users, message):
        if not isinstance(users, list):
            return [False, "There was an error processing the users"]

        #removes duplicate users from the chat
        users = list(dict.fromkeys(users))

        if len(users) == 1:
            return [False, "The group must have more than one other person"]

        #creates a new group chat and returns the id of the chat
        sql = "INSERT INTO group_messages (group_name) VALUES ('New Group');"
        self.db.execute(sql)
        self.conn.commit()
        group_id = self.db.lastrowid
        
        #adds a row in the group relational table that relates the user id and the group id
        for user_id in users:
            if not self.user.checkIfIdExists(user_id):
                return [False, "A user listed does not exist"]

            if user_id == self_user_id:
                return [False, "group cannot contain yourself"]

            sql = "INSERT INTO group_rel (group_id, user_id) VALUES (%s, %s);" % (group_id, user_id,)
            self.db.execute(sql)

        sql = "INSERT INTO group_rel (group_id, user_id) VALUES (%s, %s);" % (group_id, self_user_id,)
        self.db.execute(sql)

        sql = "INSERT INTO group_content (group_id, user_id, content, time) VALUES (%s, %s, '%s', %s);" % (group_id, self_user_id, message, int(time()))
        
        self.db.execute(sql)

        self.conn.commit()
        return [True, group_id]

    def addGeneralChat(self, content, user_id):
        if not self.user.checkIfIdExists(user_id):
            return False

        if not self.validate(content):
            return False

        content = self.sanitize(content)

        sql = "INSERT INTO general_chat (content, user_id, time) VALUES ('%s', %s, %s);" % (str(content), user_id, time(),)

        self.db.execute(sql)
        self.conn.commit()

        return True

    #loads chats after certain id that defaults to None
    def loadGeneralChat(self, comment_id = None):
        sql = ""
        if not comment_id:
            sql = "SELECT * FROM general_chat;"
        else:
            sql = "SELECT * FROM general_chat WHERE comment_id > %s;" % (comment_id,)

        self.db.execute(sql)
        results = self.db.fetchall()

        data = []
        for result in results:
            time = self.getTime(result[3])
            username = self.user.getUsernameById(result[2])[0]

            data.append([username, result[1], time, result[0]])

        return data

    def addDirectChat(self, sender_id, target_id, content):
        if not self.user.checkIfIdExists(sender_id) or not self.user.checkIfIdExists(target_id):
            return [False, "Provided ID is not valid"]

        if not self.validate(content):
            return [False, "Content given is not valid"]

        #checks if the chat has already been created
        sql = "SELECT * FROM direct_rel WHERE (user_1 = %s AND user_2 = %s) OR (user_2 = %s AND user_1 = %s);" % (sender_id, target_id, sender_id, target_id)

        self.db.execute(sql)

        results = self.db.fetchall()

        #if the chat has not been created yet, it makes it
        if len(results) == 0:
            sql = "INSERT INTO direct_rel (user_1, user_2) VALUES (%s, %s)" % (sender_id, target_id)
            self.db.execute(sql)

        content = self.sanitize(content)

        sql = "INSERT INTO direct_messages (sender_id, target_id, content, time) VALUES (%s, %s, '%s', %s);" % (sender_id, target_id, content, int(time()),)

        self.db.execute(sql)
        self.conn.commit()

        return [True]

    def loadDirectChat(self, sender_id, target_id, given_time = None):
        if not self.user.checkIfIdExists(sender_id) or not self.user.checkIfIdExists(target_id):
            return False

        sql = ""
        if not given_time:
            sql = "SELECT * FROM direct_messages WHERE (sender_id = %s AND target_id = %s) OR (target_id = %s AND sender_id = %s);" % (sender_id, target_id, sender_id, target_id,)
        else:
            sql = "SELECT * FROM direct_messages WHERE ((sender_id = %s AND target_id = %s) OR (target_id = %s AND sender_id = %s)) AND time > %s;" % (sender_id, target_id, sender_id, target_id, given_time,)

        self.db.execute(sql)
        results = list(self.db.fetchall())

        if len(results) == 0:
            return False

        data = []
        for result in results:
            time = self.getTime(result[2])
            username = self.user.getUsernameById(result[0])[0]

            data.append([username, result[3], time, result[2]])

        return data

    def loadDirectChatByUser(self, user_id):
        sql = "SELECT * FROM direct_rel WHERE user_1 = %s OR user_2 = %s;" % (user_id, user_id)

        self.db.execute(sql)
        results = self.db.fetchall()

        users = []
        for result in results:
            chat_user = result[1] if user_id == result[0] else result[0]
            sql = "SELECT * FROM direct_messages WHERE (sender_id = %s AND target_id = %s) OR (target_id = %s AND sender_id = %s) ORDER BY time DESC LIMIT 1;" % (user_id, chat_user, user_id, chat_user)

            self.db.execute(sql)
            last_sent = self.db.fetchone()
            last_sent_user = ""
            last_sent_content = last_sent[3]
            last_sent_time = self.getTime(last_sent[2])

            if last_sent[0] == user_id:
                last_sent_user = "You said: "
            else:
                last_sent_user = "They said: "

            chat_user = self.user.getUsernameById(chat_user)[0]
            users.append([chat_user, last_sent_content, last_sent_user, last_sent_time])

        return users

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
    def loadGroupChat(self, user_id, group_id, given_time = None):
        sql = "SELECT * FROM group_rel WHERE user_id = %s AND group_id = %s;" % (user_id, group_id)

        if not given_time:
            sql = "SELECT * FROM group_content WHERE group_id = %s;" % (group_id,)
        else:
            sql = "SELECT * FROM group_content WHERE group_id = %s AND time > %s" % (group_id, given_time)

        self.db.execute(sql)

        posts = self.db.fetchall()

        if len(posts) == 0:
            return False

        data = []
        for post in posts:
            username = self.user.getUsernameById(post[1])[0]
            content = post[2]
            post_time = self.getTime(post[3])
            data.append([username, content, post_time, post[3]])

        return data

    def loadGroupChatsByUser(self, user_id):
        sql = "SELECT * FROM group_rel WHERE user_id = %s;" % (user_id,)

        self.db.execute(sql)
        results = self.db.fetchall()

        groups = []
        for result in results:
            sql = "SELECT group_name FROM group_messages WHERE group_id = %s" % (result[0])

            self.db.execute(sql)
            group_name = self.db.fetchone()[0]

            sql = "SELECT * FROM group_content WHERE group_id = %s ORDER BY time DESC LIMIT 1;" % (result[0])

            self.db.execute(sql)
            group_id, user_id, content, time = self.db.fetchone()
            username = self.user.getUsernameById(user_id)[0]

            groups.append([group_name, group_id, "%s said:" % (username), content, self.getTime(time), self.loadGroupUsers(group_id)])

        return groups

    def validate(self, content):
        if len(content) > 250:
            return False
        
        return True
    
    def sanitize(self, content):
        return escape(content)

    def hasDirectChatWith(self, self_id, user_id):
        if not self.user.checkIfIdExists(user_id) or not self.user.checkIfIdExists(self_id):
            return False
        
        sql = "SELECT COUNT(*) FROM direct_messages WHERE (sender_id = %s AND target_id = %s) OR (target_id = %s AND sender_id = %s)" % (self_id, user_id, self_id, user_id,)

        self.db.execute(sql)

        return (self.db.fetchone()[0] > 0)

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
			return "About %s days ago" % (int(diff / 86400))
		else:
			return "More than a year ago"