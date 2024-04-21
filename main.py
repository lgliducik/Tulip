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
from bson import ObjectId


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
    monday = StringField('monday')
    tuesday = StringField('tuesday')
    wednesday = StringField('wednesday')
    thursday = StringField('thursday')
    friday = StringField('friday')
    saturday = StringField('saturday')
    sunday = StringField('sunday')


@app.route('/update/', methods=['GET', 'POST'])
def update():
    form = ScheduleForm()

    if request.method == 'POST' and form.validate():

        monday = form.monday.data
        tuesday = form.tuesday.data
        wednesday = form.wednesday.data
        thursday = form.thursday.data
        friday = form.friday.data
        saturday = form.saturday.data
        sunday = form.sunday.data
        print(sunday)
        print(sunday.split(", "))

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
    if request.method == 'GET':
        form = ScheduleForm()
        form.monday.process_data("".join(mycol.find_one({"day": "monday"})["activity"]))
        form.tuesday.process_data("".join(mycol.find_one({"day": "tuesday"})["activity"]))
        form.wednesday.process_data("".join(mycol.find_one({"day": "wednesday"})["activity"]))
        form.thursday.process_data("".join(mycol.find_one({"day": "thursday"})["activity"]))
        form.friday.process_data("".join(mycol.find_one({"day": "friday"})["activity"]))
        form.saturday.process_data("".join(mycol.find_one({"day": "saturday"})["activity"]))
        form.sunday.process_data("".join(mycol.find_one({"day": "sunday"})["activity"]))

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


@app.route('/update_task', methods=['POST'])
def update_task():
    task_id = request.json['params']['task_id']
    print(task_id)
    status = todotable.find_one({"_id": ObjectId(task_id)})["status"]
    print(status)
    print(not status)

    filter_id = {'_id': ObjectId(task_id)}
    new_values = {"$set": {'status': int(not status)}}
    print(new_values)
    todotable.update_one(filter_id, new_values)
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
def home_page():
    dict_result = {}

    tasks = [{'task_name': i.get('task_name'), 'status': i.get('status'), 'id': i['_id']} for i in todotable.find()]
    print(tasks)
    dict_result['tasks'] = tasks

    weather = get_buienradar_weather()
    dict_result['weather'] = weather

    weekday = datetime.today().weekday()
    print(weekday)
    result_activity = get_activity(weekday)
    dict_result['activity'] = result_activity

    direction_result = direction("center")
    dict_result['direction_center'] = direction_result
    print("".join(direction_result))

    direction_result = direction("")
    dict_result['direction_westwijk'] = direction_result
    print("".join(direction_result))
    print("".join(direction_result))

    if request.method == 'POST':
        print(request.form)

        new_task = request.form.get('texttodo')
        if new_task:
            if add_new_task_to_db(new_task):
                dict_result["status_todo"] = "Задача добавлена"

        return render_template('main.html', dict_result=dict_result)

    if request.method == 'GET':
        print("GET")
        return render_template('main.html', dict_result=dict_result)


if __name__ == '__main__':
    app.run()
