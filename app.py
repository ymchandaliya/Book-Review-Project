import os
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session,sessionmaker
from flask import Flask,request,render_template,session
from flask_session import Session

app=Flask(__name__)

engine=create_engine("postgres://bftqfkexrtucxu:79677fd3c30aed91117949656c9b2aa42663fb3ef287ef94a4f862738370c1cd@ec2-174-129-27-158.compute-1.amazonaws.com:5432/dch7g1rbas0o3o")
db=scoped_session(sessionmaker(bind=engine))

app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]="filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register",methods=["POST"])
def register():
    # session.clear()
    name=request.form.get("name")
    username=request.form.get("user")
    password=request.form.get("password")
    row=db.execute("select id from users where username=:username",{"username":username}).fetchone()
    if row in None:
        db.execute("insert into users(name,username,password) values(:name,:username,:password)",{"name":name,"username":username,"password":password})
        db.commit()
        return render_template("message.html",message="You have successfully registered\nSign in and go ahead")
    else:
        return render_template("message.html",message="Username already exists!\nTry another one!!!")

@app.route("/sign in")
def signin():
    return render_template("signin.html")

# #global name
# uname=""

@app.route("/search",methods=["post"])
def check():
    session.clear()
    #users=db.execute("select username,password from users").fetchall()
    username=request.form.get("user")
    # global uname
    password=request.form.get("password")
    uname=db.execute("select id,username,password from users where username=:username and password=:password",{"username":username,"password":password}).fetchone()
    if uname is None:
        return render_template("message.html",message="Oops! It seems wrong username OR password")
    else:
        session["user_id"]=uname[0]
        session["user_name"]=uname[1]
        return render_template("search.html",username=session["user_name"])

@app.route("/books", methods=["post"])
def books():
    # global uname
    query=request.form.get("query")
    query1='%'+query+'%'
    bookslist=db.execute("select * from books where isbn like :isbn or title like :title or author like :author",{"isbn":query1,"title":query1,"author":query1}).fetchall()
    if len(bookslist) == 0:
        return render_template("error.html",message="Oops! No such book found")
    else:
        return render_template("books.html",bookslist=bookslist,username=session["user_name"])

@app.route("/search")
def search():
    # global uname
    return render_template("search.html",username=session["user_name"])

@app.route("/sign in")
def signout():
    session.clear()
    return render_template("signin.html")

@app.route("/details/<string:isbn>")
def details(isbn):
    # global uname
    res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key":"4obs0JcZebFbBlPvF8Gf3g","isbns":isbn})
    result=res.json()
    rating=result['books'][0]['work_text_reviews_count']
    average=result['books'][0]['average_rating']
    # users=db.execute("select id from users").fetchall()
    book=db.execute("select id,title,author,isbn,year from books where isbn=:isbn",{"isbn":isbn}).fetchone()
    reviews=db.execute("select users.username,reviews.rating,reviews.review from reviews INNER JOIN users on reviews.user_id=users.id where reviews.isbn=:isbn",{"isbn":isbn}).fetchall()
    return render_template("book.html",book=book,rating=rating,average=average,username=session["user_name"],reviews=reviews)

@app.route("/details/<int:book_id>",methods=["post"])
def reviews(book_id):
    rating=int(request.form.get("rating"))
    review=request.form.get("review")
    isbn=db.execute("select isbn from books where id=:book_id",{"book_id":book_id}).fetchone()
    count=db.execute("select user_id from reviews where user_id=:user_id and isbn=:isbn",{"user_id":session["user_id"],"isbn":isbn.isbn}).fetchone()
    if count is None:
        db.execute("insert into reviews(rating,review,user_id,book_id,isbn) values (:rating,:review,:user_id,:book_id,:isbn)",{"rating":rating,"review":review,"user_id":session["user_id"],"book_id":book_id,"isbn":isbn.isbn})
        db.commit()
        return render_template("error.html",message="Thank You! for submitting review")
    else:
        return render_template("error.html",message="You have already submitted review for this book")
