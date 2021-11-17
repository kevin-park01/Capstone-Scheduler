#include <iostream>
#include <stdexcept>
#include "session.h"

unsigned const int ROOM_START = 6;  // 6 a.m. 24-hour clock 
const double INTERVAL = 15.0;    // minutes
unsigned int BUFFER = 30; // buffer duration in minutes
static Session* buffer = new Session(0, BUFFER, 0);  // all buffer 'sessions' are references to this, note that it should have a reserved sessionID


bool assignSession(Session* session, Room* room, int timeSlots, list<Room*> roomList)
{
	bool timeCompatible = false, speakerCompatible = true;
	int currSessionIndex = (int)ceil(60 * (room->startTime - ROOM_START) / INTERVAL);		// Initialize current index to index where room opens
	int leftIndex;

	session->speaker.sort();
	while (!timeCompatible && currSessionIndex < room->schedule.size())		// Loop through room schedule
	{
		leftIndex = currSessionIndex;
		speakerCompatible = true;
		while (!timeCompatible && speakerCompatible && currSessionIndex < room->schedule.size() && room->schedule.at(currSessionIndex) == nullptr)		// Find the earliest interval that fits the session
		{
			currSessionIndex++;
			// Check if the interval is long enough to fit the session
			if (currSessionIndex - leftIndex == timeSlots)
			{
				// Check other rooms for overlapping speakers
				for (Room* scheduledRoom : roomList)
				{
					if (!speakerCompatible)
					{
						break;
					}

					// Loop through the time slots in each room
					for (int j = leftIndex; j < leftIndex + timeSlots; j++)
					{
						// A time slot is available if it is a null pointer
						if (!scheduledRoom->schedule.at(j))
						{
							continue;
						}

						// Compare speakers at the same index in two different rooms
						scheduledRoom->schedule.at(j)->speaker.sort();
						if (session->speaker == scheduledRoom->schedule.at(j)->speaker)
						{
							speakerCompatible = false;
							currSessionIndex = leftIndex;
							break;
						}
					}
				}

				if (speakerCompatible)
				{
					timeCompatible = true;
				}
			}
		}
		currSessionIndex++;
	}

	// If the schedule has an opening for the session to be scheduled and speakers are not overlapped, then assign the session to appropriate time slots
	if (timeCompatible)
	{
		int i = leftIndex;
		for (; i < leftIndex + timeSlots; i++)
		{
			room->schedule.at(i) = session;
		}

		// if at least one time slot after session and buffer, add buffer
		int buffer_slots = (int)ceil(BUFFER / INTERVAL);
		if (i + buffer_slots + 1 < room->schedule.size()) 
		{
			for (; i < leftIndex + buffer_slots; i++)
			{
				room->schedule.at(i) = buffer;
			}
		}
	}

	return timeCompatible;
}

bool checkCompatibility(Session* session, Room* room)
{
	bool equipCompatible = true, capCompatible = true;

	// Check equipment compatability
	session->equipment.sort();
	room->equipment.sort();
	if (session->equipment != room->equipment)
	{
		equipCompatible = false;
	}

	// Check estimated capacity of session doesn't exceed max capacity of room
	if (session->estimatedCapacity > room->maxCapacity)
	{
		capCompatible = false;
	}

	return equipCompatible && capCompatible;
}

list<Room*> schedule(list<Session*> sessionList, list<Room*> emptyRoomList)     // Schedule sessions into rooms
{
	list<Room*> roomList = list<Room*>();      // List containing rooms that have sessions scheduled	
	bool isScheduled = false;
	int timeSlots = 0;

	for (Session* session : sessionList)
	{
		timeSlots = (int)ceil(session->duration / INTERVAL);  // number of time slots to fill for this session
		for (Room* room : roomList)
		{
			if (checkCompatibility(session, room)) // Check compatability of sessions to rooms
			{
				isScheduled = assignSession(session, room, timeSlots, roomList);	// fill up the time slots
			}
		}

		if (!isScheduled)					// If an existing room isn't compatible, pull a room from the list of empty rooms 
		{									// and equip it accordingly with the session to schedule		
			if (emptyRoomList.empty())
			{
				//throw new exception("Attempted to get a room from emptyRoomList while it was empty");
				cout << "Attempted to get a room from emptyRoomList while it was empty" << endl;
				break;
			}

			Room* newRoom = (emptyRoomList).back();
			emptyRoomList.pop_back();
			newRoom->equipment = session->equipment;
			assignSession(session, newRoom, timeSlots, roomList);	// fill up the time slots
			roomList.push_back(newRoom);
		}
	}
	return roomList;
}

void printSessions(list<Session*> sessionList)   // Print each session and equipment needed
{
	for (Session* session : sessionList)
	{
		cout << "Session " << session->sessionId << " with speaker(s) { ";
		for (int speaker : session->speaker) {
			cout << speaker << " ";
		}
		cout << "} needs equipment { ";
		for (string equipment : session->equipment)
		{
			cout << equipment << " ";
		}
		cout << "} for " << session->duration << " minutes (" << (int)ceil(session->duration / INTERVAL) << " time slots)." << endl;
	}
	cout << endl;
}

void printSchedule(list<Room*> scheduledRooms)  // Print each room that has been scheduled and its equipment
{
	for (Room* room : scheduledRooms)
	{
		cout << "Room " << room->roomId << " opens at " << room->startTime << " ( ";
		for (string equipment : room->equipment)
		{
			cout << equipment << " ";
		}
		cout << "): " << endl;

		int counter = 0;
		for (Session* session : room->schedule)
		{
			if (counter % 4 == 0) {
				cout << "|  ";
			}
			counter += 1;

			if (session != nullptr)
			{
				cout << session->sessionId << "  ";
			}
			else
			{
				cout << "_  ";
			}
		}
		cout << endl;
	}
}

int main()
{
	list<Room*> emptyRoomList;         // List that initially contains every room available to be scheduled
	list<Session*> sessionList;     // List that contains sessions to be scheduled

	// Empty rooms
	Room* room1 = new Room(1, 50, 7, 14, list<string>());
	Room* room2 = new Room(2, 100, 8, 14, list<string>());

	emptyRoomList = { room2, room1 };

	// Sessions to schedule
	Session* session1 = new Session(1, 120, 25, list<string>{ "Wifi" }, list<int>{ 1 });
	Session* session2 = new Session(2, 30, 20, list<string>{ "Projector", "Speaker" }, list<int>{ 2 });
	Session* session3 = new Session(3, 45, 20, list<string>{ "Wifi" }, list<int>{ 2 });
	Session* session4 = new Session(4, 50, 40, list<string>{ "Projector", "Speaker" }, list<int>{ 2 });
	Session* session5 = new Session(5, 45, 40, list<string>{ "Projector", "Speaker" }, list<int>{ 1 });
	Session* session6 = new Session(6, 30, 40, list<string>{ "Wifi" }, list<int>{ 1 });

	sessionList = { session1, session2, session3, session4, session5 };

	// Call scheduling algorithm
	list<Room*> scheduledRooms = schedule(sessionList, emptyRoomList);

	printSessions(sessionList);
	printSchedule(scheduledRooms);
}