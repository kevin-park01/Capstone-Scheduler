#include <iostream>
#include <stdexcept>
#include <algorithm>
#include "session.h"
#include "parser.h"

unsigned const int ROOM_START = 6;  // 6 a.m. 24-hour clock 
const double INTERVAL = 15.0;    // minutes
unsigned int BUFFER = 30; // buffer duration in minutes
static Session* buffer1 = new Session(0, BUFFER, 0, "buffer", "", "");  // all buffer 'sessions' are references to this, note that it should have a reserved sessionID

// Check if l1 is a subset of l2
bool checkSubset(list<string> l1, list<string> l2) {
	l1.sort();
	l2.sort();
	for (string s : l1)
	{
		if (find(l2.begin(), l2.end(), s) != l2.end())
		{
			return true;
		}
	}
	return false;
}

// Check if l1 is a subset of l2
bool checkSubset(list<int> l1, list<int> l2) {
	l1.sort();
	l2.sort();
	for (int s : l1)
	{
		if (find(l2.begin(), l2.end(), s) != l2.end())
		{
			return true;
		}
	}
	return false;
}

// Assign session to room schedule
bool assignSession(Session* session, Room* room, unsigned int timeSlots, list<Room*> roomList)
{
	bool timeCompatible = false;
	bool isCompatible = true;
	int currSessionIndex = (int)ceil(60 * (room->startTime - ROOM_START) / INTERVAL);	// Initialize current index to index where room opens
	int leftIndex;

	while (!timeCompatible && currSessionIndex < room->schedule.size())		// Loop through room schedule
	{
		leftIndex = currSessionIndex;
		isCompatible = true;
		
		// Find the earliest interval that fits the session
		while (!timeCompatible && isCompatible && currSessionIndex < room->schedule.size() && room->schedule[currSessionIndex] == nullptr)		
		{
			currSessionIndex++;

			// Check if the interval is long enough to fit the session
			if (currSessionIndex - leftIndex == timeSlots)
			{
				// Check other rooms for overlapping speakers
				for (Room* scheduledRoom : roomList)
				{
					if (!isCompatible) break;

					// Loop through the time slots in each room
					for (int j = leftIndex; j < leftIndex + timeSlots; j++)
					{
						if (!scheduledRoom->schedule[j])	 continue;	// A time slot is available if it is a null pointer					

						// Compare speakers at the same index in two different rooms
						if (checkSubset(session->speaker, scheduledRoom->schedule[j]->speaker) || session->topic == scheduledRoom->schedule[j]->topic)
						{
							isCompatible = false;
							currSessionIndex = leftIndex;
							break;
						}
					}
				}

				if (isCompatible)
				{
					timeCompatible = true;
				}
			}
		}
		currSessionIndex++;
	}

	// If the schedule has an opening for the session to be scheduled and 
	// speakers are not overlapped, then assign the session to appropriate time slots
	if (timeCompatible)
	{
		// if at least one time slot after session and buffer, add buffer	
		int i = leftIndex;
		for (; i < leftIndex + timeSlots; i++)
		{
			room->schedule[i] = session;
		}

		// add buffer after session if not at end of room availability
		int bufferSlots = (int)ceil(BUFFER / INTERVAL);
		if (i + bufferSlots < room->schedule.size())
		{
			for (; i < leftIndex + bufferSlots + timeSlots; i++)
			{
				room->schedule[i] = buffer1;
			}
		}
	}

	return timeCompatible;
}



// Check if a session is compatible to a room
bool checkCompatibility(Session* session, Room* room)
{
	bool equipCompatible = true, capCompatible = true, formatCompatible = true;

	// Check equipment compatability
	if (!checkSubset(session->equipment, room->equipment))
	{
		equipCompatible = false;
	}

	// Check estimated capacity of session doesn't exceed max capacity of room
	if (session->estimatedCapacity > room->maxCapacity)
	{
		capCompatible = false;
	}

	// Check format compatibility
	if (session->format != room->format)
	{
		formatCompatible = false;
	}

	return equipCompatible && capCompatible && formatCompatible;
}


// operator function for std::sort to sort a list of sessions by topic
bool comp_topic(const Session* a, const Session* b)
{
	return a->topic < b->topic;
}


// Schedule sessions into rooms
list<Room*> schedule(list<Session*> *sessionList, list<Room*> emptyRoomList)     
{
	list<Room*> roomList = list<Room*>();      // List containing rooms that have sessions scheduled	
	bool isScheduled = false;
	int timeSlots = 0;

	// *** topic constraint ***
	// sort session list alphabetically by topic, grouping sessions with same topic
	// * may cause more rooms to be used and modified *
	// * sessions will be scheduled in alphabetical order in most cases *
	// * sessions with the same topic may be scheduled at overlapping times in different rooms *
	//list<Session*> sortedSessionList = *sessionList;
	sessionList->sort(comp_topic);

	for (Session* session : *sessionList)
	{
		timeSlots = (int)ceil(session->duration / INTERVAL);  // number of time slots to fill for this session
		for (Room* room : roomList)
		{
			if (checkCompatibility(session, room)) // Check compatability of sessions to rooms
			{
				isScheduled = assignSession(session, room, timeSlots, roomList);	// fill up the time slots
				if (isScheduled)
				{
					sessionList->remove(session);
				}
			}
		}

		if (!isScheduled)					// If an existing room isn't compatible, pull a room from the list of empty rooms 
		{									// and equip it accordingly with the session to schedule		
			if (emptyRoomList.empty())
			{
				continue;
			}

			Room* newRoom = (emptyRoomList).back();
			emptyRoomList.pop_back();
			newRoom->equipment = session->equipment;
			newRoom->format = session->format;

			assignSession(session, newRoom, timeSlots, roomList);	// fill up the time slots
			roomList.push_back(newRoom);
			sessionList->remove(session);
		}
	}
	return roomList;
}


/*  
	Printed Abbreviations
	R  ->  Roundtable
	P  ->  Panel
	bf ->  buffer
*/

// Print each session and equipment needed
void printSessions(list<Session*> sessionList)   
{
	cout << "\nSession Title" << " | " << "Speaker(s)" << " | " << "Format" << " | " << "Slots" << " | " << "Equipment" << endl; 
	cout << "--------------|------------|--------|-------|------------------" << endl;
	for (Session* session : sessionList)
	{
		cout << "      " << session->title << "      |     ";
		for (int speaker : session->speaker)
		{
			cout << speaker << " ";
		}

		cout << "     |   " << session->format << "    |   " << (int)ceil(session->duration / INTERVAL) << "   | ";
		for (string equipment : session->equipment)
		{
			cout << equipment << " ";
		}
		cout << endl;
	}
	cout << endl;
}


// Print each room that has been scheduled and its equipment
void printSchedule(list<Room*> scheduledRooms, int day)  
{
	cout << "Day " << day + 1 << ":" << endl;
	for (Room* room : scheduledRooms)
	{
		cout << "Room " << room->roomId << " opens at " << room->startTime << " ( ";
		for (string equipment : room->equipment)
		{
			cout << equipment << " ";
		}
		cout << ", " << room->format << " ): " << endl;

		int counter = 0;
		for (Session* session : room->schedule)
		{
			if (counter % 4 == 0)
			{
				cout << "|  ";
			}
			counter += 1;

			if (session != nullptr)
			{
				if (session == buffer1)
					cout << "bf  ";
				else
					cout << session->title << "  ";
			}
			else
			{
				cout << "__  ";
			}
		}
		cout << endl;
	}
	cout << endl;
}


// Print all room information
void printRooms(list<Room*> rooms)
{
	for (Room* room : rooms)
	{
		cout << "Room " << room->roomId << " opens at " << room->startTime << " ( ";
		for (string equipment : room->equipment)
		{
			cout << equipment << " ";
		}
		cout << ", " << room->format << " )\n";
	}
	cout << endl;
}


int main()
{
	list<Room*> emptyRoomList;         // List that initially contains every room available to be scheduled
	list<Session*> sessionList;     // List that contains sessions to be scheduled
	string input = "";

	cout << "Enter 'n' to run without parsing or 'y' to run with parsing: ";
	cin >> input;

	if (input == "n")	// run without parsing
	{
		// Empty rooms
		Room* room1day1 = new Room(1, 100, 8, 12, "", list<string>());
		Room* room2day1 = new Room(2, 50, 7, 12, "", list<string>());
		Room* room1day2 = new Room(1, 100, 8, 12, "", list<string>());
		Room* room2day2 = new Room(2, 50, 7, 12, "", list<string>());

		list<Room*> day1RoomList = { room2day1, room1day1 };
		list<Room*> day2RoomList = { room2day2, room1day2 };

		// Sessions to schedule
		Session* session1 = new Session(1, 120, 25, "A1", "R", "A", list<string>{ "Wifi" }, list<int>{ 1 });
		Session* session2 = new Session(2, 30, 20, "B1", "P", "B", list<string>{ "Projector", "Speaker" }, list<int>{ 2 });
		Session* session3 = new Session(3, 45, 20, "C1", "R", "C", list<string>{ "Wifi" }, list<int>{ 2 });
		Session* session4 = new Session(4, 50, 40, "A2", "P", "A", list<string>{ "Projector", "Speaker" }, list<int>{ 2 });
		Session* session5 = new Session(5, 45, 40, "C2", "R", "C", list<string>{ "Wifi" }, list<int>{ 3 });
		Session* session6 = new Session(6, 30, 40, "B2", "R", "B", list<string>{ "Wifi" }, list<int>{ 1 });
		Session* session7 = new Session(7, 120, 25, "A3", "R", "A", list<string>{ "Wifi" }, list<int>{ 1 });
		Session* session8 = new Session(8, 30, 20, "B3", "P", "B", list<string>{ "Projector", "Speaker" }, list<int>{ 2 });
		Session* session9 = new Session(9, 45, 20, "C3", "R", "C", list<string>{ "Wifi" }, list<int>{ 2 });
		Session* session10 = new Session(10, 50, 40, "A4", "P", "A", list<string>{ "Projector", "Speaker" }, list<int>{ 2 });
		Session* session11 = new Session(11, 45, 40, "C4", "R", "C", list<string>{ "Wifi" }, list<int>{ 3 });
		Session* session12 = new Session(12, 30, 40, "B4", "R", "B", list<string>{ "Wifi" }, list<int>{ 1 });

		sessionList = { session1, session2, session3, session4, session5, session6, session12, session11, session10, session9, session8, session7 };
		printSessions(sessionList);

		// Call scheduling algorithm
		list<Room*> scheduledRoomsDay1 = schedule(&sessionList, day1RoomList);
		list<Room*> scheduledRoomsDay2 = schedule(&sessionList, day2RoomList);

		printSchedule(scheduledRoomsDay1, 0);
		printSchedule(scheduledRoomsDay2, 1);

		if (sessionList.size() > 0)
		{
			printSessions(sessionList);
		}
	}

	else if (input == "y")	// run with parsing
	{
		emptyRoomList = ParseRooms();
		sessionList = ParseSession();
		//printRooms(emptyRoomList);

		// Call scheduling algorithm
		list<Room*> scheduledRooms = schedule(&sessionList, emptyRoomList);

		printSessions(sessionList);
		printSchedule(scheduledRooms, 0);
	}

	return 0;
}
