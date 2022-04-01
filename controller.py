import schedule
from flask import Flask, render_template
from datetime import datetime


room1 = schedule.Room(1, 10, 'Room 1', 'WSCC', 1)
room2 = schedule.Room(2, 10, 'Room 2', 'WSCC', 1)

session1 = schedule.Session(1, 75, 5, 'Intro to CS 1', 'Roundtable', 'CS', 'Social Event', ['ASU'],['Mic'], [1])
session2 = schedule.Session(2, 75, 5, 'Intro to CS 2', 'Lecture', 'CS', 'Social Event', ['ASU'], ['Mic', 'Wifi'], [1])
session3 = schedule.Session(3, 75, 5, 'Intro to BS 1', 'Roundtable', 'BS', 'Social Event', ['Fulton'], ['Mic'], [2])
session4 = schedule.Session(4, 75, 5, 'Intro to BS 2', 'Lecture', 'BS', 'Social Event', ['Fulton'], ['Wifi'], [2])
session5 = schedule.Session(5, 75, 5, 'Intro to ENG 1', 'Lecture', 'BS', 'Social Event', ['Arts'], ['Wifi'], [2])
session6 = schedule.Session(6, 75, 5, 'Intro to ENG 2', 'Lecture', 'BS', 'Social Event', ['Arts'], ['Wifi' ], [2])

speaker1 = schedule.Speaker(1, 'Bob', 'B', [1, 2])
speaker2 = schedule.Speaker(1, 'Maria', 'M', [3, 4, 5, 6])

sessions = [session1, session2, session3, session4, session5, session6]
rooms = [room1, room2]
speakers = [speaker1, speaker2]


year = datetime.now().year
month = datetime.now().month
start_times = [datetime(1, 1, 1, 7, 0), datetime(1, 1, 1, 8, 30)]
end_times = [datetime(1, 1, 1, 8, 15), datetime(1, 1, 1, 9, 45)]
days = [datetime(year, month, 13), datetime(year, month, 14), datetime(year, month, 15), datetime(year, month, 16)]


day_schedule = schedule.Schedule(start_times, end_times, sessions, rooms, days, speakers)
day_schedule.init()


app = Flask(__name__)

@app.route('/')
def home():
    # Get sessions that match filters
    filter_types = ['Social Event']
    filter_formats = ['Roundtable', 'Lecture']
    filter_sponsors = ['ASU', 'Fulton', 'Arts']
    filter_topics = ['CS', 'BS']
    results = day_schedule.get_filtered_sessions(filter_types, filter_formats, filter_sponsors, filter_topics)

    print('Formats:')
    for format in day_schedule.get_room_formats():
        print(format)
    print()

    print('Topics:')
    for topic in day_schedule.get_session_topics():
        print(topic)
    print()

    print('Types:')
    for type in day_schedule.get_session_types():
        print(type)
    print()

    print('Sponsors:')
    for sponsor in day_schedule.get_session_sponsors():
        print(sponsor)
    print()

    return render_template('home.html', sessions=results)


@app.route('/schedule')
def create_schedule():
    selected_sessions = sessions
    selected_rooms = rooms
    selected_days = days
    selected_times = start_times

    day_schedule.create_schedule(selected_sessions, selected_rooms, selected_days, selected_times)
    sessions_sched = day_schedule.get_scheduled_sessions()

    day_schedule.print_schedule()

    # Get rooms that match filters and number of available slots for the filtered days and slots
    filter_days = [days[0], days[1], days[2], days[3]]
    filter_times = [start_times[0], start_times[1]]
    for results in day_schedule.get_filtered_room_availability(filter_days, filter_times, ['Mic', 'Wifi'], 100, ['Roundtable', 'Lecture']):
        print(f'Room {results[0].room_id} has {results[1]} slots')

    return render_template('schedule.html', schedule=sessions_sched)


# Start main function
if __name__ == '__main__':
    app.run(debug=True)