from flask import Flask, request, render_template
import googlemaps
from weather import get_buienradar_weather
from datetime import datetime
from database import mycol
import os
from dotenv import load_dotenv


app = Flask(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

api_key = os.environ.get('API_KEY')

# Initialize the client with your API key
gmaps = googlemaps.Client(key=api_key)


def get_dict_trams(directions_res):
    dict_trams = {}
    for route in directions_res[0]['legs']:
        dict_trams[route['steps'][0]['transit_details']['line']['short_name']] = route['departure_time']['text']
    return dict_trams


def direction(route):
    if route == "center":
        directions_result = gmaps.directions("Amsterdam, Kronenburg",
                                             "Museumplein 6, 1071 DJ Amsterdam",
                                             mode="transit")

        dict_trams = get_dict_trams(directions_result)

        result = [f"Next tram № {tram_number} from kronenburg to centrall station: {time}" for tram_number, time in dict_trams.items()]
    else:
        directions_result = gmaps.directions("Museumplein 6, 1071 DJ Amsterdam",
                                             "Amsterdam, Kronenburg",
                                             mode="transit")

        dict_trams = get_dict_trams(directions_result)
        result = [f"Next tram № {tram_number} from kronenburg to westwijk: {time}" for tram_number, time in dict_trams.items()]
    return result


def get_activity(weekday):
    result = ""
    if weekday == 0:
        result = mycol.find_one({"day": "monday"})
    elif weekday == 1:
        result = mycol.find_one({"day": "tuesday"})
    return result


@app.route('/', methods=['GET', 'POST'])
def home_page():
    dict_result = {}

    weather = get_buienradar_weather()
    dict_result['weather'] = weather

    weekday = datetime.today().weekday()
    print(weekday)
    result_activity = get_activity(weekday)
    dict_result['activity'] = result_activity

    direction_result = direction("center")
    dict_result['direction'] = direction_result
    dict_result['route'] = "center"
    print("".join(direction_result))

    if request.method == 'POST':
        print("POST")
        checkbox_value = request.form.get('checkbox')
        print(request.form)
        print("checkbox_value = ", checkbox_value)
        if checkbox_value == "on":
            direction_result = direction("center")
            dict_result['direction'] = direction_result
            dict_result['route'] = "center"
            print("".join(direction_result))
            return render_template('main.html', dict_result=dict_result)
        else:
            direction_result = direction("")
            dict_result['direction'] = direction_result
            print("".join(direction_result))
            dict_result['route'] = "westwijk"
            return render_template('main.html', dict_result=dict_result)

    if request.method == 'GET':
        print("GET")
        return render_template('main.html', dict_result=dict_result)


if __name__ == '__main__':
    app.run()
