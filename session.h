#pragma once
#include <list>
#include <vector>
#include <time.h>
#include <string>
#include <cmath>
using namespace std;

extern const unsigned int ROOM_START;
extern const double INTERVAL;

struct Session
{
    unsigned int sessionId;
    unsigned int duration;  // in minutes
    unsigned int estimatedCapacity;
    string format;
    list<string> equipment;
    list<int> speaker;

    Session(unsigned int sessionId, unsigned int duration, unsigned int estimatedCapacity, string format, list<string> equipment, list<int> speaker)
    {
        this->sessionId = sessionId;
        this->duration = duration;
        this->estimatedCapacity = estimatedCapacity;
        this->format = format;
        this->equipment = equipment;
        this->speaker = speaker;
    }

    Session(unsigned int sessionId, unsigned int duration, unsigned int estimatedCapacity, string format)
    {
        Session(sessionId, duration, estimatedCapacity, format, list<string>(), list<int>());
    }
};

struct Room
{
    unsigned int roomId, maxCapacity;
    unsigned int startTime, endTime;
    string format;
    list<string> equipment;
    vector<Session*> schedule;

    // Fills up the time intervals in room->schedule between 
    // ROOM_START and room.startTime.  Should be called before 
    // attempting to schedule any sessions.
    // * assumes ROOM_START is the earliest possible time for any
    // room to be available *
    void initializeSchedule()
    {
        if (ROOM_START <= startTime)
        {
            int timeSlots = (int)ceil(60 * (endTime - ROOM_START) / INTERVAL);  // number of time slots btwn ROOM_START and startTime                    
            schedule = vector<Session*>(timeSlots, nullptr);    // Initialize schedule to have null pointers indicating a session has not been scheduled
        }
        else
        {
            cout << "Room cannot start before " << ROOM_START << endl;
        }
    }

    Room(int roomId, int maxCapacity, int startTime, int endTime, string format, list<string> equipment)
    {
        this->roomId = roomId;
        this->maxCapacity = maxCapacity;
        this->startTime = startTime;
        this->endTime = endTime;
        this->format = format;
        this->equipment = equipment;
        initializeSchedule();
    }
};
