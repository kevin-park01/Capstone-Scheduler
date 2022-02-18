import schedule
import sessionparser
import RoomParser

def main():

    val = input("Do you want to Parse (Enter 'y' for yes, and 'n' for no): ")

    if val == 'y':
        #print("Parsing")
        sessions = sessionparser.ParseSession()

        rooms = RoomParser.ParseRooms()
    else:

        room1 = schedule.Room(1, 10, 6, 12)
        room2 = schedule.Room(2, 10, 7, 12)

        session1 = schedule.Session(1, 60, 5, 'Intro to CS 1', 'Roundtable', 'CS', ['Mic'], [1])
        session2 = schedule.Session(2, 120, 5, 'Intro to CS 2', 'Panel', 'BS', ['Wifi', 'Mic'], [2])
        session3 = schedule.Session(3, 180, 5, 'Intro to BS 1', 'Panel', 'BS', ['Wifi'], [2])
        session4 = schedule.Session(4, 240, 5, 'Intro to BS 2', 'Roundtable', 'CS', ['Mic'], [1])

        sessions = [session1, session2, session3, session4]
        rooms = [room1, room2]

    day_schedule = schedule.Schedule()
    day_schedule.create_day_schedule(sessions, rooms, 0)
    day_schedule.create_day_schedule(day_schedule.sessions_not_sched, rooms, 1)
    day_schedule.print_schedule()

# Start main function
if __name__ == '__main__':
    main()