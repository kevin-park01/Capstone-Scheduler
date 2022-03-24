import schedule
from flask import Flask, render_template
from datetime import datetime


room1 = schedule.Room(1, 10)
room2 = schedule.Room(2, 10)

session1 = schedule.Session(1, 75, 5, 'Intro to CS 1', 'Roundtable', 'CS', 'Social Event', ['Mic'], [1])
session2 = schedule.Session(2, 75, 5, 'Intro to CS 2', 'Roundtable', 'CS', 'Social Event', ['Mic', 'Wifi'], [1])
session3 = schedule.Session(3, 75, 5, 'Intro to BS 1', 'Roundtable', 'BS', 'Social Event', ['Mic'], [2])
session4 = schedule.Session(4, 75, 5, 'Intro to BS 2', 'Roundtable', 'BS', 'Social Event', ['Wifi'], [2])
session5 = schedule.Session(5, 75, 5, 'Intro to ENG 1', 'Roundtable', 'BS', 'Social Event', ['Wifi'], [2])
session6 = schedule.Session(6, 75, 5, 'Intro to ENG 2', 'Roundtable', 'BS', 'Social Event', ['Wifi'], [2])

sessions = [session1, session2, session3, session4, session5, session6]
rooms = [room1, room2]

year = datetime.now().year
month = datetime.now().month
start_times = [datetime(year, month, 1, 7, 0), datetime(year, month, 1, 8, 30)]
end_times = [datetime(year, month, 1, 8, 15), datetime(year, month, 1, 9, 45)]

day_schedule = schedule.Schedule(start_times, end_times)
selected_sessions = sessions


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', sessions=sessions)


@app.route('/schedule')
def create_schedule():
    day_schedule.create_schedule(selected_sessions, rooms, 2)
    sessions_sched = day_schedule.get_scheduled_sessions()
    return render_template('schedule.html', schedule=sessions_sched)


# Start main function
if __name__ == '__main__':
    app.run(debug=True)