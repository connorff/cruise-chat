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
    
    return render_template("chat_list.html")

@app.route("/chat/<username>")
def chat_user(username):
    if not checkSession():
        return redirect("/")

    return render_template("chat_user.html", username=username)

@app.route("/chat/new")
def chat_new():
    if not checkSession():
        return redirect("/")

    return render_template("chat_new.html")

@app.route("/groups")
def room_list():
    if not checkSession():
        return redirect("/")

    return render_template("room_list.html")

@app.route("/groups/<room_id>")
def room_id(room_id):
    if not checkSession():
        return redirect("/")

    return render_template("room_id.html", room_id=room_id)

@app.route("/groups/new")
def room_new():
    if not checkSession():
        return redirect("/")

    return render_template("room_new.html")

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
        return "false"

    print session.get("id")

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

def checkSession():
    if not session.get("username"):
        return False
    return True

app.run("0.0.0.0", port=5000)