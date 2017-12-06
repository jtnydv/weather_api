from db import db

class WeatherModel(db.Model):
    __tablename__ = 'weather'

    id = db.Column(db.Integer, primary_key = True)
    summary = db.Column(db.String(80))
    temperature = db.Column(db.Float)
    humidity = db.Column(db.Float)
    city = db.Column(db.String(80))
    date = db.Column(db.DateTime)

    def __init__(self, summary, temperature, humidity, city, date):
        self.summary = summary
        self.temperature = temperature
        self.humidity = humidity
        self.city = city.lower()
        self.date = date

    def json(self):
        return {'id' : self.id,
                'summary' : self.summary,
                'temperature' : self.temperature,
                'humidity' : self.humidity,
                'date' : self.date.isoformat()}

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id = id).first()

    @classmethod
    def find_by_name_order_by_date(cls, city_name):
        return cls.query.filter_by(city = city_name).order_by(db.desc(WeatherModel.date)).limit(5).all()

    @classmethod
    def find_by_date(cls, city_name, date):
        return cls.query.filter_by(date = date, city = city_name).first()

    @classmethod
    def find_by_name(cls, city_name):
        return cls.query.filter_by(city = city_name).all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()