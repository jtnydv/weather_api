from flask import Flask, current_app
from flask_restful import Api
from flask_apscheduler import APScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from resources.city import City
from resources.weather import Weather

from models.city import CityModel
from models.weather import WeatherModel

from datetime import datetime
from darksky import forecast
from config import darksky_key


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
api = Api(app)

# Create tables before executing the first query
@app.before_first_request
def create_tables():
    db.create_all()

# Add resources to the API
api.add_resource(City, '/city', '/city/<string:name>', methods = ['GET', 'POST', 'DELETE'])
api.add_resource(Weather, '/weather/<int:w_id>', '/weather', methods = ['GET', 'PUT', 'DELETE'])

if __name__ == "__main__":
    from db import db
    db.app = app
    db.init_app(app)

    with db.app.app_context():
        # Helper function that adds new entries to the database every 24 hours
        def add_weather(city, today_in):
            today = today_in.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
            weather_obj = forecast(darksky_key, city.latitude, city.longitude, time = today.isoformat())
            weather = WeatherModel(weather_obj.summary, weather_obj.temperature, weather_obj.humidity, city.name, today)
            weather.save_to_db()

        # Initiation function
        def job_fetch_weather():
            todays_datetime = datetime.now()
            for city in CityModel.query.all():
                add_weather(city, todays_datetime)

    # Configuration for Scheduler Job Settings
    class Config(object):
        JOBS = [
            {
                'id': 'add_weather_job',
                'func': job_fetch_weather,
                'trigger': 'interval',
                'hours': 24,
                'start_date' : '2017-12-05 17:00:00.000000'
                # 'seconds' : 10
            }
        ]

        SCHEDULER_JOBSTORES = {
            'new_default': SQLAlchemyJobStore(url = 'sqlite:///data.db')
        }

        SCHEDULER_API_ENABLED = True

    app.config.from_object(Config())

    # Start the scheduler and initialize
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run(port = 5000, debug = True, use_reloader =False)

    # Stop scheduler and remove all the jobs
    scheduler.delete_all_jobs()
    scheduler.shutdown()