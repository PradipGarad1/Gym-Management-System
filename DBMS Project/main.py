from flask import Flask, render_template , request , redirect, url_for,flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user, logout_user,login_manager , LoginManager
from flask_login import login_required,current_user
from datetime import datetime, date

#My DB Connection
local_server = True 
app = Flask(__name__)
app.secret_key='PradipGarad'


login_manager = LoginManager(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#app.config['SQLALCHEMY_DATABASE_URI']='mysql//:username:password@localhost/database_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/gymmanagsystem'
db =SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))
    email= db.Column(db.String(50),unique=True)
    gender =db.Column(db.String(50))
    age=db.Column(db.Integer)
    fee = db.Column(db.String(50))  
    password=db.Column(db.String(2000))
    city = db.Column(db.String(50))
    

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    time = db.Column(db.DateTime(50))
    date = db.Column(db.Date, nullable=False, default=date.today)  


#connect to pages
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/entry_history")
@login_required
def entry_history():
    # Fetch entry history for the current user
    user_entries = Entry.query.filter_by(email=current_user.email).all()

    return render_template('entry_history.html', user_entries=user_entries)

@app.route("/search", methods= ["POST","GET"])
def search():
    if request.method=="POST":
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("User Are There")
            return render_template('search.html')
        else:
            flash("User Are Not There")
            return render_template("search.html")
    return render_template("search.html")   
    
# Update your Flask app code
@app.route("/all_users")
def all_users():
    # Fetch all users
    all_users = User.query.all()
    return render_template('all_users.html', users=all_users)
@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        age = int(request.form.get('age'))
        fee = request.form.get('fee')
        password = request.form.get('password')
        my_city = request.form.get('city')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email already exists", "Denger")
            return render_template('signup.html')    


        else :
            if age>=18:
                encpassword = generate_password_hash(password)

                new_user = User(name=name, email=email, gender=gender, age=age,fee =fee, password=encpassword,city =my_city)
                db.session.add(new_user)
                db.session.commit()


                flash("Sign Up Succesfully Please Login")
                return render_template('login.html')
            else:
                flash("Your Age Below 18. You can not be a Memeber")
                return render_template('signup.html')

    return render_template('signup.html')


@app.route("/delete_user" ,methods=["POST", "GET"])
def delete_user():
    if request.method == "POST":
        email= request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            db.session.delete(user)
            db.session.commit()
            flash("User Deleted Succesfully")
            return redirect(url_for("index"))
        else:
            flash("Invalid email or password", "danger")

    return render_template('delete_user.html')
    

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password') 
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            if user.fee == 'Yes':
                time = datetime.now()
                current_date = date.today()
                login_entry = Entry(name=user.name, email=email, time=time, date=current_date)
                db.session.add(login_entry)
                db.session.commit()
                login_user(user)
                flash("Login Success", "primary")
                return redirect(url_for('index'))
            else:
                flash("Your are not paid fee. First Pay fee")
                return redirect(url_for('pay_fee'))

        else:
            flash("Invalid Entry", "danger")
            return render_template('login.html')

    return render_template('login.html')


@app.route("/pay_fee", methods=["GET", "POST"])
def pay_fee():
    if request.method == "POST":
        return redirect(url_for('index'))  
    else:
        return render_template('pay_fee.html', user=current_user) 


@app.route("/process_payment", methods=["POST"])
def process_payment():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        fee = request.form.get("fee")

        # Validate the user's  email and password
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            user.fee = fee
            db.session.commit()
        
            if fee == "No":
                flash("Fee is not paid. Please pay the fee to access the gym.", "danger")
                return redirect(url_for("index"))

            flash("Payment status updated successfully", "success")
            return redirect(url_for("login"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("pay_fee"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Muscle Pumped UP? Thank You" , "warning")
    return redirect(url_for('login'))
app.run(debug=True)