import os
from flask import Flask, render_template,request,session,jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
import requests

app= Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    usernames = db.execute("SELECT username FROM users")
    return render_template("register.html",usernames=usernames)


@app.route("/registration",methods=["POST","GET"])
def registration():
    name = request.form.get("name")
    password = request.form.get("password")
    if name and password:
        if request.method == "GET":
            return render_template("error.html", message="register or login first")
        else:
            if db.execute("SELECT username FROM users WHERE username = :name", {"name": name}).rowcount == 1:
                return render_template("register.html", message="username already exists")
            else:
                db.execute("INSERT into users (username,password) VALUES (:name,:password)",{"name": name, "password": password})
                db.commit()
                return render_template("index.html")
    else:
        return render_template("register.html",message="username and password are rquired")




@app.route("/login" ,methods=["POST"])
def login():
    name = request.form.get("name")
    password =request.form.get("password")
    if db.execute("SELECT username,password FROM users WHERE username = :name AND password = :password",{"name": name,"password":password}).rowcount == 1:
        session['username']=name
        return render_template("homepage.html",username1=session['username'])
    else:
        return render_template("index.html", message="username or password incorrect")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return  render_template("index.html")

@app.route("/homepage/books", methods=["POST"])
def search():
    search = request.form.get("search")
    if db.execute("SELECT isbn,title,author,year FROM books WHERE LOWER(title) LIKE '%"+search+"%' OR LOWER(author) LIKE '%"+search+"%' OR isbn LIKE '%"+search+"%'  ",{"search":search}).rowcount==0:
        return render_template("books.html",message="no books found",username1=session['username'])
    else:
        results = db.execute("SELECT isbn,title,author,year FROM books WHERE LOWER(title) LIKE '%"+search+"%' OR LOWER(author) LIKE '%"+search+"%' OR isbn LIKE '%"+search+"%' ",{"search":search}).fetchall()
        return render_template("books.html",results=results,username1=session['username'])

@app.route("/homepage/books/<string:isbn>",methods=["GET","POST"])
def details(isbn):
    x =db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()
    a = db.execute("SELECT * FROM reviews JOIN users ON reviews.user_id=users.user_id WHERE book_id=:bookid",{"bookid":x.books_id}).fetchall()
    res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key": "ruO7wCroXGRF3rec9tw", "isbns": isbn})


    if res.status_code == 200:
        data = res.json()
        info1 = data["books"][0]["average_rating"]
        info2 = data["books"][0]["work_ratings_count"]


        if request.method == "GET":
            if 'username' in session:
                return render_template("details.html", isbn=isbn, x=x, reviews=a, username1=session['username'],info1=info1, info2=info2)
            else:
                return render_template("index.html")

        else:
            userid = db.execute("SELECT user_id FROM users WHERE username=:username",{"username": session['username']}).fetchone()
            newreview = request.form.get("userreview")
            rating = request.form.get("rating")
            if newreview and rating:
                if db.execute("SELECT user_id,book_id FROM reviews WHERE user_id=:userid AND book_id=:bookid",{"userid": userid.user_id, "bookid": x.books_id}).rowcount == 1:
                    message = "You have already reviewed"
                    return render_template("details.html", username1=session['username'], isbn=isbn, x=x, message=message,reviews=a, info1=info1, info2=info2)
                else:
                    db.execute("INSERT into reviews (user_id,book_id,review,rating) VALUES (:userid,:bookid,:review,:rating)",{"userid": userid.user_id, "bookid": x.books_id, "review": newreview, "rating": rating})
                    db.commit()
                    a = db.execute(
                        "SELECT * FROM reviews JOIN users ON reviews.user_id=users.user_id WHERE book_id=:bookid",
                        {"bookid": x.books_id}).fetchall()
                    return render_template("details.html", username1=session['username'], isbn=isbn, x=x, reviews=a,info1=info1, info2=info2)
            else:
                message="submit both rating review"
                return render_template("details.html",username1=session['username'], isbn=isbn, x=x, message=message,reviews=a, info1=info1, info2=info2)


    else:
        if request.method == "GET":
            if 'username' in session:
                return render_template("details.html", isbn=isbn, x=x, reviews=a, username1=session['username'])
            else:
                return render_template("index.html")


        else:
            userid = db.execute("SELECT user_id FROM users WHERE username=:username",
                                {"username": session['username']}).fetchone()
            newreview = request.form.get("userreview")
            rating = request.form.get("rating")
            if newreview and rating:
                if db.execute("SELECT user_id,book_id FROM reviews WHERE user_id=:userid AND book_id=:bookid",{"userid": userid.user_id, "bookid": x.books_id}).rowcount == 1:
                    message = "already reviewed"
                    return render_template("details.html", username1=session['username'], isbn=isbn, x=x, message=message,reviews=a)
                else:
                    db.execute("INSERT into reviews (user_id,book_id,review,rating) VALUES (:userid,:bookid,:review,:rating)",{"userid": userid.user_id, "bookid": x.books_id, "review": newreview, "rating": rating})
                    db.commit()
                    return render_template("details.html", username1=session['username'], isbn=isbn, x=x, reviews=a,)
            else:
                message="submit both rating and review"
                return render_template("details.html", username1=session['username'], isbn=isbn, x=x, reviews=a,message=message )

@app.route("/api/<string:isbn>")
def api(isbn):
    if 'username' in session :
        x=db.execute("SELECT * FROM books WHERE isbn=:isbn",{"isbn":isbn}).fetchone()
        res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key": "ruO7wCroXGRF3rec9tw", "isbns": isbn})
        if res.status_code == 200:
            data = res.json()
            info1 = data["books"][0]["reviews_count"]
            info2 = data["books"][0]["average_rating"]
        if x is None:
            return jsonify({"error": "the requested ISBN number is not in database"}), 404
        return jsonify({
            "title": x.title,
            "author": x.author,
            "year": x.year,
            "isbn": x.isbn,
            "review_count": info1,
            "average_score": info2
            })
    else:
        return render_template("index.html")




if __name__ == '__main__':
    main()







