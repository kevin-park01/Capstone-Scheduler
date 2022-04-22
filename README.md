# Capstone-Scheduler
# Natalie Moes, Frank Armijo, Junghwan Park

This application includes a scheduling algorithm follows several constraints and a user interface that enables user interaction 
with the algorithm. While this algorithm is not a fully autonomous scheduler, it can schedule a majority of sessions such that 
the planner only needs to manually schedule a small portion of sessions. The application uses a parser takes in five CSV files 
that inform the algorithm of data regarding sessions, rooms, speakers, times, and days. The parser can also handle requests to 
export generated schedules as a CSV file.

The format for input CSV are as follows:
- Room CSV: Room ID, Room Format,  Property , Room Name, Capacity of the Room, Floor of the property
    - Example: [1,Theater,Sheraton,Room A,100,1]
- Session CSV: Session ID, Session Title, Format, Type, Estimated Seating, Topic, Sponsor (can be empty), Cosponsor (can be empty), 
Duration of the Session, Speaker ID (can be a list), Equipment Request (can be empty or a list)
    - Exmaple: [1234,Introduction to Scheduling,Roundtable,Forum Session,50,Scheduling and Algorithms,ASU,,75,1,Projector]
- Time CSV: Start Times, End Times
    - Example: [8:30,9:45]
- Date CSV: Dates 
    - Example: [1/1/22]

The main constraints that the algorithm follows include:
- Speaker Overlap: There should be no speaker overlap where a speaker is scheduled to be at two or more sessions at the same time.
- Topic Overlap: There should be no topic overlap where two or more sessions with the same topic are scheduled at the same time. 
This enables participants who are interested in a specific topic to attend all sessions on that topic.
- Sponsor Overlap: Each session has a sponsor that is the organizer for the session. To enable participants to attend sessions of 
a specific sponsor or organization, there should be no sponsor overlap where two or more sessions with the same sponsor are 
scheduled at the same time.
- Buffer Customization: The user should be able to specify if there are buffers in between sessions or not. The algorithm must 
recognize these buffers and not schedule sessions during those times.
- Equipment Compatibility: Some sessions will require specific equipment such as internet access or speakers, so rooms must be 
adequately equipped to host these sessions. Rooms do not have equipment by default so the algorithm must be able to equip rooms as 
needed while minimizing the equipment needed in all rooms.
- Multiple-Day Scheduling: Conferences often span several days. Therefore, the algorithm should be able to schedule across several days