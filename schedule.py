from dataclasses import dataclass, field
import math


# Gloabl constants
ROOM_START = 6      # Earliest time (military time) a room can open
ROOM_END = 12       # Latest time (military time) a room can close
INTERVAL = 30       # Time (minutes) of each schedule slot
BUFFER = 30         # Buffer time (minutes) in between sessions

# Global logs used for constraint checking
speaker_log = []    # Records which speakers will be speaking at indexes of all schedules
topic_log = []      # Records what topics will be presented at indexes of all schedules


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


# A room is where sessions will be scheduled in. Each room will contain scheduled sessions
# throughout one or more days. A room should have some pre-determined attributes like capacity
# but also some attributes that will be updated dynamically like equipment since rooms are equipped
# to match the session it is trying to schedule.
@dataclass
class Room:
    room_id: int                                                    # Unique room indentifier
    max_capacity: int                                               # Maximum number of people allowed
    start_time: int                                                 # When the room opens in military time
    end_time: int                                                   # When the rooms closes in military time
    format: str = ""                                                # Format of room (e.g., roundtable)
    equipment: list[str] = field(default_factory=list)              # List of equipment needed (e.g., WiFi)
    schedule: list[list[Session]] = field(default_factory=list)     # List of session lists that represent daily schedules


    # Create a blank schedule with slots in between ROOM_START and ROOM_END 
    def schedule_init(self): 
        if self.start_time < ROOM_START or self.end_time > ROOM_END:
            print(f'ERROR: Room cannot start before {ROOM_START} or end after {ROOM_END}')
        
        time_slots = math.ceil((60 * (ROOM_END - ROOM_START)) / INTERVAL)
        self.schedule += [['_'] * time_slots]


    # Set the format of the room
    def set_format(self, format: str):
        self.format = format


    # Add equipment to room
    def add_equipment(self, equipment: list[str]):
        self.equipment.extend(equipment)


    # Get the index of when the room opens
    def get_start_index(self) -> int:
        return math.ceil(60 * (self.start_time - ROOM_START) / INTERVAL)


    # Get the index of when the room closes
    def get_end_index(self) -> int:
        return math.ceil(60 * (self.end_time - ROOM_START) / INTERVAL)


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


    # Insert session into the specified interval in the schedule 
    def insert_session(self, session: Session, left_index: int, right_index: int, day: int):
        for i in range(left_index, right_index):
            self.schedule[day][i] = session.session_id


    # Insert buffer into specified interval in the schedule
    def insert_buffer(self, left_index: int, right_index: int, day: int):
        for i in range(left_index, right_index):
            self.schedule[day][i] = 'B'


    # Add the session to the specified day's schedule
    def add_session(self, session: Session, day: int) -> bool:
        # Check if the session and room are compatible
        if not self.check_compatible(session):
            return False

        sched = self.schedule[day]
        left_index = self.get_start_index()
        buffer_slots = math.ceil(BUFFER / INTERVAL)
        slots_needed = math.ceil(session.duration / INTERVAL) + buffer_slots

        for i in range(self.get_start_index(), self.get_end_index()):
            # Check if there is a speaker conflict
            if set(speaker_log[day][i]).intersection(session.speaker):
                left_index = i + 1
                continue

            # Check if there is a topic conflict
            if session.topic in topic_log[day][i]:
                left_index = i + 1
                continue

            # Check if the schedule at this index already has a session or buffer
            if sched[i] != '_':
                left_index = i + 1
                continue
                
            # Insert the session if there is enough open space
            if i - left_index == slots_needed:
                self.insert_session(session, left_index, i - buffer_slots, day)
                self.insert_buffer(i - buffer_slots, i, day) 
                update_logs(session, left_index, i - buffer_slots, day)
                return True
            # Handle edge case where a session is scheduled at the end of a room's schedule
            elif i + 1 == len(self.schedule[day]) and i - left_index + 1 == slots_needed:
                self.insert_session(session, left_index, i + 1, day)
                self.insert_buffer(i - buffer_slots + 1, i + 1, day) 
                update_logs(session, left_index, i + 1, day)
                return True
            # Handle edge case where session can fit without a buffer at the end of a schedule
            elif i + 1 == len(self.schedule[day]) and i - left_index + 1 == slots_needed - buffer_slots:
                self.insert_session(session, left_index, i + 1, day) 
                update_logs(session, left_index, i + 1, day)
                return True

        return False


    # Print daily schedules for this room
    def print_schedule(self):
        print(f'Room {self.room_id} Schedule')
        print(f'   Equipment: {self.equipment}')
        print(f'   Format: {self.format} \n')
        for i in range(len(self.schedule)):
            output = f'   Day {i}:  '
            for session in self.schedule[i]:
                output += str(session) + "  "
            print(output)
        print()


# A schedule will contain a list of scheduled rooms and unscheduled sessions. Multiple schedules can 
# be made to contain different sets of rooms and sessions to schedule. If a session can be successfully 
# scheduled into a room, that room will be added to a list of scheduled rooms to be sent to the user. 
# Otherwise, that session will be added to a list of unscheduled sessions and the user can re-schedule 
# it for another day.
@dataclass
class Schedule:
    rooms_sched: dict[int, Room] = field(default_factory=dict)        # Maps room ID's to rooms
    sessions_not_sched: list[Session] = field(default_factory=list)   # List of session not able to be scheduled
    days_scheduled: int = 0                                           # Number of days scheduled
    

    # Create a schedule for one day. Intended to be called once each day
    def create_day_schedule(self, sessions: list[Session], rooms: list[Room], day: int) -> bool:
        self.days_scheduled += 1
        
        # Initialize logs
        logs_init()

        # Initalize room schedules
        for room in rooms:
            room.schedule_init()

        # Loop through sessions
        for sess in sessions:
            is_scheduled = False

            for room in rooms:
                if room.room_id not in self.rooms_sched.keys():
                    room.add_equipment(sess.equipment)
                    room.set_format(sess.format)
                    self.rooms_sched[room.room_id] = room

                if self.rooms_sched[room.room_id].add_session(sess, day):
                    is_scheduled = True
                    break
            
            if not is_scheduled:
                self.sessions_not_sched.append(sess)

        if len(self.sessions_not_sched) > 0:
            return False

        return True


    # Print schedule
    def print_schedule(self):
        for room in self.rooms_sched.values():
            room.print_schedule()


# Create a blank log for speaker and topic logs
def logs_init():
    global topic_log
    global speaker_log
    topic_log += [[[]] * (math.ceil((60 * (ROOM_END - ROOM_START)) / INTERVAL) + 1)]
    speaker_log += [[[]] * (math.ceil((60 * (ROOM_END - ROOM_START)) / INTERVAL) + 1)]


# Update speaker and topic logs
def update_logs(session: Session, left_index: int, right_index: int, day: int):
    for i in range(left_index, right_index):
        speaker_log[day][i] = speaker_log[day][i] + session.speaker
        topic_log[day][i] = topic_log[day][i] + [session.topic]