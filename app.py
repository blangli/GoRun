from flask import Flask, redirect, render_template, get_flashed_messages, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required, UserMixin
from flask_bcrypt import Bcrypt
from wtforms import StringField, EmailField, SubmitField, PasswordField, DecimalField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, NumberRange
from datetime import datetime, timedelta
import time
import requests
import urllib
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)


app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
# Redirect URL - set to domain of website when deploying
REDIRECT = "http://127.0.0.1:5000/callback"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


#================== FORMS =====================#

class SignUpForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirmation = PasswordField("Password (again)", validators=[DataRequired()])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class GoalForm(FlaskForm):
    goal = DecimalField("Change weekly goal", validators=[DataRequired(), NumberRange(min=0, max=1000)])
    submit = SubmitField("Set")

#============= DATABASE MODEL ===================#

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    strava_username = db.Column(db.String(200), default='0')
    access_token = db.Column(db.String(200), default='0')
    refresh_token = db.Column(db.String(200), default='0')
    token_expiration = db.Column(db.String(200), default='0')
    goal = db.Column(db.Float, default='0')

    def __repr__(self):
        return '<Name %r>' % self.name




#=================== ROUTES ========================#

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/')
@app.route('/index')
def index():
    get_flashed_messages()
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    get_flashed_messages()
    
    if current_user.is_authenticated:
        return redirect("/account")

    form = LoginForm()

    if form.validate_on_submit():
        
        user = Users.query.filter_by(email=form.email.data).first()
        
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("You are logged in")
            return redirect("/data")
        
        else:
            flash("Login unsuccesful. Please check email and password")
            return redirect("/login")
    
    else:
        return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    get_flashed_messages()
    
    if current_user.is_authenticated:
        return redirect("/account")
    
    form = SignUpForm()
    
    if form.validate_on_submit():
        
        password = form.password.data
        confirmation = form.confirmation.data
        if password != confirmation:
            flash("Passwords don't match")
            return redirect("/signup")
        
        existing_user = Users.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash("Account already exists")
            return redirect("/signup")

        # Generate password hash
        password_hash = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Add new user to the database
        user = Users(name=form.name.data, email=form.email.data, password=password_hash)
        db.session.add(user)
        db.session.commit()

        flash("Registered")
        return redirect("/login")
            
    else:
        return render_template('signup.html', form=form)   


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():

    form = GoalForm()

    if form.validate_on_submit():
        current_user.goal = form.goal.data
        db.session.commit()
        return redirect('/data')

    email = current_user.email
    strava_username = current_user.strava_username

    return render_template('account.html', email=email, strava_username=strava_username, form=form)


@app.route('/data', methods=['GET', 'POST'])
@login_required
def data():

    goal = current_user.goal

    # When page is loaded, token expiration time must be checked against current datetime.
    # If expired, request for new token must be made. Then update the database with new token details.

    if current_user.access_token == "0" or current_user.refresh_token == "0":
        flash("Please connect Strava account")
        return redirect('/account')
    
    try:
        expiration = int(current_user.token_expiration)
        current_time = round(time.time())
    except:
        flash("Please connect Strava account")
        return redirect('/account')

    # If current time > expiration time, make a request to Strava for a new token.
    if current_time > expiration - 3000:
        strava_request = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            'client_id' : CLIENT_ID,
            'client_secret' : CLIENT_SECRET,
            'grant_type' : 'refresh_token',
            'refresh_token' : current_user.refresh_token
        }
        )
        strava_request = strava_request.json()

        current_user.access_token = strava_request["access_token"]
        current_user.refresh_token = strava_request["refresh_token"]
        current_user.token_expiration = strava_request["expires_at"]
        db.session.commit()
    

    # Request activites from Strava, to use the json to show run data 
    activities_url = 'https://www.strava.com/api/v3/athlete/activities'
    header = {'Authorization': 'Bearer ' + current_user.access_token}

    activities_request = requests.get(activities_url, headers=header)
    data = activities_request.json()


    date = datetime.date(datetime.today())
    day_of_week = datetime.isoweekday(date)
    # Last week's sunday.
    sunday = date - timedelta(days=day_of_week)
        

    # Create a list of lists, so that each index of the list can store each day of the week's activities ([0] = monday, [1] = tuesday etc.......)
    activity_list = [[] for i in range(7)]

    # Initialise a dict, to temporarily store each activity's data, before appending to the list.
    dict = {}
    # Loop through each day of the current week (mon-sun)
    for x in range(7):
        # Get each day of the week, relative to the previous Sunday.
        day = sunday + timedelta(days=(x+1))
        # Loop through each activity in the data downloaded from Strava.
        for activity in data:
            activity_date = (activity['start_date'][:-10])
            # If activity is a run, and the date matches the current day of week, put it into the dict. Then append the dict to the activity_list.
            if activity_date == str(day) and activity['sport_type'] == "Run":
                dict = {'Date': activity_date, 'Name': activity['name'], 'Distance': (str(activity['distance'] / 1000).rstrip('0').rstrip('.')), 'Time': round((activity['moving_time'] / 3600), 1)}
                activity_list[x].append(dict)
     
    # Number of runs in the current week
    activities_count = 0
    # Total distance ran
    distance_count = 0
    # Total distance ran on each day of the week
    daily_distance = []
    
    for day in activity_list:
        distance = 0
        for activity in day: 
            activities_count += 1
            
            distance_count += float(activity['Distance'])
            
            distance += float(activity['Distance'])
        
        if distance > 0:
            distance = str(round(distance, 2)).rstrip('0').rstrip('.')
        else:
            distance = 0 
        daily_distance.append(distance)
    

    # Calculate remaining distance left to reach weekly goal.
    remaining_distance = round(goal - distance_count, 3)
    if remaining_distance < 0:
        remaining_distance = 0

    # Calculate percentage of weekly goal completed (to go in the progress circle)
    percentage = 0
    
    if goal > 0:
        percentage = round((distance_count / goal) * 100)
        if percentage > 100:
            percentage = 100

    # Format variables to remove '.0'
    remaining_distance_str = 0
    distance_count_str = 0
    goal_str = 0

    if remaining_distance > 0:
        remaining_distance_str = str(remaining_distance).rstrip('0').rstrip('.')
    
    if distance_count > 0:
        distance_count_str = str(distance_count).rstrip('0').rstrip('.')

    if goal > 0:
        goal_str = str(goal).rstrip('0').rstrip('.')
    
    
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    return render_template('data.html', 
        expiration=expiration, 
        time=current_time, 
        activities_count=activities_count,
        distance_count=distance_count,
        goal=goal,
        remaining_distance=remaining_distance,
        daily_distance=daily_distance,
        weekdays=weekdays,
        activity_list=activity_list,
        percentage=percentage,
        remaining_distance_str=remaining_distance_str,
        distance_count_str=distance_count_str,
        goal_str=goal_str)


@app.route('/strava_login')
@login_required
def strava_login():
    
    # Redirect to strava Oauth page, passing in needed variables.
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT,
        'response_type': 'code',
        'scope': 'activity:read_all'
    }
    return redirect('{}?{}'.format(
        'https://www.strava.com/oauth/authorize',
        urllib.parse.urlencode(params)
    ))
    

@app.route('/callback', methods=['GET', 'POST'])
@login_required
def callback():
    
    # Get the one-time code from the strava redirect.
    CODE = request.args.get('code')
    
    # If there is no code, redirect to account.
    if CODE is None:
        return redirect('/account')
    
    SCOPE = request.args.get('scope')
    
    if SCOPE != "read,activity:read_all":
        flash("Couldn't get required permissions from Strava. Please try again")
        return redirect('/account')

    # Make request to Strava for authorization code and refresh code
    strava_request = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            'client_id' : CLIENT_ID,
            'client_secret' : CLIENT_SECRET,
            'code' : CODE,
            'grant_type' : 'authorization_code'
        }
    )
    
    strava_request = strava_request.json()

    # Get variables from callback response and put them into users database
    current_user.strava_username = strava_request["athlete"]["firstname"] + " " + strava_request["athlete"]["lastname"]
    current_user.access_token = strava_request["access_token"]
    current_user.refresh_token = strava_request["refresh_token"]
    current_user.token_expiration = strava_request["expires_at"]
    db.session.commit()
    

    # Redirect to data page once Strava account authorized
    flash('Strava account connected') 
    return redirect('/data')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect("/login")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)