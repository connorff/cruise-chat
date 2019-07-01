from flask import Flask, render_template, request, session
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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/feed")
def feed():
    posts = list(messages.loadGeneralChat())

    i = 0
    for i in range(len(posts)):
        posts[i] = list(posts[i])
        posts[i][2] = user.getUsernameById(posts[i][2])[0]
        posts[i][3] = messages.getTime(posts[i][3])

    return render_template("feed.html", posts = posts)

@app.route("/chat")
def chat_list():
    return render_template("chat_list.html")

@app.route("/chat/<username>")
def chat_user(username):
    return render_template("chat_user.html", username=username)

@app.route("/chat/new")
def chat_new():
    return render_template("chat_new.html")

@app.route("/groups")
def room_list():
    return render_template("room_list.html")

@app.route("/groups/<room_id>")
def room_id(room_id):
    return render_template("room_id.html", room_id=room_id)

@app.route("/groups/new")
def room_new():
    return render_template("room_new.html")

@app.route("/settings")
def settings():
    return render_template("settings.html")

@app.route("/api/check_general")
def check_general():
    if request.args.get("id"):
        return json.dumps(messages.loadGeneralChat(request.args["id"]))
    else:
        return json.dumps(messages.loadGeneralChat())

@app.route("/api/check_direct")
def check_direct():
    if request.args.get("time"):
        return json.dumps(messages.loadDirectChat(request.args["time"]))
    else:
        return json.dumps(messages.loadGeneralChat())

@app.route("/api/check_group")
def check_group():
    return "hi"

app.run("0.0.0.0", port=5000)