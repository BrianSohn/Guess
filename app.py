import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    '''display homepage'''
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username")

        # Ensure username does not exist already
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if rows:
            return apology("username already exists")

        # Ensure password and confirmation are not blank
        if not password:
            return apology("must provide password")

        if not confirmation:
            return apology("must confirm password")

        # Ensure password and confirmation match
        if password != confirmation:
            return apology("password and confirmation do not match")

        # Insert username and password into database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, generate_password_hash(password))

        # Redirect user to homepage
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/create-group", methods=["POST"])
@login_required
def create_group():
    """Create a new group"""
    group_name = request.form.get("name")
    group_code = request.form.get("code")

    # Ensure group name was submitted
    if not group_name:
        return apology("must provide group name")
    
    # Ensure group code was submitted
    if not group_code:
        return apology("must provide group code")
    
    # Ensure group with same name and code does not exist already
    rows = db.execute("SELECT * FROM groups WHERE groupname = ? AND hash = ?", group_name, generate_password_hash(group_code))
    if rows:
        return apology("Group with identical name & code exists already")

    # Insert group name and code into Groups table
    group_id = db.execute("INSERT INTO groups (groupname, hash) VALUES (?, ?)", group_name, generate_password_hash(group_code))

    # Insert group-user pair into userGroup table
    db.execute("INSERT INTO userGroup (group_id, user_id) VALUES (?, ?)", group_id, session["user_id"])

    # Redirect user to homepage
    return redirect("/groups")


@app.route("/join-group", methods=["POST"])
@login_required
def join_group():
    """Join an existing group"""
    group_name = request.form.get("name")
    group_code = request.form.get("code")

    # Ensure group name was submitted
    if not group_name:
        return apology("must provide group name")
    
    # Ensure group code was submitted
    if not group_code:
        return apology("must provide group code")

    # Ensure group with same name and code exists already
    rows = db.execute("SELECT * FROM groups WHERE groupname = ?", group_name)
    rows = [row for row in rows if check_password_hash(row["hash"], group_code)]
    if len(rows) != 1:
        return apology("Incorrect group name / code")
    
    # Get group id
    group_id = rows[0]["id"]

    # Insert user into desired group in userGroup table
    db.execute("INSERT INTO userGroup (group_id, user_id) VALUES (?, ?)", group_id, session["user_id"])

    # Redirect user to homepage
    return redirect("/groups")


@app.route("/groups", methods=["GET", "POST"])
@login_required
def group():
    
    # User reached via POST, by clicking on a group button
    if request.method == "POST": 
        id = request.form.get("id")
        name = request.form.get("name")
        
        query = """
                SELECT u.username, ug.score, RANK() OVER (ORDER BY score DESC) AS ranking
                FROM userGroup AS ug
                JOIN users AS u ON ug.user_id = u.id
                WHERE ug.group_id = ?
                """
        ranking = db.execute(query, id)

        return render_template("group.html", name=name, ranking=ranking)
    
    # User reached via GET
    else: 
        '''show all groups user is joined in'''

        rows = db.execute("SELECT groups.id, groups.groupname FROM userGroup JOIN groups ON userGroup.group_id = groups.id WHERE user_id = ?", session["user_id"])

        return render_template("myGroups.html", rows=rows)
