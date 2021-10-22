#include <iostream>
#include <list>
using namespace std;

struct sessionNode {
    int sessionId, duration, estimatedCapacity;
    list<string> equipment = list<string>();
};

struct roomNode {
    int roomId, maxCapacity, startTime, endTime;
    list<string> equipment = list<string>();
    list<sessionNode*> schedule = list<sessionNode*>();
};

bool checkCompatability(sessionNode* session, roomNode* room) {
    // Check equipment compatability
    session->equipment.sort();
    room->equipment.sort();
    if(session->equipment != room->equipment) {
        return false;
    }
    // Check estimated capacity of session doesn't exceed max capacity of room
    if(session->estimatedCapacity > room->maxCapacity) {
        return false;
    }

    return true;    // Return true if all conditions are met
}

list<roomNode*>* schedule(list<sessionNode*>* sessionList, list<roomNode*>* emptyRoomList) {        // Schedule sessions into rooms
    list<roomNode*>* roomList = new list<roomNode*>();      // List containing rooms that have sessions scheduled
    bool isScheduled = false;
    for(sessionNode* session : *sessionList) {
        for(roomNode* room : *roomList) {
            if(checkCompatability(session, room)) {         // Check compatability of sessions to rooms
                room->schedule.push_back(session); 
                isScheduled = true;
            }
        }
        if(!isScheduled) {      // If an existing room isn't compatible, pull a room from the list of empty rooms and equip it accordingly with the session to schedule
            roomNode* newRoom = (*emptyRoomList).back();
           (*emptyRoomList).pop_back();
            newRoom->equipment = session->equipment;
            newRoom->schedule.push_back(session);
            (*roomList).push_back(newRoom);
        }
    }
    return roomList;
}

int main() {
    list<roomNode*>* emptyRoomList = new list<roomNode*>();         // List that initially contains every room available to be scheduled
    list<sessionNode*>* sessionList = new list<sessionNode*>();     // List that contains sessions to be scheduled

    // Empty rooms
    roomNode* room1 = new roomNode();
    room1->roomId = 1;
    room1->maxCapacity = 50;

    roomNode* room2 = new roomNode();
    room2->roomId = 2;
    room2->maxCapacity = 100;

    (*emptyRoomList).push_back(room1);
    (*emptyRoomList).push_back(room2);

    // Sessions to schedule
    sessionNode* session1 = new sessionNode();
    session1->sessionId = 1;
    session1->estimatedCapacity = 25;
    session1->equipment = {"Wifi"};

    sessionNode* session2 = new sessionNode();
    session2->sessionId = 2;
    session2->estimatedCapacity = 50;
    session2->equipment = {"Projector", "Speaker"};

    sessionNode* session3 = new sessionNode();
    session3->sessionId = 3;
    session3->estimatedCapacity = 20;
    session3->equipment = {"Wifi"};    

    (*sessionList).push_back(session1);
    (*sessionList).push_back(session2);
    (*sessionList).push_back(session3);

    // Call scheduling algorithm
    list<roomNode*>* scheduledRooms = schedule(sessionList, emptyRoomList);
    
    // Print each session and equipment needed
    for(sessionNode* session : *sessionList) {
        cout << session->sessionId << ": ";
        for(string equipment : session->equipment) {
            cout << equipment << " ";
        }
        cout << endl;
    }
    cout << endl;

    // Print each room that has been scheduled and its equipment
    for(roomNode* room : *scheduledRooms) {
        cout << "Schedule for room " << room->roomId << " ( ";
        for(string equipment : room->equipment) {
            cout << equipment << " ";
        }
        cout << "): ";
        for(sessionNode* session : room->schedule) {
            cout << session->sessionId << " ";
        }
        cout << endl;
    }
}