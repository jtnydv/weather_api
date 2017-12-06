from db import db

class CityModel(db.Model):
    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)

    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

    def json(self):
        return {'name' : self.name, 'latitude' : self.latitude, 'longitude' : self.longitude}

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name = name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()