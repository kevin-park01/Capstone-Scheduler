#include <list>
using namespace std;

struct session {
    int sessionId, duration, estimatedCapacity;
    list<string> equipment = list<string>();
    list<string> speaker = list<string>();
};

struct room {
    int roomId, maxCapacity, startTime, endTime;
    list<string> equipment = list<string>();
    list<session*> schedule = list<session*>();
};
