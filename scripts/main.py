from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from users_class import User
from messages_class import Messages
from db import db_connect
import json

conn = db_connect()

user = User(conn)
messages = Messages(user, conn)

app = Flask(__name__, static_folder="../static", template_folder="..//tpl")

#session stuff
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)

@app.route("/", methods=["GET", "POST"])
def home():
    if not request.form.get("username"):
        return render_template("index.html")

    username = request.form.get("username")
    password = request.form.get("password")

    if user.login(username, password):
        session["username"] = username
        session["id"] = user.getIdByUsername(username)[0]
        return redirect(url_for("feed"))
    else:
        return render_template("index.html")

@app.route("/feed")
def feed():
    if not checkSession():
        return redirect("/")

    posts = list(messages.loadGeneralChat())

    i = 0
    for i in range(len(posts)):
        posts[i] = list(posts[i])
        posts[i][2] = user.getUsernameById(posts[i][2])[0]
        posts[i][3] = messages.getTime(posts[i][3])

    return render_template("feed.html", posts = posts)

@app.route("/chat")
def chat_list():
    if not checkSession():
        return redirect("/")
    
    chats = messages.loadDirectChatByUser(session.get("id"))

    return render_template("chat_list.html", chats=chats)

@app.route("/chat/<username>")
def chat_user(username):
    if not checkSession():
        return redirect("/")

    user_id = user.getIdByUsername(username)

    if not user_id:
        return redirect(url_for("chat_new"))

    user_id = user_id[0]
    
    chat = messages.loadDirectChat(session.get("id"), user_id)
    last_sent = chat[len(chat) - 1][3]

    return render_template("chat_user.html", username=username, posts=chat, last_sent=last_sent, user_id=user.getIdByUsername(username)[0])

@app.route("/chat/new", methods=["GET", "POST"])
def chat_new():
    if not checkSession():
        return redirect("/")

    if not request.form.get("message") or not request.form.get("id"):
        return render_template("chat_new.html")

    result = messages.addDirectChat(session.get("id"), request.form["id"], request.form["message"])

    if not result[0]:
        return render_template("chat_new.html", error=result[1])
    
    return redirect(url_for("chat_user", username=user.getUsernameById(request.form["id"])))
    

@app.route("/groups")
def room_list():
    if not checkSession():
        return redirect("/")

    chats = messages.loadGroupChatsByUser(session.get("id"))
    
    for i in range(len(chats)):
        user_string = ""
        for username in chats[i][5]:
            if username == chats[i][5][len(chats[i][5]) - 1]:
                user_string += username
            else:
                user_string += username + ", "
        chats[i][5] = user_string

    return render_template("room_list.html", chats=chats)

@app.route("/groups/<room_id>")
def room_id(room_id):
    if not checkSession():
        return redirect("/")

    posts = messages.loadGroupChat(session.get("id"), room_id)

    last_sent = posts[len(posts) - 1][3]

    return render_template("room_id.html", posts=posts, group_id=room_id, last_sent=last_sent)

@app.route("/groups/new", methods=["GET", "POST"])
def room_new():
    if not checkSession():
        return redirect("/")

    if not request.form.get("users") or not request.form.get("message"):
        return render_template("room_new.html")

    users = json.loads(request.form["users"])
    message = request.form["message"]

    created = messages.createGroupChat(session.get("id"), users, message)
    if not created[0]:
        print created[1]
        return render_template("room_new.html", error=created[1])
    else:
        return redirect(url_for("room_id", room_id=created[1]))
    

@app.route("/settings")
def settings():
    if not checkSession():
        return redirect("/")

    return render_template("settings.html")

@app.route("/api/check_general")
def check_general():
    if not checkSession():
        return redirect("/")

    if request.args.get("id"):
        return json.dumps(messages.loadGeneralChat(request.args["id"]))
    else:
        return json.dumps(messages.loadGeneralChat())

@app.route("/api/check_direct")
def check_direct():
    if not checkSession():
        return redirect("/")
    if not request.args.get("id"):
        return json.dumps(False)

    if request.args.get("time"):
        return json.dumps(messages.loadDirectChat(request.args["id"], session.get("id"), request.args["time"]))
    else:
        return json.dumps(messages.loadDirectChat(request.args["id"], session.get("id")))

@app.route("/api/check_group")
def check_group():
    if not checkSession():
        return redirect("/")
    
    if not request.args.get("id"):
        return json.dumps(False)

    if request.args.get("time"):
        return json.dumps(messages.loadGroupChat(session.get("id"), request.args["id"], request.args["time"]))
    
    return json.dumps(messages.loadGroupChat(session.get("id"), request.args["id"]))

@app.route("/api/post_general")
def post_general():
    if not checkSession():
        return redirect("/")

    if not request.args.get("content"):
        return json.dumps(False)

    return json.dumps(messages.addGeneralChat(request.args["content"], session.get("id")))

@app.route("/api/post_direct")
def post_direct():
    if not checkSession():
        return redirect("/")

    if not request.args.get("content") or not request.args.get("id"):
        return json.dumps(False)

    return json.dumps(messages.addDirectChat(session.get("id"), request.args["id"], request.args["content"])) 

@app.route("/api/post_group")
def post_group():
    if not checkSession():
        return redirect("/")
    
    if not request.args.get("content") or not request.args.get("id"):
        return json.dumps(False)

    return json.dumps(messages.sendGroupChat(request.args["id"], session.get("id"), request.args["content"]))

@app.route("/api/check_name")
def check_name():
    if not checkSession():
        return redirect("/")

    if not request.args.get("string"):
        return json.dumps(False)

    return json.dumps(user.getUsernameLike(request.args["string"]))

@app.route("/api/check_direct_chat")
def check_direct_chat():
    if not checkSession():
        return redirect("/")

    if not request.args.get("id"):
        return json.dumps(False)

    return json.dumps(messages.hasDirectChatWith(session.get("id"), request.args["id"]))

def checkSession():
    if not session.get("username"):
        return False
    return True

app.run("0.0.0.0", port=5000)