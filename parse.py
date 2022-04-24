import csv
from dataclasses import dataclass, field
import math
from datetime import datetime
import schedule

def generatedCSV(sessions):

	fields = ['Session ID','Title', 'Format', 'Type', 'Estimated Capacity',
	'Subject/Topic', 'Sponsor','Start Time', 'End Time' ,'Room ID', 'Date'] 

	rows = []
	
	for session in sessions:
		
		temp_id = session.session_id
		temp_title = session.title
		temp_format = session.format
		temp_type = session.type
		temp_capacity = session.est_capacity
		temp_topic= session.topic
		temp_sponsor = session.sponsors
		temp_start= session.start_time.time()
		temp_end = session.end_time.time()
		temp_room = session.assigned_room
		hold = session.start_time.month
		hold1 = session.start_time.day
		temp_day = str(hold) + "/" + str(hold1)

		row = [temp_id, temp_title, temp_format, temp_type,
		temp_capacity, temp_topic, temp_sponsor, temp_start, temp_end, temp_room, temp_day]
		
		rows.append(row)

	with open('SCHEDULEOUTPUT.csv', 'w', encoding='utf8') as f:
		write = csv.writer(f)
		write.writerow(fields)
		write.writerows(rows)



def parseRooms(filename):
    file = open(filename, encoding="utf8")
    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []

    RoomList = []

    for row in csvreader:
        #rows.append(row)
        temp_room_id = int(row[0])
        temp_property = row[1]
        temp_room_name = row[2]
        temp_capacity = int(row[3])
        temp_floor = int(row[4])

        tempRoom = schedule.Room(temp_room_id, temp_capacity, temp_room_name, temp_property, temp_floor)

        RoomList.append(tempRoom)

    file.close()
    return RoomList

def parseTime(filename):
    file = open(filename, encoding="utf8")
    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []
    start_time_list = []
    end_time_list = []


    for row in csvreader:

        time = row[0].split(':')
        hour = int(time[0])
        minute = int(time[1])
        time_2 = row[1].split(':')
        hour2 = int(time_2[0])
        minute2 = int(time_2[1])
        start_time_list.append(datetime(1,1,1,hour,minute))
        end_time_list.append(datetime(1,1,1,hour2,minute2))

    return start_time_list, end_time_list

def parseDays(filename):
    file = open(filename, encoding="utf8")
    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []

    day_list = []

    for row in csvreader:

        days =  row[0].split('/')
        temp_month = int(days[0])
        temp_day = int(days[1])
        temp_year = int(days[2])
        day_list.append(datetime(temp_year,temp_month,temp_day))

    return day_list


def parseSpeakers(filename):
    file = open(filename, encoding="utf8")
    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []
    speaker_list = []

    count = 0 

    for row in csvreader:
        temp_id = int(row[0])
        flag = False

        if count > 0:
            for speakers in speaker_list:
                if speakers.speaker_id == temp_id:
                    test = int(row[3])
                    speakers.session_ids.append(test)
                    flag = True
                
        if flag == False:
        
            temp_fname = row[1]
            temp_initial = row[2]
            temp_session_id = [int(row[3])]
            temp_speaker = schedule.Speaker(temp_id, temp_fname, temp_initial, temp_session_id)
            speaker_list.append(temp_speaker)

        count += 1
    return speaker_list


def parseSession(filename):
    file = open(filename, encoding="utf8")
    csvreader = csv.reader(file)
    header = next(csvreader)
    rows = []
    SessionList = []

    for row in csvreader:
    
        temp_session_id = int(row[0])
        temp_title = row[1]
        temp_format = row[2]
        temp_type = row[3]
        temp_estimated_capacity = int(row[4])
        temp_topic = row[5]
        temp_sponsor = [row[6]]
        temp_duration = int(row[8])
        temp_equipment = row[9].split(',')
        temp_speaker = row[10].split(',')
        tempSession = schedule.Session(temp_session_id, temp_duration, temp_estimated_capacity,
        temp_title, temp_format, temp_topic, temp_type, temp_sponsor, temp_equipment, temp_speaker)
        SessionList.append(tempSession)


    file.close()
    return SessionList

