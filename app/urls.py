from app import app

# Dashboard Route
@app.route('/')
@app.route("/dashboard")
def dashboard():
    return "User Dashboard"
