import os, secrets
from app import app, db
from PIL import Image
from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, PostForm, UpdateAccountForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Dashboard Route
@app.route('/')
@app.route("/dashboard")
@login_required
def dashboard():
    posts = Post.query.all()
    photo = url_for('static', filename = 'profile_photos/' + current_user.photo)
    return render_template("dashboard.html", photo = photo, title = "Dashboard", posts = posts)

# Login Route
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

# Logout Route
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("dashboard"))

# User Registration Route
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

# Save Photo Route
def save_photo(form_photo):
    random_hex = secrets.token_hex(8)
    _, fileExtension = os.path.splitext(form_photo.filename)
    photo_filename = random_hex + fileExtension
    photo_path = os.path.join(app.root_path, "static/profile_photos", photo_filename)

    output_size = (125, 125)
    img = Image.open(form_photo)
    img.thumbnail(output_size)
    img.save(photo_path)

    return photo_filename

# Account Information Route
@app.route("/user", methods = ["GET", "POST"])
@login_required
def user():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.photo.data:
            photo_file = save_photo(form.photo.data)
            current_user.photo = photo_file
        current_user.username = form.username.data
        current_user.firstname = form.firstname.data
        current_user.middlename = form.middlename.data
        current_user.lastname = form.lastname.data
        current_user.dob = form.dob.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your Account Has Been Successfully Updated!", "success")
        return redirect(url_for("user"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.middlename.data = current_user.middlename
        form.lastname.data = current_user.lastname
        form.dob.data = current_user.dob
        form.email.data = current_user.email
    photo = url_for('static', filename = 'profile_photos/' + current_user.photo)
    return render_template("account.html", user = user, photo = photo, form = form, title = "Account of {} {} {}".format(current_user.firstname, current_user.middlename, current_user.lastname))

# Post Information Route
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title = post.title, post = post)