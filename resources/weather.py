from darksky import forecast
from flask import jsonify, request
from flask_restful import Resource
from dateutil.parser import parse, parserinfo

from models.city import CityModel
from models.weather import WeatherModel
from config import darksky_key, google_key

class Weather(Resource):
    # Helper function
    def get_weather(self, city_name):
        weather_obj = WeatherModel.find_by_name_order_by_date(city_name.lower())
        result = []
        for obj in weather_obj:
            result.append(obj.json())
        return {'city' : city_name, 'weather' : result}

    # Route Handlers

    # /weather
    # Get last 5 day weather information for all the cities in the database
    # /weather?city=<name>
    # Get last 5 days weather data for specified city
    # /weather?city=<name>&date=<date>
    # Get all the weather information for specific city filtered by date
    def get(self):
        city_name = request.args.get('city')
        date = request.args.get('date')

        # Response if no filter is provided
        if date is None and city_name is None:
            return [self.get_weather(city.name)for city in CityModel.query.all()], 200

        if city_name is None:
            return {'message' : 'Please enter a city name to get weather information'}, 400

        city = CityModel.find_by_name(city_name.lower())

        # Check if provided city exists in the database or not
        if city:
            # If city exists check if date is provided or not
            if date:
                input_date = parse(date, parserinfo(dayfirst = True)).replace(hour = 0, minute = 0, second = 0, microsecond = 0)
                # Check if weather information for a particular date is available or not
                weather_obj = WeatherModel.find_by_date(city.name, input_date)
                if weather_obj:
                    return weather_obj.json(), 200
                # If absent, fetch the data for the city from the API
                else:
                    new_forecast = forecast(darksky_key, city.latitude, city.longitude, time = input_date.isoformat())
                    return {'summary' : new_forecast.summary, 'temperature' : new_forecast.temperature, 'humidity' : new_forecast.humidity}, 200
            else:
                return self.get_weather(city.name), 200
        
        return {'message' : 'Requested city is not present in the database'}, 400

    # Edit weather information for specific ID
    # /weather/<id>
    def put(self, w_id):
        # Get all the allowed data
        summary = request.get_json().get('summary')
        temperature = request.get_json().get('temperature')
        humidity = request.get_json().get('humidity')

        weather_obj = WeatherModel.find_by_id(w_id)

        # Check if requested Weather object exist or not
        if weather_obj is None:
            return {'message' : 'Weather Object with reuested ID was not found!'}

        # Check if data fields exists or not
        if summary:
            weather_obj.summary = summary

        if temperature:
            weather_obj.temperature = temperature

        if humidity:
            weather_obj.humidity = humidity

        # Update the concerned object
        weather_obj.save_to_db()
        return weather_obj.json(), 200

    # Delete weather information for specific ID
    # /weather/<id>
    def delete(self, w_id):
        weather_obj = WeatherModel.find_by_id(w_id)

        # If weather object doesn't exist
        if weather_obj is None:
            return {'message' : 'Weather Object with reuested ID was not found!'}, 400

        # Delete from the database
        try:
            weather_obj.delete_from_db()
        except:
            return {'message' : 'There was an issue deleting the object'}, 500
        
        return {'message' : 'The requested Weather Object was deleted'}, 200