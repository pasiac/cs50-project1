import os, re

from flask import Flask, session, render_template, request, g, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import requests, json


app = Flask(__name__)
app.config['TESTING'] = True
app.debug = True


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


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        item = request.form.get("item")
        books = (db.execute("SELECT * FROM books WHERE "
                            "isbn LIKE :item OR author LIKE :item OR title LIKE :item",
                            {"item": (item+'%').capitalize()})).fetchall()
        return render_template("index.html", books=books)


# TODO: something with session to get user real log in system
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        login = request.form.get("login")
        password = request.form.get("password")
        email = request.form.get("email")
        if db.execute("SELECT * FROM users WHERE login = :login OR email = :email",
                      {"login": login, "email": email}).rowcount == 0:
            db.execute("INSERT INTO users(login, password, email) VALUES (:login, :password, :email)",
                       {"login": login, "password": password, "email": email})
            db.commit()
            return render_template("login.html", newaccount=True)
        else:
            return render_template("register.html", isExist=True)


@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


@app.route("/logout")
def logout():
    session.pop('user', None)
    g.user = None
    return render_template("index.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        login = request.form.get("login")
        password = request.form.get("password")
        if db.execute("SELECT * FROM users WHERE login = :login AND password = :password",
                      {"login": login, "password": password}).rowcount != 0:
            session['user'] = login
            session['logged_in'] = True
            g.user = session['user']
            return render_template("index.html")
        else:
            is_wrong = True
            return render_template("login.html", wrong=is_wrong)
    # GET request
    return render_template("login.html")


@app.route("/books/<isbn>")
def books(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("errorLayout.html")
    data = requests.get(f"https://www.goodreads.com/book/review_counts.json?isbns={isbn}&key=XCZxj5AZYl3kaMUi80UeA").json()
    return render_template("books.html", book=book, data=data)



