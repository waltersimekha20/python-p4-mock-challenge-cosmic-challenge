#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        scientists = Scientist.query.all()
        scientists_dict = [scientist.to_dict(rules = ('-missions',)) for scientist in scientists]
        return make_response(scientists_dict, 200)
    
    def post(self):
        form_data = request.get_json()
        name = form_data.get('name')
        field_of_study = form_data.get('field_of_study')
        try:
            new_scientist = Scientist(name=name, field_of_study=field_of_study)
            db.session.add(new_scientist)
            db.session.commit()
            return make_response(new_scientist.to_dict(), 201)
        except:
            respond = {"errors": ["validation errors"]}
            return make_response(respond, 400)


api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            response_body = scientist.to_dict()
            status_code = 200
        else:
            response_body = {"error": "Scientist not found"}
            status_code = 404

        return make_response(response_body, status_code)
    
    def patch(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            form_data = request.get_json()
            try:
                for attr in form_data:
                    setattr(scientist, attr, form_data.get(attr))
                db.session.add(scientist)
                db.session.commit()
                return make_response(scientist.to_dict(), 202)
            except:
                response_body = {"errors":["validation errors"]}
                return make_response(response_body, 400)
        else:
            response_body = {"error": "Scientist not found"}
            return make_response(response_body, 404)
        
    def delete(self, id):
        scientist = Scientist.query.filter_by(id=id).first()
        if scientist:
            db.session.delete(scientist)
            db.session.commit()
            return make_response({}, 204)
        else:
            response_body = {"error": "Scientist not found"}
            return make_response(response_body, 404)


api.add_resource(ScientistById, '/scientists/<int:id>')


class Planets(Resource):
    def get(self):
        planets = Planet.query.all()
        resp = [planet.to_dict(rules=('-missions',)) for planet in planets]
        return make_response(resp, 200)
    
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        form_data = request.get_json()
        name = form_data.get('name')
        scientist_id = form_data.get('scientist_id')
        planet_id = form_data.get('planet_id')

        try:
            new_mission = Mission(name=name, scientist_id=scientist_id, planet_id=planet_id)
            db.session.add(new_mission)
            db.session.commit()
            return make_response(new_mission.to_dict(), 201)
        except:
            resp = {"errors": ["validation errors"]}
            return make_response(resp, 400)

api.add_resource(Missions, '/missions')


if __name__ == '__main__':
    app.run(port=5555, debug=True)