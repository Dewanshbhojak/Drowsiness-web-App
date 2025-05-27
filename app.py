from flask import Flask, render_template, request, redirect, session, flash, jsonify, send_from_directory
import Code  # Your drowsiness detection module
import json
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = "secret key"

client = MongoClient("mongodb://localhost:27017/")
db = client['drowsiness_system']
users_collection = db['user']

# ---------- Static Pages ----------

@app.route("/<path:path>")
def serve_page(path):
    return send_from_directory("static", path)

@app.route('/home')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')

# ---------- Register/Login ----------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            number = request.form['number']
            email = request.form['email']

            print("Received data:", username, password, number, email)

            if users_collection.find_one({"$or": [{"number": number}, {"email": email}]}):
                print("User already exists")
                flash("Email or number already registered")
                return redirect('/register')

            result = users_collection.insert_one({
                "username": username,
                "password": password,
                "number": number,
                "email": email
            })

            print("Inserted user ID:", result.inserted_id)

            flash("Account created! Please login.")
            return redirect('/')

        except Exception as e:
            print("Error:", e)
            flash("Something went wrong")
            return redirect('/register')

    return render_template('register.html')

      

 
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users_collection.find_one({"username": username, "password": password})
        if user:
            session['username'] = username
            return redirect('/home')
        else:
            flash("Invalid username or password")
            return redirect('/')  # FIXED: Redirect back to login, not /home
    return render_template('login.html')

# ---------- Drowsiness Detection ----------

@app.route('/run.html')
def run():
    Code.start1()
    return render_template("run.html")

@app.route('/test.html')
def test():
    return render_template("test.html")



@app.route("/dashboard.html")
def dashboard():
    return render_template( "dashboard.html")

# ---------- API Endpoint ----------
@app.route("/api/location")
def get_location():
    try:
        with open("location_data.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"location": "N/A", "city": "N/A", "region": "N/A", "country": "N/A"})

@app.route("/api/sleep_count")
def get_sleep_count():
    try:
        with open("sleep_data.json", "r") as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"sleep_count": 0})
    

# ---------- Main ----------

if __name__ == "__main__":
    app.run(debug=True)
