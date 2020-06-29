import os, secrets
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, PostForm, UpdateAccountForm, ResetPasswordRequestForm, ResetPasswordForm
from app.models import User, Post, Comment
from app.email import send_password_reset_email
from flask_mail import Message

# When User Becomes Authenticated, Track The TimeStamp For Last Seen On Profile
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Getting Current Date Time
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# Dashboard Route
@app.route('/')
@app.route("/dashboard")
@login_required
def dashboard():

    page = request.args.get("page", 1, type = int)

    posts = Post.query.order_by(Post.created_datetime.desc()).paginate(page = page, per_page = 5)
    comments = Comment.query.order_by(Comment.timestamp.desc())

    return render_template("dashboard.html", title = "Dashboard", posts = posts, comments = comments)

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

# Reset Password Request Route
@app.route("/reset_password", methods = ["GET", "POST"])
def reset_password_request():
    
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    
    form = ResetPasswordRequestForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
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

    if user is None:
        flash("Invalid Token", "warning")
        return redirect(url_for("reset_password_request"))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Congratulations! Your password has been reset successfully.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html", title = "Reset Password", form = form)

# Own User Account Information Route
@app.route("/user/<string:username>", methods = ["GET", "POST"])
@login_required
def user(username):

    page = request.args.get("page", 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    total_posts = db.session.query(Post).filter_by(user_id = current_user.id).count()
    posts = Post.query.filter_by(author = user).order_by(Post.created_datetime.desc()).paginate(page = page, per_page = 5)

    form = UpdateAccountForm()

    if form.validate_on_submit():

        current_user.username = form.username.data
        current_user.firstname = form.firstname.data
        current_user.middlename = form.middlename.data
        current_user.lastname = form.lastname.data
        current_user.dob = form.dob.data
        current_user.email = form.email.data

        db.session.commit()
        flash("Your Account Has Been Successfully Updated!", "success")

        return redirect(url_for("user", username = username, title = "Account of {} {} {}".format(current_user.firstname, current_user.middlename, current_user.lastname)))

    elif request.method == "GET":

        form.username.data = current_user.username
        form.firstname.data = current_user.firstname
        form.middlename.data = current_user.middlename
        form.lastname.data = current_user.lastname
        form.dob.data = current_user.dob
        form.email.data = current_user.email

    return render_template("account.html", user = user, posts = posts, total_posts = total_posts, form = form, title = "Account of {} {} {}".format(current_user.firstname, current_user.middlename, current_user.lastname))

# Post Information Route - READ Route
@app.route("/post/<int:post_id>")
@login_required
def post(post_id):

    post = Post.query.get_or_404(post_id)
    comments = Comment.query.order_by(Comment.timestamp.desc())

    return render_template("post.html", title = post.title, comments = comments, post = post)

# Add A Post - CREATE Route
@app.route("/addPost", methods = ["GET", "POST"])
@login_required
def new_post():

    if request.method == "POST":

        # Taking Form Data To Add A Post
        post_title = request.form["title"]
        post_content = request.form["body"]

        # Storing Data in Post Model (Including Post Photo)
        new_post = Post(title = post_title, body = post_content, author = current_user)

        # Adding in DB
        try:
            db.session.add(new_post)
            db.session.commit()
            flash("Your Post Has Been Successfully Created!", "success")

            return redirect(url_for("dashboard"))

        except:
            flash("There was an issue in creating your blog post! Please try again later.", "danger")

# Update Post - UPDATE Route
@app.route("/updatePost", methods = ["GET", "POST"])
@login_required
def updatePost():

    if request.method == "POST":
        post = Post.query.get(request.form.get("id"))
        
        # Checking If Author Is The Current User
        if post.author != current_user:
            abort(403)

        post.title = request.form["title"]
        post.body = request.form["body"]

        post.updated_datetime = datetime.utcnow()

        db.session.commit()
        flash("Post Updated Successfully!", "success")
        
        return redirect(url_for("dashboard"))

# Delete Post - DELETE Route
@app.route("/deletePost/<int:id>")
@login_required
def deletePost(id):
    post_to_delete = Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post Deleted Successfully!", "success")

        return redirect(url_for("dashboard"))

    except:
        flash("There was an issue in deleting your blog post! Please try again later.", "danger")

# Other User Profiles Route
@app.route("/userProfile/<string:username>")
@login_required
def userProfile(username):

    page = request.args.get("page", 1, type = int)
    user = User.query.filter_by(username = username).first_or_404()
    total_posts = db.session.query(Post).filter_by(user_id = user.id).count()
    posts = Post.query.filter_by(author = user).order_by(Post.created_datetime.desc()).paginate(page = page, per_page = 5)

    return render_template("userProfile.html", posts = posts, user = user, total_posts = total_posts, title = "Account of {} {} {}".format(user.firstname, user.middlename, user.lastname))

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
@login_required
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
@login_required
def followed_by(username):

    user = User.query.filter_by(username = username).first()

    if user is None:
        flash("User does not exist!", "danger")
        return redirect(url_for("dashboard"))

    page = request.args.get("page", 1, type = int)
    users = user.followed.paginate(page = page, per_page = 5)
    follows = [{"user": item.followed, "follow_time": item.follow_time} for item in users.items]

    return render_template("followers.html", user = user, users = users, title = "Followed By", follows = follows)

# Like/Unlike Post Action Route
@app.route("/like/<int:post_id>/<action>")
@login_required
def like_action(post_id, action):
    post = Post.query.filter_by(id = post_id).first_or_404()

    # Case: Like Action
    if action == "like":
        current_user.like_post(post)
        db.session.commit()
    
    # Case: Unlike Action
    if action == "unlike":
        current_user.unlike_post(post)
        db.session.commit()

    return redirect(request.referrer)

# Comment Post Route
@app.route("/post/<int:post_id>/comment", methods = ["GET", "POST"])
@login_required
def comment(post_id):

    post = Post.query.filter_by(id = post_id).first_or_404()

    if request.method == "POST":
        
        comment = Comment(text = request.form["comment"], user_id = current_user.id, post_id = post.id)
        db.session.add(comment)
        db.session.commit()
        flash("Your Comment Has Been Added To The Post Successfully!", "success")

        return redirect(url_for("dashboard"))

    return render_template("dashboard.html")

# Help/Support Route
@app.route("/help")
def help():
    return render_template("help.html", title = "Help/Support")