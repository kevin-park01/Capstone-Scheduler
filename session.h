#include <list>
#include <time.h>
using namespace std;

struct session {
    int sessionId;
    int duration;  // in minutes
    int estimatedCapacity;
    list<string> equipment = list<string>();
    list<string> speaker = list<string>();
};

struct room {
    int roomId, maxCapacity;
    int startTime, endTime;
    list<string> equipment = list<string>();
    list<session*> schedule = list<session*>();

    // Fills up the time intervals in room->schedule between 
    // ROOM_START and room.startTime.  Should be called before 
    // attempting to schedule any sessions.
    // * assumes ROOM_START is the earliest possible time for any
    // room to be available *
    void initializeSchedule(int room_start, int intrvl)
    {
        if (room_start > startTime)
        {
            int t = (int) ceil((room_start - startTime) / intrvl);
            for (int i = 0; i < t; i++)
            {
                schedule.push_back(nullptr);
            }
        }
    }
};
