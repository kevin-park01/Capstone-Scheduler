#pragma once
#include <list>
#include <time.h>
#include <string>
using namespace std;

extern const int ROOM_START;
extern const int INTERVAL;

struct session
{
    unsigned int sessionId;
    unsigned int duration;  // in minutes
    unsigned int estimatedCapacity;
    list<string>* equipment;
    list<string>* speaker;


    session(unsigned int sessionId, unsigned int duration, unsigned int estimatedCapacity, list<string>* equipment, list<string>* speaker)
    {
        this->sessionId = sessionId;
        this->duration = duration;
        this->estimatedCapacity = estimatedCapacity;
        this->equipment = equipment;
        this->speaker = speaker;
    }

    session(unsigned int sessionId, unsigned int duration, unsigned int estimatedCapacity)
    {
        session(sessionId, duration, estimatedCapacity, new list<string>(), new list<string>());
    }

};

struct room
{
    unsigned int roomId, maxCapacity;
    unsigned int startTime, endTime;
    list<string>* equipment;
    list<session*>* schedule;

    // Fills up the time intervals in room->schedule between 
    // ROOM_START and room.startTime.  Should be called before 
    // attempting to schedule any sessions.
    // * assumes ROOM_START is the earliest possible time for any
    // room to be available *
    void initializeSchedule()
    {
        schedule = new list<session*>();
        if (ROOM_START < startTime)
        {
            int timeSlots = (int)ceil(60 * (startTime - ROOM_START) / INTERVAL);  // number of time slots btwn ROOM_START and startTime                    
            schedule->insert(schedule->begin(), timeSlots, nullptr);   // load schedule w/ t unavailable time slots
        }
    }

    room(int roomId, int maxCapacity, int startTime, int endTime, list<string>* equipment)
    {
        this->roomId = roomId;
        this->maxCapacity = maxCapacity;
        this->startTime = startTime;
        this->endTime = endTime;
        this->equipment = equipment;
        initializeSchedule();
    }
};
