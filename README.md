# Project 1

Web Programming with Python and JavaScript

This project is on a books website "bookalliance".It is basically a website where users can search for books using isbn,title 
or author and get details about the book(using raw sql commands).User first need to register with username and password and then login.
Users can  then view others' ratings and reviews and post their own reviews as well.Goodreads API has been used to 
provide books' average rating and rating count.Also API for this website is also available using url "api/<isbn>".
Here are the files used and their uses:

application.py- Used for flask and sqlalchemy
import.py     - For importing books.csv details into database
book.csv      - contains book details
index.html    - it is the login page
register.html - registration page
layout1.html  - it is the basic layout of index.html and register.html
layout2.html  - basic layout of books.html,details.html and homepage.html
homepage.html - where user can search for books 
books.html    - for displaying users' search results
details.html  - for displaying details of selected book and viewing others' reviews and writing your own 
error.html    - when someone tries to access url without logging in.


Database consists of 3 table:
Users:                         books:                        reviews:
user_id-primary key            books_id-Primary key          review_id-primary key
username- VARCHAR              isbn- VARCHAR                 user_id-foreign key references users
password-VARCHAR               author-VARCHAR                book_id-foreign key references books
                               year-INT                      review- VARCHAR
                               title-VARCHAR                 rating- INT
