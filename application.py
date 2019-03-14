import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/successreg", methods=["POST"])
def successreg():
    login = request.form.get("login")
    password = request.form.get("password")
    email = request.form.get("email")
    db.execute("INSERT INTO users(login, password, email) VALUES (:login, :password, :email)",
        {"login": login, "password": password, "email": email})
    db.commit()
    return render_template("successreg.html")


@app.route("/login")
def login():
    return render_template("login.html", wrong=False)


@app.route("/checklogin", methods=["POST"])
def checklogin():
    login = request.form.get("login")
    password = request.form.get("password")
    message = "You logged in."
    if db.execute("SELECT * FROM users WHERE login = :login AND password = :password",
                  {"login": login, "password": password}).rowcount != 0:
        return render_template("successLayout.html", message=message)
    else:
        isWrong = True
        return render_template("login.html", wrong=isWrong)







