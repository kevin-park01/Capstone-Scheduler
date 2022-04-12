import schedule
from flask import Flask, render_template
from datetime import datetime
import parse


# 1. Include Parsing Here
# 2. Call functions to get lists for all start times, end times, days, sessions, rooms, speakers
# 3. Create Schedule object
# 4. Call 'init' function for object

speakers = parse.parseSpeakers('speaker.csv')
sessions = parse.parseSession('session.csv')
rooms = parse.parseRooms('rooms.csv')
days = parse.parseDays('Date.csv')
start_times, end_times = parse.parseTime('time.csv')
day_schedule = schedule.Schedule(start_times, end_times, days, sessions, rooms, speakers)
day_schedule.init()


app = Flask(__name__)

@app.route('/')
def home():
    # Get sessions that match filters
    filter_types = day_schedule.get_session_types()
    filter_formats = day_schedule.get_session_formats()
    filter_sponsors = day_schedule.get_session_sponsors()
    filter_topics = day_schedule.get_session_topics()
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
    filter_days = day_schedule.days
    filter_times = day_schedule.start_times

    for room, num_available in day_schedule.get_filtered_room_availability(filter_days, filter_times, ['Mic', 'Wifi'], 100, ['Roundtable', 'Lecture'], selected_sessions):
        print(f'Room {room.room_id} has {num_available} slots')

    parse.generatedCSV(sessions_sched)

    return render_template('schedule.html', schedule=sessions_sched)


# Start main function
if __name__ == '__main__':
    app.run(debug=True)

