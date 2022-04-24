from dataclasses import dataclass, field
from datetime import datetime
from operator import attrgetter
import sys


# A speaker is someone who will be assigned to one or more sessions to present.
@dataclass
class Speaker:
    speaker_id: int                 # Unique speaker identifer
    first_name: str                 # First name of speaker
    last_initial: str               # Last inital of speaker
    session_ids: list[int]          # ID of session the speaker is assigned to


# A session represents a meeting or event to be scheduled. Each session should have pre-determined 
# attributes that cannot be left empty because rooms require session attributes to schedule sessions 
# without breaking constraints.
@dataclass
class Session:
    session_id: int                      # Unique session identifier
    duration: int                        # Time in minutes that a session lasts
    est_capacity: int                     # Estimated number of attendees
    title: str                           # Title of session
    format: str                          # Format of session (e.g., roundtable)
    topic: str                           # Topic of session (e.g., "African History")
    type: str                            # Type of the session (e.g., Social Event)
    sponsors: list[str]                  # List of sponsors, including co-sponsors
    equipment: list[str]                 # List of equipment needed (e.g., WiFi)
    speaker: list[int]                   # List of speaker ID's
    assigned_room: int = 0               # Room ID that the session is scheduled into
    start_time: datetime = datetime(1, 1, 1)    # Time of day that session is scheduled to start
    end_time: datetime = datetime(1, 1, 1)      # Time of day that session is scheduled to end


    # Set session start and end time
    def set_time(self, start: datetime, end: datetime, day: datetime):
        self.start_time = datetime(day.year, day.month, day.day, start.hour, start.minute)
        self.end_time = datetime(day.year, day.month, day.day, end.hour, end.minute)

    
    # Set scheduled room ID
    def set_room(self, room_id: int):
        self.assigned_room = room_id


# A room is where sessions will be scheduled in. Each room will contain scheduled sessions
# throughout one or more days. A room should have some pre-determined attributes like capacity
# but also some attributes that will be updated dynamically like equipment since rooms are equipped
# to match the session it is trying to schedule.
@dataclass
class Room:
    room_id: int                                                    # Unique room indentifier
    max_capacity: int                                               # Maximum number of people allowed
    name: str                                                       # Name of the room
    property: str                                                   # Property the room is located in
    floor: int                                                      # Floor number the room is on
    format: str = ""                                                # Format of room (e.g., roundtable)
    equipment: list[str] = field(default_factory=list)              # List of equipment needed (e.g., WiFi)
    schedule: list[list[Session]] = field(default_factory=list)     # List of session lists that represent daily schedules
    slots: int = 0                                                  # Number of slots in a schedule


    # Create a blank schedule with slots in between ROOM_START and ROOM_END 
    def schedule_init(self, num_slots: int, start_times: list[datetime], end_times: list[datetime], day: datetime):   
        empty_list = []

        for slot_index in range(num_slots):
            empty_slot = Session(-1, 0, 0, 'Emtpy', 'Empty', 'Empty', 'Empty', [], [], [])
            empty_slot.set_time(start_times[slot_index], end_times[slot_index], day)
            empty_list.append(empty_slot)

        self.schedule += [empty_list]
        self.slots = num_slots


    # Add equipment to room
    def add_equipment(self, equipment: list[str]):
        self.equipment.extend(equipment)


    # Check if the session is compatible with this room
    def check_compatible(self, session: Session) -> bool:
        # Check if this room has the equipment needed by the session
        if session.equipment != [''] and self.equipment != [] and not set(session.equipment).issubset(self.equipment):
            return False

        # Check if the session's estimated capacity exceeds this room's maximum capacity
        if session.est_capacity > self.max_capacity:
            return False
        
        return True


    # Add the session to the specified day's schedule
    def add_session(self, session: Session, day_index: int, day: datetime, slots: list[int], start_times: list[datetime], end_times: list[datetime], speaker_log, topic_log, sponsor_log) -> bool:
        # Check if the session and room are compatible
        if not self.check_compatible(session):
            return False

        sched = self.schedule[day_index]

        for i in slots:
            is_valid = True
            slot_duration = (end_times[i] - start_times[i]).total_seconds() / 60.0

            if sched[i].session_id != -1:                                         # Check if the schedule at this index already has a session
                continue
            elif session.duration > slot_duration:                                # Check if session duration exceeds slot duration
                continue
            elif set(speaker_log[day_index][i]).intersection(session.speaker):    # Check if there is a speaker conflict
                continue
            elif session.topic in topic_log[day_index][i]:                        # Check if there is a topic conflict
                continue
            elif session.sponsors != [''] and set(session.sponsors).intersection(sponsor_log[day_index][i]):   # Check if there is a sponsor conflict
                continue

            # Insert the session if there is enough open space
            session.set_time(start_times[i], end_times[i], day)
            session.set_room(self.room_id)
            self.schedule[day_index][i] = session
            
            if self.equipment == [] and session.equipment != ['']:
                self.add_equipment(session.equipment)

            # Update speaker and topic logs
            speaker_log[day_index][i] = speaker_log[day_index][i] + session.speaker
            topic_log[day_index][i] = topic_log[day_index][i] + [session.topic]
            sponsor_log[day_index][i] = sponsor_log[day_index][i] + session.sponsors
            return True

        return False


    # Print daily schedules for this room
    def print_schedule(self, start_times: list[datetime], end_times: list[datetime], days: list[datetime]):
        print(f'Room {self.room_id} Schedule')
        print(f'   Equipment: {self.equipment}')
        print(f'   Format: {self.format}')
        for i in range(len(days)):
            print(f'\n   Day {days[i].date()}:')
            for j in range(len(self.schedule[i])):
                if(self.schedule[i][j].session_id == -1):
                    print(f'   {start_times[j].time()} - {end_times[j].time()}:')
                else:
                    print(f'   {start_times[j].time()} - {end_times[j].time()}: {self.schedule[i][j].session_id}')
        print()


# A schedule will contain a list of scheduled rooms and unscheduled sessions. Multiple schedules can 
# be made to contain different sets of rooms and sessions to schedule. If a session can be successfully 
# scheduled into a room, that room will be added to a list of scheduled rooms to be sent to the user. 
# Otherwise, that session will be added to a list of unscheduled sessions and the user can re-schedule 
# it for another day.
@dataclass
class Schedule:
    start_times: list[datetime]                                           # List of schedule interval start times
    end_times: list[datetime]                                             # List of schedule interval end times
    days: list[datetime]                                                  # List of all days
    all_sessions: list[Session]                                           # List of all sessions
    all_rooms: list[Room]                                                 # List of all rooms
    speakers: list[Speaker]                                               # List of all speakers
    days_scheduled: int = 0                                               # Number of days scheduled
    rooms_sched: dict[int, Room] = field(default_factory=dict)            # Maps room ID's to rooms
    sessions_scheduled: list[Session] = field(default_factory=list)       # List of scheduled sessions
    sessions_not_scheduled: list[Session] = field(default_factory=list)   # List of session not able to be scheduled
    speaker_log: list[list[list[str]]] = field(default_factory=list)      # List of speakers in each time slot for each day
    topic_log: list[list[list[str]]] = field(default_factory=list)        # List of topics in each time slot for each day
    sponsor_log: list[list[list[str]]] = field(default_factory=list)     # List of sponsors and cosponsors in each time slot for each day


    # Create a blank log for speaker and topic logs
    def logs_init(self):
        self.topic_log += [[[]] * len(self.start_times)]
        self.speaker_log += [[[]] * len(self.start_times)]
        self.sponsor_log += [[[]] * len(self.start_times)]


    def init(self):
        for i in range(len(self.days)):
            # Initialize logs
            self.logs_init()

            # Initalize room schedules
            for room in self.all_rooms:
                room.schedule_init(len(self.start_times), self.start_times, self.end_times, self.days[i])


    # Print schedule
    def print_schedule(self):
        for room in self.rooms_sched.values():
            room.print_schedule(self.start_times, self.end_times, self.days)
        
        print(f'Successfully scheduled {len(self.sessions_scheduled)} out of {len(self.all_sessions)} sessions.')

    
    # Get speaker object given the speaker's ID
    def get_speaker(self, id: int) -> Speaker:
        for speaker in self.speakers:
            if speaker.speaker_id == id:
                return speaker
        
        return None


    # Return scheduled sessions in a list
    def get_scheduled_sessions(self) -> list[Session]:
        return self.sessions_scheduled


    # Return unscheduled sessions in a list
    def get_unscheduled_sessions(self) -> list[Session]:
        if len(self.sessions_scheduled) == 0:
            return self.all_sessions

        unscheduled = []
        for sess in self.all_sessions:
            unscheduled.append(sess)
            for sched_sess in self.sessions_scheduled:
                if sess.session_id == sched_sess.session_id:
                    unscheduled.remove(sess)
                    break

        return unscheduled


    # Return a set of session formats needed by sessions that haven't been schedule yet
    def get_session_formats(self) -> set[str]:
        formats = set()

        for sess in self.get_unscheduled_sessions():
            if sess.format != "":
                formats.add(sess.format)

        return formats

    
    # Return a set of room formats from all rooms
    def get_room_formats(self) -> set[str]:
        formats = set()

        for room in self.all_rooms:
            if room.format != "":
                formats.add(room.format)

        return formats

    
    # Return a set of all equipment from all rooms
    def get_room_equipment(self) -> set[str]:
        equipment = set()

        for room in self.all_rooms:
            if room.equipment != [""]:
                equipment.update(room.equipment)
        
        return equipment


    # Return a set of all properties from all rooms
    def get_room_properties(self) -> set[str]:
        properties = set()

        for room in self.all_rooms:
            if room.property != "":
                properties.add(room.property)

        return properties


    # Return a set of session topics
    def get_session_topics(self) -> set[str]:
        topics = set()

        for sess in self.get_unscheduled_sessions():
            if sess.topic != "":
                topics.add(sess.topic)

        return topics


    # Return a set of session types
    def get_session_types(self) -> set[str]:
        types = set()

        for sess in self.get_unscheduled_sessions():
            if sess.type != "":
                types.add(sess.type)

        return types


    # Return a set of sponsors
    def get_session_sponsors(self) -> set[str]:
        sponsors = set()

        for sess in self.get_unscheduled_sessions():
            if sess.sponsors != [""]:
                sponsors.update(sess.sponsors)

        return sponsors


    # Returns the max capacity of all rooms
    def get_room_max_capacity(self) -> int:
        max = 0

        for room in self.all_rooms:
            if room.max_capacity > max:
                max = room.max_capacity
        
        return max


    # Returns the smallest capacity of selected sessions
    def get_session_min_capacity(self, selected_sessions: list[Session]) -> int:
        min = sys.maxsize

        for session in selected_sessions:
            if session.est_capacity < min:
                min = session.est_capacity

        return min


    # Get index of slot in start_times list
    def get_slot_index(self, time: datetime) -> int:
        time_index = -1
        
        for i in range(len(self.start_times)):
            if self.start_times[i].time() == time.time():
                time_index = i
        
        return time_index


    # Get index of days in days list
    def get_day_index(self, day: datetime):
        day_index = -1

        for i in range(len(self.days)):
            if self.days[i].date() == day.date():
                day_index = i
        
        return day_index


    # Get list of sessions that match filters
    def get_filtered_sessions(self, types: list[str], formats: list[str], sponsors: list[str], topics: list[str]):
        compatible_sessions = []
        
        for session in self.get_unscheduled_sessions():
            if len(types) > 0 and session.type not in types:
                continue
            elif len(formats) > 0 and session.format not in formats:
                continue
            elif len(sponsors) > 0 and not set(session.sponsors).issubset(sponsors):
                continue
            elif len(topics) > 0 and session.topic not in topics:
                continue

            compatible_sessions.append(session)

        return compatible_sessions


    # Get list of rooms that match filters and the number of available slots of specified days and times
    def get_filtered_room_availability(self, days: list[datetime], times: list[datetime], properties: list[str], equipment: list[str], capacity: int, formats: list[str], selected_sessions: list[Session]) -> list[tuple()]:
        compatible_rooms = []
        min_capacity = self.get_session_min_capacity(selected_sessions)
       
        
        for room in self.all_rooms:
            num_available = 0

            for day in days:
                day_index = self.get_day_index(day)

                for time in times:
                    slot_index = self.get_slot_index(time)

                    if len(equipment) > 0 and not set(room.equipment).issubset(equipment):      # Check if this room's equipment is a subset of the filtered equipment
                        continue
                    elif not capacity == None and room.max_capacity > capacity:                 # Check if room's capacity exceeds the filtered capacity
                        continue
                    elif room.max_capacity < min_capacity:                                      # Check if room's capacity is less than the minimum capacity of selected sessions
                        continue
                    elif len(formats) > 0 and not room.format in formats:                       # Check if the room's format is in the list of filtered formats
                        continue
                    elif len(properties) > 0 and not room.property in properties:               # Check if the room's property is in the list of filtered properties
                        continue

                    if room.schedule[day_index][slot_index].session_id == -1:
                        num_available += 1

            if num_available != 0:
                compatible_rooms.append((room, num_available))

        return compatible_rooms


    # Create a schedule for one day. Intended to be called once each day
    def create_day_schedule(self, sessions: list[Session], rooms: list[Room], day_index: int, day: datetime, slots: list[datetime]):
        self.days_scheduled += 1
        self.sessions_not_scheduled = []

        # Sort sessions by capacity in descending order
        sessions.sort(key=lambda x: x.est_capacity, reverse=True)

        # Loop through sessions
        for sess in sessions:
            is_scheduled = False

            for room in rooms:
                if room.room_id not in self.rooms_sched.keys():
                    self.rooms_sched[room.room_id] = room

                if self.rooms_sched[room.room_id].add_session(sess, day_index, day, slots, self.start_times, self.end_times, self.speaker_log, self.topic_log, self.sponsor_log):
                    is_scheduled = True
                    self.sessions_scheduled.append(sess)
                    break
            
            if not is_scheduled:
                self.sessions_not_scheduled.append(sess)


    # Create multiple day schedules. Requires a list of indexes matching the selected indexes of the days list.
    def create_schedule(self, sessions: list[Session], rooms: list[Room], days: list[datetime], times: list[datetime]):
        session_list = sessions
        slot_indexes = []
        i = 0

        for time in times:
            slot_indexes.append(self.get_slot_index(time))

        while i < len(days) and len(session_list) > 0:
            day_index = self.get_day_index(days[i])

            self.create_day_schedule(session_list, rooms, day_index, days[i], slot_indexes)
            session_list = self.sessions_not_scheduled
            i += 1