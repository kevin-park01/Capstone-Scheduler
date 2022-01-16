#pragma once
#include <list>
#include <vector>
#include <string>
#include <sstream>
#include <fstream>
#include <iostream>
#include "session.h"
using namespace std;


list<Room*> ParseRooms() 
{
	fstream fin;
	list<Room*> tempEmptyRoomList;
	string line;

	fin.open("RoomInput.csv", ios::in); //open input

	while (getline(fin, line) && !line.empty()) 
	{
		stringstream mystream(line);
		string temp;

		getline(mystream, temp, ',');
		int tempID = stoi(temp);

		getline(mystream, temp, ',');
		int tempmaxcap = stoi(temp);

		getline(mystream, temp, ',');
		int tempStartTime = stoi(temp);

		getline(mystream, temp, ',');
		int tempEndTime = stoi(temp);

		getline(mystream, temp, ',');
		string tempFormat = temp;

		getline(mystream, temp, ',');

		/*
		getline(mystream, temp, ',');

		list<string> words;

		string s;
		using namespace std;

		istringstream iss(temp);

		while ( getline( iss, s, ' ' ) ) {


			 words.push_back(s);
		}

		//words = NULL;
		for (auto const &i: words) {

	}
		*/

		Room* room2 = new Room(tempID, tempmaxcap, tempStartTime, tempEndTime, tempFormat, list<string>());
		tempEmptyRoomList.push_back(room2);

		if (!mystream)	break; // something went wrong reading the line
	}

	fin.close();
	return tempEmptyRoomList;
};


list<Session*> ParseSession() 
{
	fstream fin;
	list<Session*> tempEmptySessionList;
	string line1;

	fin.open("sess.csv", ios::in);

	while (getline(fin, line1) && !line1.empty()) 
	{
		stringstream mystream(line1);
		list<string> tempEquipment;
		list<int> tempSpeaker;
		string temp;

		getline(mystream, temp, ',');
		int tempSessionId = stoi(temp);

		getline(mystream, temp, ',');
		int tempSessionDuration = stoi(temp);

		getline(mystream, temp, ',');
		int tempEstimatedCapacity = stoi(temp);

		getline(mystream, temp, ',');
		string tempFormat = temp;

		getline(mystream, temp, ',');

		string d;	
		istringstream iss(temp);
		while (getline(iss, d, ' ')) 
		{
			tempEquipment.push_back(d);
		}

		getline(mystream, temp, ',');
		
		string r;	
		istringstream isss(temp);
		while (getline(isss, r, ' ')) 
		{
			int hold = stoi(r);
			tempSpeaker.push_back(hold);
		}

		/*list<string> words1;

		string d;
		using namespace std;
		istringstream iss(temp);
		while ( getline( iss, d, ' ' ) ) {

			 words1.push_back(d);
		}




		for (auto const &i: words1) {
			//std::cout << i << std::endl;
	}

		getline(mystream, temp, ',');

		list<int> temporary;
		string r;
		using namespace std;
		istringstream isss(temp);
		while ( getline( isss, r, ' ' ) ) {

			 int hold = stoi(r);
			 temporary.push_back(hold);
		}
*/

		Session* session1 = new Session(tempSessionId, tempSessionDuration, tempEstimatedCapacity, tempFormat, tempEquipment, tempSpeaker);
		tempEmptySessionList.push_back(session1);

		if (!mystream)	break; // something went wrong reading the line
	}

	fin.close();
	return tempEmptySessionList;
};