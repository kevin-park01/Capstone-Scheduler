import schedule

def main():

    room1 = schedule.Room(1, 10)
    room2 = schedule.Room(2, 10)

    session1 = schedule.Session(1, 60, 5, 'Intro to CS 1', 'Roundtable', 'CS', ['Mic'], [1])
    session2 = schedule.Session(2, 120, 5, 'Intro to CS 2', 'Roundtable', 'CS', ['Mic', 'Wifi'], [1])
    session3 = schedule.Session(3, 180, 5, 'Intro to BS 1', 'Roundtable', 'BS', ['Mic'], [2])
    session4 = schedule.Session(4, 240, 5, 'Intro to BS 2', 'Roundtable', 'BS', ['Wifi'], [2])

    sessions1 = [session1, session2]
    sessions2 = [session3, session4]
    rooms = [room1, room2]

    start_times = ['7:00', '8:30']
    end_times = ['8:15', '9:45']

    day_schedule = schedule.Schedule(start_times, end_times)
    day_schedule.create_schedule(sessions1, rooms, 2)
    day_schedule.create_schedule(sessions2, rooms, 2)

# Start main function
if __name__ == '__main__':
    main()