from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.Integer)
    nearest_star = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='planet', cascade="all, delete-orphan")

    # Add serialization rules
    serialize_rules = ('-missions.planet', )


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    field_of_study = db.Column(db.String)

    # Add relationship
    missions = db.relationship('Mission', back_populates='scientist', cascade="all, delete-orphan")

    # Add serialization rules
    serialize_rules = ('-missions.scientist',)

    # Add validation
    @validates('name')
    def check_name_exists(self, key, name):
        if name:
            return name
        else:
            raise ValueError("Scientist name must exist")
        
    @validates('field_of_study')
    def check_field_exists(self, key, field_of_study):
        if field_of_study:
            return field_of_study
        else:
            raise ValueError("Scientist Field of Study must exist")


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'))

    # Add relationships
    scientist = db.relationship('Scientist', back_populates='missions')
    planet = db.relationship('Planet', back_populates='missions')

    # Add serialization rules
    serialize_rules = ('-scientist.missions', '-planet.missions')

    # Add validation
    @validates('name')
    def check_name(self, key, name):
        if name:
            return name
        else:
            raise ValueError("Mission name must exist")

    @validates('planet_id')
    def check_planet_id(self, key, planet_id):
        if planet_id:
            return planet_id
        else:
            raise ValueError("Missing planet id")
        
    @validates('scientist_id')
    def check_scientist_id(self, key, scientist_id):
        if scientist_id:
            return scientist_id
        else:
            raise ValueError("Missing Scientist Id")
        



# add any models you may need.