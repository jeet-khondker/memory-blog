import os, secrets
from app import app, db
from PIL import Image
from flask import render_template, flash, redirect, url_for, request, abort
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, PostForm, UpdateAccountForm, ResetPasswordRequestForm, ResetPasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from app.email import send_password_reset_email
from datetime import datetime

# When User Becomes Authenticated, Track The TimeStamp For Last Seen On Profile
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Dashboard Route
@app.route('/')
@app.route("/dashboard")
@login_required
def dashboard():
    page = request.args.get("page", 1, type = int)

    show_followed = False

    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get("show_followed", ''))
    if show_followed:
        query = current_user.followed_posts

    posts = Post.query.order_by(Post.created_datetime.desc()).paginate(page = page, per_page = 5)
    photo = url_for('static', filename = 'profile_photos/' + current_user.photo)

    return render_template("dashboard.html", photo = photo, title = "Dashboard", posts = posts, show_followed = show_followed)

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
    flash("You Are Successfully Logged Out", "info")
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
@app.route("/user/<string:username>", methods = ["GET", "POST"])
@login_required
def user(username):
    page = request.args.get("page", 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    total_posts = db.session.query(Post).filter_by(user_id = current_user.id).count()
    posts = Post.query.filter_by(author = user).order_by(Post.created_datetime.desc()).paginate(page = page, per_page = 5)
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
        return redirect(url_for("user", username = username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.middlename.data = current_user.middlename
        form.lastname.data = current_user.lastname
        form.dob.data = current_user.dob
        form.email.data = current_user.email
    photo = url_for('static', filename = 'profile_photos/' + current_user.photo)
    return render_template("account.html", user = user, posts = posts, total_posts = total_posts, photo = photo, form = form, title = "Account of {} {} {}".format(current_user.firstname, current_user.middlename, current_user.lastname))

# Post Information Route - READ Route
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title = post.title, post = post)

# Add A Post Route - CREATE Route
@app.route("/addPost", methods = ["GET", "POST"])
@login_required
def new_post():

    if request.method == "POST":
        # Taking Form Data To Add A Post
        post_title = request.form["title"]
        post_content = request.form["body"]

        # Storing Data in Post Model
        new_post = Post(title = post_title, body = post_content, author = current_user)

        # Adding in DB
        try:
            db.session.add(new_post)
            db.session.commit()
            flash("Your Post Has Been Successfully Created!", "success")
            return redirect(url_for("dashboard"))
        except:
            flash("There was an issue in creating your blog post! Please try again later.", "danger")

# Update Post Route
@app.route("/updatePost", methods = ["GET", "POST"])
def updatePost():
    if request.method == "POST":
        post = Post.query.get(request.form.get("id"))
        
        if post.author != current_user:
            abort(403)

        post.title = request.form["title"]
        post.body = request.form["body"]
        post.updated_datetime = datetime.utcnow()

        db.session.commit()
        flash("Post Updated Successfully!", "success")
        return redirect(url_for("dashboard"))

# Delete Post Route
@app.route("/deletePost/<int:id>")
def deletePost(id):
    post_to_delete = Post.query.get_or_404(id)

    if post.author != current_user:
        abort(403)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post Deleted Successfully!", "success")
        return redirect(url_for("dashboard"))
    except:
        flash("There was an issue in deleting your blog post! Please try again later.", "danger")

# Other User Profiles Route
@app.route("/userProfile/<string:username>")
def userProfile(username):
    page = request.args.get("page", 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    total_posts = db.session.query(Post).filter_by(user_id = user.id).count()
    posts = Post.query.filter_by(author = user).order_by(Post.created_datetime.desc()).paginate(page = page, per_page = 5)
    return render_template("userProfile.html", posts = posts, user = user, total_posts = total_posts)

# Follow User Route
@app.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username = username).first()

    if user is None:
        flash("User does not exist!", "danger")
        return redirect(url_for("dashboard"))

    if current_user.is_following(user):
        flash("You are already following this user!", "info")
        return redirect(url_for("userProfile", username = username))

    current_user.follow(user)
    db.session.commit()

    flash("You are now following {}".format(username), "success")
    return redirect(url_for("userProfile", username = username))

# Unfollow User Route
@app.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username = username).first()

    if user is None:
        flash("User does not exist!", "danger")
        return redirect(url_for("dashboard"))

    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))

    current_user.unfollow(user)
    db.session.commit()

    flash("You are not following {}".format(username), "success")
    return redirect(url_for("userProfile", username = username))

# Followers Route
@app.route("/followers/<username>")
def followers(username):
    user = User.query.filter_by(username = username).first()

    if user is None:
        flash("User does not exist!", "danger")
        return redirect(url_for("dashboard"))

    page = request.args.get("page", 1, type = int)
    users = user.followers.paginate(page = page, per_page = 5)

    follows = [{"user": item.follower, "follow_time": item.follow_time} for item in users.items]

    return render_template("followers.html", user = user, users = users, follows = follows, title = "Followers of")

# Following Users Route
@app.route("/followed/<username>")
def followed_by(username):
    user = User.query.filter_by(username = username).first()

    if user is None:
        flash("User does not exist!", "danger")
        return redirect(url_for("dashboard"))

    page = request.args.get("page", 1, type = int)
    users = user.followed.paginate(page = page, per_page = 5)

    follows = [{"user": item.followed, "follow_time": item.follow_time} for item in users.items]

    return render_template("followers.html", user = user, users = users, title = "Followed By", follows = follows)

# Reset Password Request Route
@app.route("/reset_password_request", methods = ["GET", "POST"])
def reset_password_request():
    
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Please check your email for the instructions to reset your password", "info")
        return redirect(url_for("login"))
    
    return render_template("reset_password_request.html", title = "Reset Password", form = form)

# Password Reset Route
@app.route("/reset_password/<token>", methods = ["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("dashboard"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Congratulations! Your password has been reset successfully.", "success")
        return redirect(url_for("login"))
        return render_template("reset_password.html", form = form)