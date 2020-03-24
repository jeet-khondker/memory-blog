from app import app
from flask import render_template, url_for

# Dashboard Route
@app.route('/')
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", title = "Dashboard")
