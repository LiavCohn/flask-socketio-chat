from flask import (
    Flask,
    render_template,
    request,
    session,
    redirect,
    url_for,
    send_from_directory,
)
import os
from flask_socketio import SocketIO, emit

connected_clients = {}

app = Flask(__name__)
app.config["SECRET_KEY"] = "bla"
UPLOAD_FOLDER = "/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

socketio = SocketIO(app)

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        session["username"] = username

        return redirect(url_for("home"))
    return render_template("login.html")


@app.route("/")
@app.route("/home")
def home():
    if "username" not in session:
        return redirect(url_for("login"))

    return render_template("index.html", username=session["username"])


@socketio.on("connect")
def handle_connect():
    session["client_id"] = request.sid
    emit("connection_response", {"client_id": request.sid})

    if "username" in session:
        username = session["username"]

        # Add the client ID and username to the dictionary
        connected_clients[request.sid] = username

        # Get the list of all connected clients except the current one
        other_clients = [
            client_id for client_id in connected_clients if client_id != request.sid
        ]

        # Emit the message to all other connected clients
        for client_id in other_clients:
            socketio.emit(
                "chat_message",
                {"sender": "System", "message": f"{username} has logged in"},
                room=client_id,
            )


@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username", None)
        session.pop("client_id", None)

    return redirect(url_for("login"))


@socketio.on("disconnect")
def handle_disconnect():
    if "username" in session:
        username = session["username"]
        emit(
            "chat_message",
            {"sender": "System", "message": f"{username} has left the chat"},
            broadcast=True,
        )
        session.pop("username", None)
        session.pop("client_id", None)


@socketio.on("message")
def handle_message(data):
    sender = session.get("username")  # Get the username from the session
    message = data["message"]

    emit(
        "chat_message",
        {
            "sender": sender,
            "message": message,
            "client_id": session.get("client_id"),
        },
        broadcast=True,
    )


@socketio.on("upload")
def handle_upload(data):
    file = data["file"]
    filename = data["name"]
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        with open(filepath, "wb") as f:
            f.write(file)
    except Exception as e:
        print("Failed to save file", e)
    # Broadcast the URL of the uploaded file to all other users
    file_url = f"/uploads/{filename}"
    emit("file_uploaded", {"filename": filename, "file_url": file_url}, broadcast=True)


@app.route("/uploads/<path:filename>", methods=["GET", "POST"])
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"], filename, as_attachment=True
    )


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
