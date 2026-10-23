from idlelib import query
import os
import uuid
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Session-এর জন্য Secret Key
app.secret_key = "my-secret-key"

# =========================
# PROFILE CONFIGURATION
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(
    BASE_DIR, "static", "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

PROFILE_DB = os.path.join(BASE_DIR, "profile.db")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}


# =========================
# DATABASE CONNECTION
# =========================

def get_profile_db():
    connection = sqlite3.connect(PROFILE_DB)
    connection.row_factory = sqlite3.Row
    return connection


# =========================
# INITIALIZE PROFILE DATABASE
# =========================

def init_profile_db():
    connection = get_profile_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            age TEXT,
            student_class TEXT,
            location TEXT,
            bio TEXT,
            image TEXT
        )
    """)

    connection.execute("""
        INSERT OR IGNORE INTO profile
        (id, name, age, student_class, location, bio, image)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        1,
        "Prithiraj",
        "14",
        "7",
        "Jashore, Bangladesh",
        "Welcome to my profile!",
        ""
    ))

    connection.commit()
    connection.close()


# =========================
# IMAGE VALIDATION
# =========================

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )
# =========================
# USERS
# =========================

# Temporary users dictionary
users = {}


# =========================
# PERSONAL INFORMATION
# =========================

name = "Prithiraj Nondy"
age = 14
student_class = 7
location = "Jashore, Bangladesh"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    # students.db-এর আগের location একই রাখা হয়েছে।
    connection = sqlite3.connect("students.db")
    connection.row_factory = sqlite3.Row
    return connection


def init_students_db():
    """students table না থাকলে তৈরি করবে; থাকলে আগের data বদলাবে না।"""
    connection = get_db_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            class INTEGER,
            grade TEXT
        )
    """)
    connection.commit()
    connection.close()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def index():

    # Login করা না থাকলে Login page
    if "username" not in session:

        return redirect(url_for("login"))

    return render_template(
        "index.html",
        name=name,
        age=age,
        student_class=student_class,
        location=location,
        username=session["username"]
    )


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    # আগে থেকেই Login করা থাকলে Home page
    if "username" in session:

        return redirect(url_for("index"))


    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")


        # Username এবং Password check
        if username in users and users[username] == password:

            # Permanent session
            session.permanent = True

            # Username session-এ save
            session["username"] = username

            return redirect(url_for("index"))


        else:

            return render_template(
                "login.html",
                error="Invalid username or password!"
            )


    return render_template("login.html")


# =========================
# SIGN UP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    # আগে থেকেই Login করা থাকলে Home page
    if "username" in session:

        return redirect(url_for("index"))


    if request.method == "POST":

        username = request.form.get("username")

        password = request.form.get("password")

        confirm_password = request.form.get("confirm_password")


        # =========================
        # EMPTY FIELD CHECK
        # =========================

        if not username or not password or not confirm_password:

            return render_template(
                "login.html",
                error="Please fill in all fields!"
            )


        # =========================
        # USERNAME CHECK
        # =========================

        if username in users:

            return render_template(
                "login.html",
                error="Username already exists!"
            )


        # =========================
        # PASSWORD CHECK
        # =========================

        if password != confirm_password:

            return render_template(
                "login.html",
                error="Passwords do not match!"
            )


        # =========================
        # CREATE ACCOUNT
        # =========================

        users[username] = password


        # Account তৈরি হওয়ার পর Login page
        return render_template(
            "login.html",
            success="Account created successfully! Please login."
        )


    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    # Session থেকে username remove
    session.pop("username", None)

    return redirect(url_for("login"))

# =========================
# ABOUT PAGE
# =========================
@app.route("/about")
def about():
    return render_template("about.html",
                           name=name,
                           age=age,
                           student_class=student_class)

# =========================
# CONTACT PAGE
# =========================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        contact_name = request.form["name"]

        email = request.form["email"]

        message = request.form["message"]


        print("Name:", contact_name)

        print("E-mail:", email)

        print("Message:", message)

        if query and contact:
            flash("Massage Send Successfully!")


        elif query and not contact:
            flash("Massage Failed To Send!")


        return render_template(
            "contact.html",
            success="Your message was sent successfully!"
        )


    return render_template("contact.html")


# =========================
# SERVICES PAGE
# =========================

@app.route("/service")
def services():

    return render_template("service.html")


# =========================
# MESSAGE SENT
# =========================

@app.route("/massage")
def massage():

    return render_template("massage.html")


# =========================
# GREETING
# =========================

@app.route("/greeting", methods=["GET", "POST"])
def greeting():

    username = None

    upper_name = None

    name_length = None


    if request.method == "POST":

        username = request.form["username"]

        upper_name = username.upper()

        name_length = len(username)


    return render_template(
        "greeting.html",
        username=username,
        upper_name=upper_name,
        name_length=name_length
    )


# =========================
# WORKERS
# =========================

@app.route("/students")
def students():

    connection = get_db_connection()

    students = connection.execute(
        "SELECT * FROM students"
    ).fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students
    )
# =========================
# ADD WORKERS
# =========================

@app.route("/add_student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]

        age = request.form["age"]

        student_class = request.form["class"]

        grade = request.form["grade"]


        connection = get_db_connection()


        connection.execute(
            """
            INSERT INTO students
            (name, age, class, grade)
            VALUES (?, ?, ?, ?)
            """,
            (
                name,
                age,
                student_class,
                grade
            )
        )


        connection.commit()

        connection.close()

        flash("Student Added Successfully!", "success")


        return redirect(url_for("students"))


    return render_template("add_student.html")


# =========================
# EDIT WORKERS
# =========================
@app.route("/edit-students/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    connection = get_db_connection()
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        student_class = request.form["class"]
        grade = request.form["grade"]

        connection.execute(
            """
            UPDATE students
            SET name = ?,
             age = ?,
              class = ?,
               grade = ?
               WHERE id = ?""",
            (
                name,
                age,
                student_class,
                grade,
                id
            )
        )

        connection.commit()
        connection.close()

        flash("Student Edited Successfully!", "success")

        return redirect(url_for("students"))

    students = connection.execute(
        "SELECT * FROM students WHERE id = ?",(id,)
    ).fetchall()

    connection.close()

    return render_template(
        "edit_student.html",
        students=students
    )

# =========================
# PROFILE PAGE
# =========================

@app.route("/profile")
def profile():
    connection = get_profile_db()

    user = connection.execute(
        "SELECT * FROM profile WHERE id = ?",
        (1,)
    ).fetchone()

    connection.close()

    return render_template(
        "profile_updated.html",
        user=user
    )
# =========================
# EDIT PROFILE
# =========================

@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    connection = get_profile_db()

    user = connection.execute(
        "SELECT * FROM profile WHERE id = ?",
        (1,)
    ).fetchone()

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        student_class = request.form.get(
            "student_class", ""
        ).strip()
        location = request.form.get(
            "location", ""
        ).strip()
        bio = request.form.get("bio", "").strip()

        # Name validation
        if not name or len(name) > 100:
            connection.close()
            flash("Enter a valid name.", "error")
            return redirect(url_for("edit_profile"))

        if len(location) > 150 or len(bio) > 1000:
            connection.close()
            flash("Some information is too long.", "error")
            return redirect(url_for("edit_profile"))

        # Keep existing profile picture
        image = user["image"] or ""

        uploaded_file = request.files.get("image")

        if uploaded_file and uploaded_file.filename:

            if not allowed_file(uploaded_file.filename):
                connection.close()
                flash(
                    "Choose a PNG, JPG, JPEG or WEBP image.",
                    "error"
                )
                return redirect(url_for("edit_profile"))

            # Generate a unique filename
            safe_name = secure_filename(uploaded_file.filename)
            if not safe_name or "." not in safe_name:
                connection.close()
                flash("The selected filename is not valid.", "error")
                return redirect(url_for("edit_profile"))

            extension = uploaded_file.filename.rsplit(".", 1)[1].lower()
            filename = f"{uuid.uuid4().hex}.{extension}"

            file_path = os.path.join(
                UPLOAD_FOLDER,
                filename
            )

            uploaded_file.save(file_path)

            # Remember the new filename in the database
            image = filename

        # Save updated information
        connection.execute("""
            UPDATE profile
            SET name = ?,
                age = ?,
                student_class = ?,
                location = ?,
                bio = ?,
                image = ?
            WHERE id = ?
        """, (
            name,
            age,
            student_class,
            location,
            bio,
            image,
            1
        ))

        connection.commit()
        connection.close()

        flash("Profile updated successfully!", "success")

        return redirect(url_for("profile"))

    connection.close()

    return render_template(
        "edit_profile.html",
        user=user
    )
# =========================
# DELETE WORKERS
# =========================
@app.route("/delete_student/<int:id>")
def delete_student(id):
    connection = get_db_connection()
    connection.execute(
        """
        DELETE FROM students WHERE id = ?""", (id,)
    )

    connection.commit()
    connection.close()

    flash("Student Delete Successfully!", "success")

    return redirect(url_for("students"))


# =========================
# SEARCH WORKERS
# =========================
@app.route("/search_students", methods=["GET", "POST"])
def search_students():

    query = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()
    else:
        query = request.args.get("query", "").strip()

    connection = get_db_connection()


    if query:
        students = connection.execute(
            """
            SELECT * FROM students
            WHERE name LIKE ?
            """,
            ("%" + query + "%",)
        ).fetchall()

    else:
        students = []

    connection.close()


    return render_template(
        "search_student.html",
        students=students,
        query=query
    )
# =========================
# RUN FLASK
# =========================

if __name__ == "__main__":
    # Flask চালুর আগেই প্রয়োজনীয় database/table তৈরি হবে।
    init_profile_db()
    app.run(debug=True)
