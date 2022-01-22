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
          return jsonify({'message': 'A valid token is missing'})

        try:
          data = jwt.decode(token, app.config['SECRET_KEY'])
          current_user = Users.query.filter_by(id=data['id']).first()
        except:
          return jsonify({'message': 'Token is invalid'})

        return func(current_user, *args,  **kwargs)
    return authorization


# create a token when a user logs in
@app.route('/api/login', methods=['GET', 'POST'])
def login_user():

  auth = request.authorization

  if not auth or not auth.username or not auth.password:
     return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

  user = Users.query.filter_by(username=auth.username).first()

  if check_password_hash(user.password, auth.password):
     token = jwt.encode({'id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=60)}, app.config['SECRET_KEY'])
     return jsonify({'token' : token.decode('UTF-8')})

  return make_response('Could not verify',  401, {'WWW.Authentication': 'Basic realm: "Login required"'})


@app.route('/api/regions', methods=['GET'])
def all_regions():

   regions = Regions.query.all()

   result = []

   for reg in regions:
       reg_data = {}
       reg_data['id'] = reg.id
       reg_data['name'] = reg.name
       city_names = [c.name for c in reg.cities]
       reg_data['cities'] = city_names

       result.append(reg_data)

   return jsonify({'regions': result})


@app.route('/api/cities', methods=['GET'])
def all_cities():

   cities = Cities.query.all()

   result = []

   for city in cities:
       city_data = {}
       city_data['id'] = city.id
       city_data['name'] = city.name
       city_data['region'] = Regions.query.filter(Regions.id == city.region_id).first().name

       result.append(city_data)

   return jsonify({'cities': result})


@app.route('/api/cities_by_region_name/<region_name>', methods=['GET'])
def cities_by_region_name(region_name):
    region = Regions.query.filter(Regions.name == region_name).all()
    if not region:
       return jsonify({'message': 'No such region.'})

    cities = region[0].cities
    result = []

    for city in cities:
        city_data = {}
        city_data['id'] = city.id
        city_data['name'] = city.name

        result.append(city_data)

    return jsonify({'cities': result})


@app.route('/api/cities_by_region_id/<region_id>', methods=['GET'])
def cities_by_region_id(region_id):
    cities = Cities.query.filter(Cities.region_id == region_id).all()
    if not cities:
       return jsonify({'message': 'No such region.'})

    result = []

    for city in cities:
        city_data = {}
        city_data['id'] = city.id
        city_data['name'] = city.name

        result.append(city_data)

    return jsonify({'cities': result})


@app.route('/api/create_region', methods=['POST'])
@user_authorization
def create_region(current_user):
    data = request.get_json(force=True)
    if not data:
       return jsonify({'message' : 'No data.'})

    # check if the region already exists
    region = Regions.query.filter(Regions.name == data['name']).all()

    if region:
        return jsonify({'message' : 'Region already exists.'})
    else:
        current_num = len(Regions.query.all())
        new_region = Regions(id = current_num+1, name=data['name'])
        db.session.add(new_region)
        db.session.commit()

    return jsonify({'message' : 'New region {} created.'.format(data['name'])})


@app.route('/api/create_city', methods=['POST'])
@user_authorization
def create_city(current_user):
    data = request.get_json(force=True)
    if not data:
       return jsonify({'message' : 'No data'})

    # check if the city already exists
    city = Cities.query.filter(Cities.name == data['name']).all()

    # check if the supplied region_id already exists
    region_id = Regions.query.filter(Regions.id == data['region_id']).all()

    if city:
        return jsonify({'message' : 'City already exists.'})
    elif not region_id:
        return jsonify({'message' : 'This region id does not exist.'})
    else:
        current_num = len(Cities.query.all())
        print(current_num)
        new_city = Cities(id = current_num+1, name=data['name'], region_id=data['region_id'])
        db.session.add(new_city)
        db.session.commit()

    return jsonify({'message' : 'New city {} created'.format(data['name'])})




if  __name__ == '__main__':
     app.run(debug=True)
