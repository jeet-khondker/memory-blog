# Custom Error Handlers

from flask import render_template
from app import app, db

# FUNCTION: ACCESS/PERMISSION DENIED ERROR
@app.errorhandler(403)
def access_denied_error(error):
    return render_template("403.html"), 403

# FUNCTION: NOT FOUND ERROR
@app.errorhandler(404)
def not_found_error(error):
    return render_template("404.html"), 404

# FUNCTION: INTERNAL SERVER ERROR
@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template("500.html"), 500