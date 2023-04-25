import os
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for
app = Flask(__name__)
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from datetime import timedelta
from App.models import db, user 
from App.database import init_db
from App.config import config

from App.controllers import (
    setup_jwt,
    setup_flask_login
)

from App.views import views

def add_views(app):
    for view in views:
        app.register_blueprint(view)

def configure_app(app, config, overrides):
    for key, value in config.items():
        if key in overrides:
            app.config[key] = overrides[key]
        else:
            app.config[key] = config[key]

def create_app(config_overrides={}):
    app = Flask(__name__, static_url_path='/static')
    configure_app(app, config, config_overrides)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['SEVER_NAME'] = '0.0.0.0'
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.config['UPLOADED_PHOTOS_DEST'] = "App/uploads"
    CORS(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    setup_jwt(app)
    setup_flask_login(app)
    app.app_context().push()
    return app


@app.route('/app', methods=['GET'])
@login_required
def login_page():
  return render_template('login.html')

@app.route('/app', methods=['GET'])
@login_required
def app_page():
    return render_template('index.html')

@app.route('/', methods=['GET'])
@app.route('/', methods=['GET'])
def signup_page():
  return render_template('signup.html')

@app.route('/', methods=['GET'])
@app.route('/', methods=['GET'])
def workout_page():
  return render_template('workout.html')

@app.route('/signup', methods=['POST'])
def signup_action():
  data = request.form  # get data from form submission
  newuser = user(username=data['username'], email=data['email'], password=data['password'])  # create user object
  try:
    db.session.add(newuser)
    db.session.commit()  # save user
    login_user(newuser)  # login the user
    flash('Account Created!')  # send message
    return redirect('index.html')  # redirect to homepage
  except Exception:  # attempted to insert a duplicate user
    db.session.rollback()
    flash("username or email already exists")  # error message
  return redirect('signup.html')


@app.route('/login', methods=['POST'])
def login_action():
  data = request.form
  user = user.query.filter_by(username=data['username']).first()
  if user and user.check_password(data['password']):  # check credentials
    flash('Logged in successfully.')  # send message to next page
    login_user(user)  # login the user
    return redirect('index.html')  # redirect to main page if login successful
  else:
    flash('Invalid username or password')  # send message to next page
  return redirect('')




@app.route('/logout', methods=['GET'])
@login_required
def logout_action():
  logout_user()
  flash('Logged Out')
  return redirect('login.html')


