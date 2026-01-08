from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

from config import Config
from app.services import ec2_services

mysql = MySQL()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mysql.init_app(app)

    # HOME
    @app.route("/")
    def home():
        if 'user_id' in session:
            return redirect(url_for("instances"))
        return render_template("index.html")

    # REGISTER (simple like old project)
    @app.route("/register", methods=['GET', 'POST'])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]

            hashed_pw = generate_password_hash(password)

            cur = mysql.connection.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                flash("Email already registered!", "danger")
                cur.close()
                return redirect(url_for("register"))

            cur.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, hashed_pw),
            )
            mysql.connection.commit()
            cur.close()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))

        return render_template("register.html")

    # LOGIN
    @app.route("/login", methods=['GET', 'POST'])
    def login():
        if request.method == "POST":
            email = request.form['email']
            password = request.form['password']

            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone()
            cur.close()

            if user and check_password_hash(user["password"], password):
                session['user_id'] = user["id"]
                session['username'] = user["username"]
                flash("Login successful!", "success")
                return redirect(url_for("instances"))
            else:
                flash("Invalid login, try again.", "danger")
                return redirect(url_for("login"))

        return render_template("login.html")

    # LOGOUT
    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logged out!", "info")
        return redirect(url_for("login"))

    # INSTANCE PAGE (protected)
    @app.route("/instances")
    def instances():
        if 'user_id' not in session:
            flash("Please login!", "warning")
            return redirect(url_for("login"))

        items = ec2_services.describe()
        return render_template("instances.html", instances=items)

    @app.route("/instances/<instance_id>/start", methods=["POST"])
    def start_instance(instance_id):
        if 'user_id' not in session:
            flash("Please login!", "warning")
            return redirect(url_for("login"))

        result = ec2_services.start_instance(instance_id, dry_run=True)
        flash(result["message"], "success" if result["success"] else "danger")
        return redirect(url_for("instances"))

    @app.route("/instances/<instance_id>/stop", methods=["POST"])
    def stop_instance(instance_id):
        if 'user_id' not in session:
            flash("Please login!", "warning")
            return redirect(url_for("login"))

        result = ec2_services.stop_instance(instance_id, dry_run=True)
        flash(result["message"], "success" if result["success"] else "danger")
        return redirect(url_for("instances"))

    return app
