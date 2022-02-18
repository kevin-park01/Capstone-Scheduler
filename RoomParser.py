import csv
from dataclasses import dataclass, field
import math
import schedule


def ParseRooms():
    file = open("Test1.csv")
    csvreader = csv.reader(file)
    header = next(csvreader)
    print(header)
    rows = []

    RoomList = []

    for row in csvreader:
        #rows.append(row)
        tempRoomId = int(row[0])
        tempMaxCapacity = int(row[1])
        tempStartTime = int(row[2])
        tempEndTime = int(row[3])
        tempFormat = row[4]
        #equipmentList 
        x = row[5].split()
        #print(x)

        tempEquipmentList = x 

        tempRoom = schedule.Room(tempRoomId, tempMaxCapacity, tempStartTime, tempEndTime, tempFormat, tempEquipmentList)

        RoomList.append(tempRoom)

    file.close()
    return RoomList