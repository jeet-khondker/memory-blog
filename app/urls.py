from app import app, db
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Dashboard Route
@app.route('/')
@app.route("/dashboard")
@login_required
def dashboard():
    photo = url_for('static', filename = 'profile_photos/' + current_user.photo)
    return render_template("dashboard.html", photo = photo, title = "Dashboard")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Username Or Password!", "danger")
            return redirect(url_for("login"))
        login_user(user, remember = form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for("dashboard")
        return redirect(next_page)
    return render_template("login.html", title = "Login", form = form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("dashboard"))

@app.route("/register", methods = ["POST", "GET"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username = form.username.data, firstname = form.firstname.data, middlename = form.middlename.data, lastname = form.lastname.data, dob = form.dob.data.strftime("%Y-%m-%d"), email = form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations! You are now a registered user.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title = "User Registration", form = form)

@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username = username).first_or_404()
    photo = url_for('static', filename = 'profile_photos/' + current_user.photo)
    return render_template("account.html", user = user, photo = photo, title = "Account of {} {} {}".format(current_user.firstname, current_user.middlename, current_user.lastname))