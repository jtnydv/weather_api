import googlemaps
from flask import jsonify, request
from flask_restful import Resource

from datetime import datetime, timedelta
from darksky import forecast

from models.city import CityModel
from models.weather import WeatherModel
from config import darksky_key, google_key

class City(Resource):
    # /city
    # List all the cities present in the database
    def get(self):
        return jsonify([city.json() for city in CityModel.query.all()])

    # /city 
    # data = {name = "<city name>"}
    # Adds a new city to the DB and adds last 5 day weather forecast
    def post(self):
        request_data = request.get_json(silent = True)

        if request_data is None:
            return {'message' : 'Please add a city name before continuing'}, 400
        name = request_data.get('name')

        
        # Check if city already exists
        if CityModel.find_by_name(name.lower()):
            return {'message' : 'A city with name {} already exists'.format(name)}, 400

        # Fetch latitude and longitude from GMaps
        gmaps = googlemaps.Client(key = google_key)
        latitude = gmaps.geocode(name)[0]['geometry']['location']['lat']
        longitude = gmaps.geocode(name)[0]['geometry']['location']['lng']

        todays_datetime = datetime.now()

        # Add last 5 day's information
        for day in range(1, 6):
            past_date = todays_datetime.replace(hour = 0, minute = 0, second = 0, microsecond = 0) - timedelta(days = day)
            weather_obj = forecast(darksky_key, latitude, longitude, time = past_date.isoformat())
            weather = WeatherModel(weather_obj.summary, weather_obj.temperature, weather_obj.humidity, name, past_date)
            weather.save_to_db()

        try:
            city = CityModel(name.lower(), latitude, longitude)
            city.save_to_db()
        except:
            return {'message' : 'Some error occured while saving'}, 500

        return city.json(), 201

    # /city/<name>
    # Removes the city from the DB
    def delete(self, name):
        city = CityModel.find_by_name(name)

        if city:
            weather_list = WeatherModel.find_by_name(city.name)
            for obj in weather_list:
                obj.delete_from_db()
                
            city.delete_from_db()
            return {'message' : 'Deleted successfully'}, 200

        return {'message' : 'Requested city was not found'}, 400