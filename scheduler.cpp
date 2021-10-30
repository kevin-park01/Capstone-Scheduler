#include <iostream>
#include "session.h"

const int ROOM_START = 6;  // 6 a.m. 24-hour clock 
const int INTERVAL = 15;    // minutes

bool checkCompatability(session* session, room* room)
{
	bool equipCompatible = true, capCompatible = true, timeCompatible = true;

	// Check equipment compatability
	session->equipment->sort();
	room->equipment->sort();
	if (*session->equipment != *room->equipment)
	{
		equipCompatible = false;
	}

	// Check estimated capacity of session doesn't exceed max capacity of room
	if (session->estimatedCapacity > room->maxCapacity)
	{
		capCompatible = false;
	}

	// Check if room is available for duration of session
	if ((room->endTime * 60) <= (ROOM_START * 60) + session->duration + room->schedule->size() * INTERVAL)
	{
		timeCompatible = false;
	}

	return equipCompatible && capCompatible && timeCompatible;
}


list<room*> schedule(list<session*> sessionList, list<room*> emptyRoomList)     // Schedule sessions into rooms
{
	list<room*> roomList = list<room*>();      // List containing rooms that have sessions scheduled	
	bool isScheduled = false;
	int timeSlots = 0;

	for (session* session : sessionList)
	{
		timeSlots = (int)ceil(session->duration / INTERVAL);  // number of time slots to fill for this session
		for (room* room : roomList)
		{
			if (checkCompatability(session, room)) // Check compatability of sessions to rooms
			{
				room->schedule->insert(room->schedule->cend(), timeSlots, session);	// fill up the time slots
				isScheduled = true;
			}
		}

		if (!isScheduled)					// If an existing room isn't compatible, pull a room from the list of empty rooms 
		{									// and equip it accordingly with the session to schedule		
			if (emptyRoomList.empty())
			{
				throw new exception("Attempted to get a room from emptyRoomList while it was empty");
			}

			room* newRoom = (emptyRoomList).back();
			emptyRoomList.pop_back();
			newRoom->equipment = session->equipment;
			newRoom->schedule->insert(newRoom->schedule->cend(), timeSlots, session);	// fill up the time slots
			roomList.push_back(newRoom);
		}
	}
	return roomList;
}


void printSessions(list<session*> sessionList)   // Print each session and equipment needed
{
	for (session* session : sessionList)
	{
		cout << session->sessionId << ": ";
		for (string equipment : *session->equipment)
		{
			cout << equipment << " ";
		}
		cout << endl;
	}
	cout << endl;
}


void printSchedule(list<room*> scheduledRooms)  // Print each room that has been scheduled and its equipment
{
	for (room* room : scheduledRooms)
	{
		cout << "Schedule for room " << room->roomId << " ( ";
		for (string equipment : *room->equipment)
		{
			cout << equipment << " ";
		}
		cout << "): ";
		for (session* session : *room->schedule)
		{
			if (session != nullptr)
			{
				cout << session->sessionId << "  ";
			}
			else
			{
				cout << " _  ";
			}
		}
		cout << endl;
	}
}

int main()
{
	list<room*> emptyRoomList;         // List that initially contains every room available to be scheduled
	list<session*> sessionList;     // List that contains sessions to be scheduled

	// Empty rooms
	room* room1 = new room(1, 50, ROOM_START, 18, new list<string>);
	room* room2 = new room(2, 100, 8, 18, new list<string>);

	emptyRoomList = { room1, room2 };

	// Sessions to schedule
	session* session1 = new session(1, 60, 25, new list<string>{ "Wifi" }, nullptr);
	session* session2 = new session(2, 30, 20, new list<string>{ "Projector", "Speaker" }, nullptr);
	session* session3 = new session(3, 15, 20, new list<string>{ "Wifi" }, nullptr);

	sessionList = { session1, session2, session3 };

	// Call scheduling algorithm
	list<room*> scheduledRooms = schedule(sessionList, emptyRoomList);

	printSessions(sessionList);
	printSchedule(scheduledRooms);
}