"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

# --------------------------------------------#
#       GET | Personajes y planetas           #
# --------------------------------------------#

# -> Muestra todos los personajes


@app.route('/people', methods=['GET'])
def get_all_people():
    people_query = People.query.all()
    all_people = list(map(lambda x: x.serialize(), people_query))
    return jsonify(all_people), 200

# -> Muestra los personajes especificos


@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    person = People.query.get(people_id)
    if person is None:
        return jsonify({"msg": "Person not found"}), 404
    return jsonify(person.serialize()), 200

# -> Muestra todos los planetas


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets_query = Planet.query.all()
    all_planets = list(map(lambda x: x.serialize(), planets_query))
    return jsonify(all_planets), 200

# -> Muestra los planetas especificos


@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    return jsonify(planet.serialize()), 200

# -----------------------------#
#  GET | Usuarios y favoritos  #
# -----------------------------#

# -> Muestra todos los usuarios


@app.route('/users', methods=['GET'])
def get_all_users():
    users_query = User.query.all()
    all_users = list(map(lambda x: x.serialize(), users_query))
    return jsonify(all_users), 200

# -> Muestra los favoritos por usuarios


@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1

    favorites_query = Favorite.query.filter_by(user_id=current_user_id).all()
    all_favorites = list(map(lambda x: x.serialize(), favorites_query))
    return jsonify(all_favorites), 200

# ------------------------#
# [POST/DELETE] Favoritos #
# ------------------------#

# -> Agrega un planeta a tu lista de favoritos


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1

    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({"msg": "Planet not found"}), 404
    existing_fav = Favorite.query.filter_by(
        user_id=current_user_id, planet_id=planet_id).first()
    if existing_fav:
        return jsonify({"msg": "Planet already in favorites"}), 400
    new_fav = Favorite(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Planet added to favorites"}), 201

# -> Agrega un personaje a tu lista de favoritos


@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    current_user_id = 1

    people = People.query.get(people_id)
    if people is None:
        return jsonify({"msg": "Person not found"}), 404
    existing_fav = Favorite.query.filter_by(
        user_id=current_user_id, people_id=people_id).first()
    if existing_fav:
        return jsonify({"msg": "Person already in favorites"}), 400
    new_fav = Favorite(user_id=current_user_id, people_id=people_id)
    db.session.add(new_fav)
    db.session.commit()
    return jsonify({"msg": "Person added to favorites"}), 201

# -> Elimina un planeta en tu lista de favoritos


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1

    fav = Favorite.query.filter_by(
        user_id=current_user_id, planet_id=planet_id).first()
    if fav is None:
        return jsonify({"msg": "Favorite planet not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted"}), 200

# -> Elimina un planeta en tu lista de favoritos


@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    current_user_id = 1

    fav = Favorite.query.filter_by(
        user_id=current_user_id, people_id=people_id).first()
    if fav is None:
        return jsonify({"msg": "Favorite person not found"}), 404

    db.session.delete(fav)
    db.session.commit()
    return jsonify({"msg": "Favorite person deleted"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
