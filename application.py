import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

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


# class Book:
#     def __init__(self, isbn, title, author, year):
#         self.isbn = isbn
#         self.title = title
#         self.author = author
#         self.year = year
#
#     def print_book(self):
#         print(f"isbn: {self.isbn}")
#         print(f"title: {self.title}")
#         print(f"author: {self.author}")
#         print(f"year: {self.year}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'GET':
        return render_template("index.html")
    else:
        item = request.form.get("item")
        books = (db.execute("SELECT * FROM books WHERE isbn = :item OR author = :item OR title = :item",
                            {"item": item}))
        if books is not None:
            return render_template("index.html", books=books)
        else:
            item = "No such book in the list"
            return render_template("index.html", message=item)


# @app.route("/search")
# def search(searchtext):
#     books = (db.execute("SELECT * FROM books WHERE isbn = :text OR author = :text OR title = :text",
#                         {"text": searchtext})).fetchall
#     if books is not None:
#         return render_template("index.html", books=books)
#     else:
#         return render_template("index.html")


# TODO: something with session to get user real log in system
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        login = request.form.get("login")
        password = request.form.get("password")
        email = request.form.get("email")
        if db.execute("SELECT * FROM users WHERE login = :login AND email = :email",
                      {"login": login, "email": email}).rowcount == 0:
            db.execute("INSERT INTO users(login, password, email) VALUES (:login, :password, :email)",
                       {"login": login, "password": password, "email": email})
            db.commit()
            return render_template("login.html", newaccount=True)
        else:
            #TODO did not work fix
            return render_template("register.html", isExist=True)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        login = request.form.get("login")
        password = request.form.get("password")
        message = "You logged in."
        if db.execute("SELECT * FROM users WHERE login = :login AND password = :password",
                      {"login": login, "password": password}).rowcount != 0:
            return render_template("successLayout.html", message=message)
        else:
            isWrong = True
            return render_template("login.html", wrong=isWrong)
