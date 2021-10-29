#include <iostream>
#include "session.h"

const int ROOM_START = 6;  // 6 a.m. 24-hour clock 
const int INTERVAL = 15;    // minutes

bool checkCompatability(session* session, room* room) {
	bool equipCompatible = true, capCompatible = true, timeCompatible = true;

	// Check equipment compatability
	session->equipment.sort();
	room->equipment.sort();
	if (session->equipment != room->equipment) {
		equipCompatible = false;
	}
	// Check estimated capacity of session doesn't exceed max capacity of room
	if (session->estimatedCapacity > room->maxCapacity) {
		capCompatible = false;
	}

	// Check if room is available for duration of session
	if (room->endTime <= ROOM_START + session->duration + room->schedule.size() * INTERVAL)
	{
		timeCompatible = false;
	}

	return equipCompatible && capCompatible && timeCompatible;    
}

list<room*> schedule(list<session*> sessionList, list<room*> emptyRoomList) {        // Schedule sessions into rooms
	list<room*> roomList = list<room*>();      // List containing rooms that have sessions scheduled	
	bool isScheduled = false;
	int timeSlots = 0;

	for (session* session : sessionList) {
		timeSlots = (int)ceil(session->duration / INTERVAL);  // number of time slots to fill for this session
		for (room* room : roomList) {
			if (checkCompatability(session, room)) {         // Check compatability of sessions to rooms

				for (int i = 0; i < timeSlots; i++) // fill up the time slots
				{
					room->schedule.push_back(session);
				}
				isScheduled = true;
			}
		}
		if (!isScheduled) {      // If an existing room isn't compatible, pull a room from the list of empty rooms and equip it accordingly with the session to schedule
			room* newRoom = (emptyRoomList).back();
			emptyRoomList.pop_back();
			newRoom->equipment = session->equipment;
			newRoom->initializeSchedule(ROOM_START, INTERVAL); // initialize the schedule of the room

			timeSlots = (int)ceil(session->duration / INTERVAL);
			for (int i = 0; i < timeSlots; i++) // fill up the time slots
			{
				newRoom->schedule.push_back(session);
			}

			roomList.push_back(newRoom);
		}
	}
	return roomList;
}

void printSessions(list<session*> sessionList) {      // Print each session and equipment needed
	for (session* session : sessionList) {
		cout << session->sessionId << ": ";
		for (string equipment : session->equipment) {
			cout << equipment << " ";
		}
		cout << endl;
	}
	cout << endl;
}

void printSchedule(list<room*> scheduledRooms) {      // Print each room that has been scheduled and its equipment
	for (room* room : scheduledRooms) {
		cout << "Schedule for room " << room->roomId << " ( ";
		for (string equipment : room->equipment) {
			cout << equipment << " ";
		}
		cout << "): ";
		for (session* session : room->schedule) {
			cout << session->sessionId << " ";
		}
		cout << endl;
	}
}

int main() {
	list<room*> emptyRoomList = list<room*>();         // List that initially contains every room available to be scheduled
	list<session*> sessionList = list<session*>();     // List that contains sessions to be scheduled

	// Empty rooms
	room* room1 = new room();
	room1->roomId = 1;
	room1->maxCapacity = 50;

	room* room2 = new room();
	room2->roomId = 2;
	room2->maxCapacity = 100;

	emptyRoomList.push_back(room1);
	emptyRoomList.push_back(room2);

	// Sessions to schedule
	session* session1 = new session();
	session1->sessionId = 1;
	session1->estimatedCapacity = 25;
	session1->equipment = { "Wifi" };

	session* session2 = new session();
	session2->sessionId = 2;
	session2->estimatedCapacity = 50;
	session2->equipment = { "Projector", "Speaker" };

	session* session3 = new session();
	session3->sessionId = 3;
	session3->estimatedCapacity = 20;
	session3->equipment = { "Wifi" };

	sessionList.push_back(session1);
	sessionList.push_back(session2);
	sessionList.push_back(session3);

	// Call scheduling algorithm
	list<room*> scheduledRooms = schedule(sessionList, emptyRoomList);

	printSessions(sessionList);
	printSchedule(scheduledRooms);
}