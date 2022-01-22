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


@app.route('/api/region', methods=['GET'])
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

@app.route('/api/region/<region_id>', methods=['GET'])
def one_region(region_id):

   region = Regions.query.get(region_id)

   if not region:
       return jsonify({'region': 'No region with id {}'.format(region_id)})

   result = {}
   result['id'] = region.id
   result['name'] = region.name
   city_names = [c.name for c in region.cities]
   result['cities'] = city_names

   return jsonify({'region': result})


@app.route('/api/city', methods=['GET'])
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


@app.route('/api/city/<city_id>', methods=['GET'])
def one_city(city_id):

   city = Cities.query.get(city_id)

   if not city:
       return jsonify({'city': 'No city with id {}'.format(city_id)})

   result = {}
   result['id'] = city.id
   result['name'] = city.name
   result['region'] = Regions.query.filter(Regions.id == city.region_id).first().name

   return jsonify({'city': result})


@app.route('/api/city/region_name/<region_name>', methods=['GET'])
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


@app.route('/api/city/region_id/<region_id>', methods=['GET'])
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


@app.route('/api/region', methods=['POST'])
@user_authorization
def create_region(current_user):
    data = request.get_json(force=True)
    if not data:
       return jsonify({'message' : 'No data.'})

    # check if the region already exists
    region = Regions.query.filter(Regions.id == data['id']).all()

    if region:
        return jsonify({'message' : 'Region with id {} already exists.'.format(data['id'])})
    else:
        new_region = Regions(id = data['id'], name=data['name'])
        db.session.add(new_region)
        db.session.commit()

    return jsonify({'message' : 'New region {} created.'.format(data['name'])})


@app.route('/api/city', methods=['POST'])
@user_authorization
def create_city(current_user):
    data = request.get_json(force=True)
    if not data:
       return jsonify({'message' : 'No data'})

    # check if the city already exists
    city = Cities.query.filter(Cities.id == data['id']).all()

    # check if the supplied region_id already exists
    region_id = Regions.query.filter(Regions.id == data['region_id']).all()

    if city:
        return jsonify({'message' : 'City with id {} already exists.'.format(data['id'])})
    elif not region_id:
        return jsonify({'message' : 'Region with id {} does not exist.'.format(data['region_id'])})
    else:
        new_city = Cities(id = data['id'], name=data['name'], region_id=data['region_id'])
        db.session.add(new_city)
        db.session.commit()

    return jsonify({'message' : 'New city {} created'.format(data['name'])})


@app.route('/api/region', methods=['PUT'])
@user_authorization
def update_region(current_user):
    data = request.get_json(force=True)
    if not data:
       return jsonify({'message' : 'No data.'})

    # check if the region exists
    region = Regions.query.get(data['id'])

    if not region:
        return jsonify({'message' : 'No region with id {}'.format(data['id'])})
    else:
        region.name = data['name']
        db.session.commit()

    return jsonify({'message' : 'Region {} is updated.'.format(data['id'])})


@app.route('/api/city', methods=['PUT'])
@user_authorization
def update_city(current_user):
    data = request.get_json(force=True)
    if not data:
       return jsonify({'message' : 'No data.'})

    # check if the city exists
    city = Cities.query.get(data['id'])

    if not city:
        return jsonify({'message' : 'No city with id {}'.format(data['id'])})
    else:
        city.name = data['name']
        city.region_id = data['region_id']
        db.session.commit()

    return jsonify({'message' : 'City {} is updated.'.format(data['id'])})


@app.route('/api/region/<region_id>', methods=['DELETE'])
@user_authorization
def delete_region(current_user, region_id):

    # check if the region exists
    region = Regions.query.get(region_id)

    if not region:
        return jsonify({'message' : 'No region with id {}'.format(region_id)})
    else:
        db.session.delete(region)
        db.session.commit()

    return jsonify({'message' : 'Region {} is deleted.'.format(region_id)})

@app.route('/api/city/<city_id>', methods=['DELETE'])
@user_authorization
def delete_city(current_user, city_id):

    # check if the city exists
    city = Cities.query.get(city_id)

    if not city:
        return jsonify({'message' : 'No city with id {}'.format(city_id)})
    else:
        db.session.delete(city)
        db.session.commit()

    return jsonify({'message' : 'City {} is deleted.'.format(city_id)})


if  __name__ == '__main__':
     app.run(debug=True)
