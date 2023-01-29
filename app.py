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
    
    # Forget group info
    session["group_id"] = None

    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id and group_id
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

    # Forget any user_id and group_id
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
        if not session.get("group_id"): 
            name = request.form.get("name")
            session["group_id"] = request.form.get("id")
        else: 
            name = db.execute("SELECT * FROM groups WHERE id = ?", session["group_id"])[0]["groupname"]
        
        # Get leaderboard
        query1 = """
                SELECT u.username, ug.points, RANK() OVER (ORDER BY points DESC) AS ranking
                FROM userGroup AS ug
                JOIN users AS u ON ug.user_id = u.id
                WHERE ug.group_id = ?
                """
        ranking = db.execute(query1, session["group_id"])
        
        # Get upcoming games
        query2 = """
                SELECT ug.game_id, g.team1, g.team2, ug.bet1, ug.bet2
                FROM userGame AS ug
                JOIN games AS g ON ug.game_id = g.id
                WHERE g.group_id = ? AND ug.user_id = ? AND (g.result1 IS NULL OR g.result2 IS NULL)
                """

        upcoming = db.execute(query2, session["group_id"], session["user_id"])

        # Get game results
        query3 = """
                SELECT ug.game_id, g.team1, g.team2, ug.bet1, ug.bet2, g.result1, g.result2
                FROM userGame AS ug
                JOIN games AS g ON ug.game_id = g.id
                WHERE g.group_id = ? AND ug.user_id = ? AND (g.result1 IS NOT NULL AND g.result2 IS NOT NULL)
                """
        
        history = db.execute(query3, session["group_id"], session["user_id"])

        return render_template("group.html", name=name, ranking=ranking, upcoming=upcoming, history=history)
    
    # User reached via GET
    else: 
        '''show all groups user is joined in'''
        
        # Forget previous group info
        session["group_id"] = None

        rows = db.execute("SELECT groups.id, groups.groupname FROM userGroup JOIN groups ON userGroup.group_id = groups.id WHERE user_id = ?", session["user_id"])

        return render_template("myGroups.html", rows=rows)


@app.route("/create-game", methods=["POST"])
@login_required
def create_game():
    team1 = request.form.get("team1")
    team2 = request.form.get("team2")

    # Create game data in db
    game_id = db.execute("INSERT INTO games (group_id, team1, team2) VALUES (?, ?, ?)", session["group_id"], team1, team2)
    
    # Create user-game data in db
    user_group_data = db.execute("SELECT * FROM userGroup WHERE group_id = ?", session["group_id"])
    users_in_group = [user["user_id"] for user in user_group_data]

    for user in users_in_group:
        db.execute("INSERT INTO userGame (game_id, user_id) VALUES (?, ?)", game_id, user)

    # Redirect to groups using POST
    return redirect("/groups", code=307)


@app.route("/guess", methods=["POST"])
@login_required
def guess():
    game_id = request.form.get("guess_game_id")
    
    # Validate inputs
    try: 
        team1_score = int(request.form.get("guess_team1"))
        team2_score = int(request.form.get("guess_team2"))
        if team1_score < 0 or team2_score < 0: 
            return apology("Score must be a non-negative integer")
    except ValueError: 
        return apology("Score must be a non-negative integer")

    if team1_score == "" or team2_score == "": 
        return apology("Must guess for both teams!")

    # Insert guess into userGame table
    db.execute("UPDATE userGame SET bet1 = ?, bet2 = ? WHERE game_id = ? AND user_id = ?", team1_score, team2_score, game_id, session["user_id"])

    # Redirect to groups using POST
    return redirect("/groups", code=307)


@app.route("/results", methods=["POST"])
@login_required
def result():
    game_id = request.form.get("result_game_id")
    
    # Validate inputs
    try: 
        team1_score = int(request.form.get("result_team1"))
        team2_score = int(request.form.get("result_team2"))
        if team1_score < 0 or team2_score < 0: 
            return apology("Result must be a non-negative integer")
    except ValueError: 
        return apology("Result must be a non-negative integer")

    if team1_score == "" or team2_score == "": 
        return apology("Must post result for both teams!")

    # Insert result into games table
    db.execute("UPDATE games SET result1 = ?, result2 = ? WHERE id = ?", team1_score, team2_score, game_id)

    # Calculate points for everyone that made a guess
    
    if team1_score > team2_score: # team1 wins - increase point for those that betted that team1 will win
        db.execute("UPDATE userGame SET points = 1 WHERE game_id = ? AND bet1 > bet2", game_id)
        db.execute("UPDATE userGame SET points = 0 WHERE game_id = ? AND bet1 <= bet2", game_id)
    elif team1_score < team2_score: # team2 wins - increase point for those that betted that team2 will win
        db.execute("UPDATE userGame SET points = 1 WHERE game_id = ? AND bet1 < bet2", game_id)
        db.execute("UPDATE userGame SET points = 0 WHERE game_id = ? AND bet1 >= bet2", game_id)
    else: # draw - increase point for those that betted that the game will be a draw
        db.execute("UPDATE userGame SET points = 1 WHERE game_id = ? AND bet1 = bet2", game_id)
        db.execute("UPDATE userGame SET points = 0 WHERE game_id = ? AND bet1 != bet2", game_id)

    # Update points for leaderboard in userGroup table
    query = """
            UPDATE userGroup
            SET points = groupGameUser.user_point
            FROM (
                SELECT userGame.user_id, SUM(userGame.points) AS user_point
                FROM userGame
                JOIN games ON userGame.game_id = games.id
                WHERE group_id = ?
                GROUP BY userGame.user_id
            ) AS groupGameUser
            WHERE userGroup.group_id = ? AND userGroup.user_id = groupGameUser.user_id
            """

    db.execute(query, session["group_id"], session["group_id"])

    # Redirect to groups using POST
    return redirect("/groups", code=307)

