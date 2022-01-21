import psycopg2
from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY']='fsDot32mWmw1v'
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@localhost:5432/regions'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Users(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255))
  password = db.Column(db.String(255))

class Regions(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True, nullable=False)
  cities = db.relationship('Cities', backref='regions', lazy=False)

class Cities(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True, nullable=False)
  region_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=False)

def user_authorization(func):
    @wraps(func)
    def authorization(*args, **kwargs):

       token = None

       if 'x-access-tokens' in request.headers:
          token = request.headers['x-access-tokens']


       if not token:
          return jsonify({'message': 'a valid token is missing'})


       try:
          data = jwt.decode(token, app.config[SECRET_KEY])
          current_user = Users.query.filter_by(public_id=data['id']).first()
       except:
          return jsonify({'message': 'token is invalid'})


          return func(current_user, *args,  **kwargs)
    return authorization


# create a token when a user logs in
@app.route('/login', methods=['GET', 'POST'])
def login_user():

  auth = request.authorization

  if not auth or not auth.username or not auth.password:
     return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

  user = Users.query.filter_by(username=auth.username).first()

  if check_password_hash(user.password, auth.password):
     token = jwt.encode({'id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
     return jsonify({'token' : token})

  return make_response('could not verify',  401, {'WWW.Authentication': 'Basic realm: "login required"'})


@app.route('/regions', methods=['GET'])
def all_regions():

   regions = Regions.query.all()

   result = []

   for reg in regions:
       reg_data = {}
       reg_data['id'] = reg.id
       reg_data['name'] = reg.name
       city_names = [c.name for c in Cities.query.filter(Cities.region_id == reg.id).all()]
       reg_data['cities'] = city_names

       result.append(reg_data)

   return jsonify({'regions': result})



if  __name__ == '__main__':
     app.run(debug=True)
