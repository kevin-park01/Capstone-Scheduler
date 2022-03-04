from dataclasses import dataclass, field


# A session represents a meeting or event to be scheduled. Each session should have pre-determined 
# attributes that cannot be left empty because rooms require session attributes to schedule sessions 
# without breaking constraints.
@dataclass
class Session:
    session_id: int                  # Unique session identifier
    duration: int                    # Time in minutes that a session lasts
    est_capcity: int                 # Estimated number of attendees
    title: str                       # Title of session
    format: str                      # Format of session (e.g., roundtable)
    topic: str                       # Topic of session (e.g., "African History")
    equipment: list[str]             # List of equipment needed (e.g., WiFi)
    speaker: list[int]               # List of speaker ID's
    start_time: str = ''             # Time of day that session is scheduled to start (e.g., '9:30')
    end_time: str = ''               # Time of day that session is scheduled to end (e.g., '12:00')


    # Set session start and end time
    def set_time(self, start: str, end: str):
        self.start_time = start
        self.end_time = end


# A room is where sessions will be scheduled in. Each room will contain scheduled sessions
# throughout one or more days. A room should have some pre-determined attributes like capacity
# but also some attributes that will be updated dynamically like equipment since rooms are equipped
# to match the session it is trying to schedule.
@dataclass
class Room:
    room_id: int                                                    # Unique room indentifier
    max_capacity: int                                               # Maximum number of people allowed
    format: str = ""                                                # Format of room (e.g., roundtable)
    equipment: list[str] = field(default_factory=list)              # List of equipment needed (e.g., WiFi)
    schedule: list[list[Session]] = field(default_factory=list)     # List of session lists that represent daily schedules
    slots: int = 0                                                  # Number of slots in a schedule


    # Create a blank schedule with slots in between ROOM_START and ROOM_END 
    def schedule_init(self, num_slots: int):         
        self.schedule += [['_'] * num_slots]
        self.slots = num_slots


    # Set the format of the room
    def set_format(self, format: str):
        self.format = format


    # Add equipment to room
    def add_equipment(self, equipment: list[str]):
        self.equipment.extend(equipment)


    # Check if the session is compatible with this room
    def check_compatible(self, session: Session) -> bool:
        # Check if this room has the equipment needed by the session
        if not set(session.equipment).issubset(self.equipment):
            return False

        # Check if the session's estimated capacity exceeds this room's maximum capacity
        if session.est_capcity > self.max_capacity:
            return False

        # Check if the session's format matches the room's format
        if session.format != self.format:
            return False
        
        return True


    # Add the session to the specified day's schedule
    def add_session(self, session: Session, day: int, start_times: list[str], end_times: list[str], speaker_log, topic_log) -> bool:
        # Check if the session and room are compatible
        if not self.check_compatible(session):
            return False

        sched = self.schedule[day]

        for i in range(len(sched)):
            is_valid = True

            if sched[i] != '_':                                             # Check if the schedule at this index already has a session
                continue
            elif set(speaker_log[day][i]).intersection(session.speaker):    # Check if there is a speaker conflict
                continue
            elif session.topic in topic_log[day][i]:                        # Check if there is a topic conflict
                continue

            # Insert the session if there is enough open space
            session.set_time(start_times[i], end_times[i])
            self.schedule[day][i] = session

            # Update speaker and topic logs
            speaker_log[day][i] = speaker_log[day][i] + session.speaker
            topic_log[day][i] = topic_log[day][i] + [session.topic]
            return True

        return False


    # Print daily schedules for this room
    def print_schedule(self, start_times: list[str], end_times: list[str]):
        print(f'Room {self.room_id} Schedule')
        print(f'   Equipment: {self.equipment}')
        print(f'   Format: {self.format}')
        for i in range(len(self.schedule)):
            print(f'\n   Day {i}:')
            for j in range(len(self.schedule[i])):
                if(self.schedule[i][j] == '_'):
                    print(f'   {start_times[j]} - {end_times[j]}: {self.schedule[i][j]}')
                else:
                    print(f'   {start_times[j]} - {end_times[j]}: {self.schedule[i][j].session_id}')
        print()


# A schedule will contain a list of scheduled rooms and unscheduled sessions. Multiple schedules can 
# be made to contain different sets of rooms and sessions to schedule. If a session can be successfully 
# scheduled into a room, that room will be added to a list of scheduled rooms to be sent to the user. 
# Otherwise, that session will be added to a list of unscheduled sessions and the user can re-schedule 
# it for another day.
@dataclass
class Schedule:
    start_times: list[str]                                            # List of schedule interval start times
    end_times: list[str]                                              # List of schedule interval end times
    days_scheduled: int = 0                                           # Number of days scheduled
    rooms_sched: dict[int, Room] = field(default_factory=dict)        # Maps room ID's to rooms
    sessions_not_sched: list[Session] = field(default_factory=list)   # List of session not able to be scheduled
    speaker_log: list[list[list[str]]] = field(default_factory=list)  # List of speakers in each time slot for each day
    topic_log: list[list[list[str]]] = field(default_factory=list)    # List of topics in each time slot for each day


    # Create a blank log for speaker and topic logs
    def logs_init(self):
        self.topic_log += [[[]] * len(self.start_times)]
        self.speaker_log += [[[]] * len(self.start_times)]


    # Print schedule
    def print_schedule(self):
        for room in self.rooms_sched.values():
            room.print_schedule(self.start_times, self.end_times)


    # Create a schedule for one day. Intended to be called once each day
    def create_day_schedule(self, sessions: list[Session], rooms: list[Room], day: int):
        self.days_scheduled += 1
        self.sessions_not_sched = []
        
        # Initialize logs
        self.logs_init()

        # Initalize room schedules
        for room in rooms:
            room.schedule_init(len(self.start_times))

        # Loop through sessions
        for sess in sessions:
            is_scheduled = False

            for room in rooms:
                if room.room_id not in self.rooms_sched.keys():
                    room.add_equipment(sess.equipment)
                    room.set_format(sess.format)
                    self.rooms_sched[room.room_id] = room

                if self.rooms_sched[room.room_id].add_session(sess, day, self.start_times, self.end_times, self.speaker_log, self.topic_log):
                    is_scheduled = True
                    break
            
            if not is_scheduled:
                self.sessions_not_sched.append(sess)


    # Create multiple day schedules
    def create_schedule(self, sessions: list[Session], rooms: list[Room], num_days: int):
        session_list = sessions
        day = 0

        while day < num_days and len(session_list) > 0:
            self.create_day_schedule(session_list, rooms, day)
            session_list = self.sessions_not_sched
            day += 1

        # Print schedule
        self.print_schedule()
        if len(session_list) > 0:
            print('Could not schedule sessions:')
            for sess in session_list:
                print(sess.session_id)