import csv
from dataclasses import dataclass, field
import math
import schedule


def ParseSession():
	file = open("Test.csv")
	csvreader = csv.reader(file)
	header = next(csvreader)
	print(header)
	rows = []
	#print (type(rows))

	SessionList = []

	for row in csvreader:
	    #rows.append(row)
	    tempSessionId = int(row[0])
	    tempDuration = int(row[1])
	    tempEstimatedCapacity = int(row[2])
	    tempTitle = row[3]
	    tempTopic = row[4]
	    tempFormat = row[5]
	    #equipmentList 
	    x = row[6].split()
	    #print(x)

	    tempEquipmentList = x 
	    #tempEquipemt = row[5]

	    y = row[7].split()

	    tempSpeaker = y

	    tempSession = schedule.Session(tempSessionId, tempDuration, tempEstimatedCapacity,tempTitle, tempTopic, tempFormat, tempEquipmentList, tempSpeaker)

	    SessionList.append(tempSession)


	file.close()
	return SessionList



