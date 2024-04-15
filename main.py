from flask import Flask, request, render_template, redirect
import googlemaps
from weather import get_buienradar_weather
from datetime import datetime
from database import mycol
from database import todotable
import os
from dotenv import load_dotenv
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField


app = Flask(__name__)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

api_key = os.environ.get('API_KEY')

# Initialize the client with your API key
gmaps = googlemaps.Client(key=api_key)

secret_key = os.environ.get('SECRET_KEY')
app.config['SECRET_KEY'] = secret_key
csrf = CSRFProtect(app)


class ScheduleForm(FlaskForm):
    monday = StringField('monday', default="".join(mycol.find_one({"day": "monday"})["activity"]))
    tuesday = StringField('tuesday', default="".join(mycol.find_one({"day": "tuesday"})["activity"]))
    wednesday = StringField('wednesday', default="".join(mycol.find_one({"day": "wednesday"})["activity"]))
    thursday = StringField('thursday', default="".join(mycol.find_one({"day": "thursday"})["activity"]))
    friday = StringField('friday', default="".join(mycol.find_one({"day": "friday"})["activity"]))
    saturday = StringField('saturday', default="".join(mycol.find_one({"day": "saturday"})["activity"]))
    sunday = StringField('sunday', default="".join(mycol.find_one({"day": "sunday"})["activity"]))


@app.route('/update/', methods=['GET', 'POST'])
def update():
    form = ScheduleForm()

    print(form.monday)
    if request.method == 'POST' and form.validate():

        monday = form.monday.data
        tuesday = form.tuesday.data
        wednesday = form.wednesday.data
        thursday = form.thursday.data
        friday = form.friday.data
        saturday = form.saturday.data
        sunday = form.sunday.data

        mydict = [{"day": "monday", "activity": monday.split(", ")},
                  {"day": "tuesday", "activity": tuesday.split(", ")},
                  {"day": "wednesday", "activity": wednesday.split(", ")},
                  {"day": "thursday", "activity": thursday.split(", ")},
                  {"day": "friday", "activity": friday.split(", ")},
                  {"day": "saturday", "activity": saturday.split(", ")},
                  {"day": "sunday", "activity": sunday.split(", ")}]

        for day in mydict:
            weekday = {'day': day["day"]}
            new_values = {"$set": {'activity': day["activity"]}}
            print(new_values)
            mycol.update_one(weekday, new_values)

        return redirect("/")

    return render_template('change_schedule.html', form=form)


def get_dict_trams(directions_res):
    dict_trams = {}
    for route in directions_res[0]['legs']:
        print(route)
        # print(route.get('steps')[0])
        dict_trams[route.get('steps')[1]['transit_details']['line']['short_name']] = route['departure_time']['text']
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
    elif weekday == 2:
        result = mycol.find_one({"day": "wednesday"})
    elif weekday == 3:
        result = mycol.find_one({"day": "thursday"})
    elif weekday == 4:
        result = mycol.find_one({"day": "friday"})
    elif weekday == 5:
        result = mycol.find_one({"day": "saturday"})
    elif weekday == 6:
        result = mycol.find_one({"day": "sunday"})
    return result


def add_new_task_to_db(task):
    new_task = {'task_name': task, 'status': 0}
    todotable.insert_one(new_task)
    return True


@app.route('/', methods=['GET', 'POST'])
def home_page():
    dict_result = {}

    tasks = [{'task_name': i.get('task_name'), 'status': i.get('status')} for i in todotable.find()]
    print(tasks)
    dict_result['tasks'] = tasks

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
        checkbox_value = request.form.get('checkbox')

        new_task = request.form.get('texttodo')
        if new_task:
            if add_new_task_to_db(new_task):
                dict_result["status_todo"] = "Задача добавлена"

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
