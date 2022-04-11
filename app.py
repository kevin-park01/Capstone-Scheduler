"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from re import search
import schedule
import parse
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "secret"
wsgi_app = app.wsgi_app     


# 1. Include Parsing Here
# 2. Call functions to get lists for all start times, end times, days, sessions, rooms, speakers
# 3. Create Schedule object
# 4. Call 'init' function for object
'''
speakers = parse.parseSpeakers('speaker.csv')
sessions = parse.parseSession('session.csv')
rooms = parse.parseRooms('rooms.csv')
days = parse.parseDays('Date.csv')
start_times, end_times = parse.parseTime('time.csv')
day_schedule = schedule.Schedule(start_times, end_times, days, sessions, rooms, speakers)
day_schedule.init()




'''
room1 = schedule.Room(1, 150, 'Room 1', 'WSCC', 1)
room2 = schedule.Room(2, 50, 'Room 2', 'BYENG', 2)

session1 = schedule.Session(1, 75, 10, 'Intro to CS 1', 'Roundtable', 'CS', 'Social Event', ['ASU'],['Mic'], [1])
session2 = schedule.Session(2, 75, 100, 'Intro to CS 2', 'Lecture', 'CS', 'Special Session', ['ASU'], ['Mic', 'Wifi'], [1])
session3 = schedule.Session(3, 75, 15, 'Intro to BS 1', 'Roundtable', 'BS', 'Social Event', ['Fulton'], ['Mic'], [2])
session4 = schedule.Session(4, 75, 10, 'Intro to BS 2', 'Panel', 'BS', 'Forum Session', ['Fulton'], ['Wifi'], [2])
session5 = schedule.Session(5, 75, 75, 'Intro to ENG 1', 'Lecture', 'BS', 'Social Event', ['Arts'], ['Wifi'], [2])
session6 = schedule.Session(6, 75, 10, 'Intro to ENG 2', 'Panel', 'BS', 'Special Session', ['Arts'], ['Wifi' ], [2])

speaker1 = schedule.Speaker(1, 'Bob', 'B', [1, 2])
speaker2 = schedule.Speaker(1, 'Maria', 'M', [3, 4, 5, 6])

sessions = [session1, session2, session3, session4, session5, session6]
rooms = [room1, room2]
speakers = [speaker1, speaker2]

year = datetime.now().year
month = datetime.now().month
start_times = [datetime(1, 1, 1, 7, 0), datetime(1, 1, 1, 8, 30)]
end_times = [datetime(1, 1, 1, 8, 15), datetime(1, 1, 1, 9, 45)]
days = [datetime(year, month, 13), datetime(year, month, 14), datetime(year, month, 15), datetime(year, month, 16)]

day_schedule = schedule.Schedule(start_times, end_times, days, sessions, rooms, speakers)
day_schedule.init()





@app.route('/', methods = ['POST', 'GET'])
def main():
    return redirect(url_for('stepOne'))
 


@app.route('/StepZero', methods = ['POST', 'GET'])
def stepZero():
    """ Renders the Step0 page. 
        For POST requests, stores the Step0 form data in the session and renders the Step1 page. """
    if request.method == 'POST':
        # TODO: store input files on server
        # TODO: ensure all needed input files have been entered
        return redirect(url_for('stepOne'))

    else:
        return render_template('Step0.html')



# TODO: dynamically modify the list of unscheduled sessions displayed based on filter selections    
# TODO: check to make sure at least one session was selected
@app.route('/StepOne', methods = ['POST', 'GET'])
def stepOne():
    """ Renders the Step1 page. 
        For POST requests, stores the Step1 form data in the session and renders the Step2 page. """
    if request.method == 'POST':
        session["selectedSessFormats"] = request.form.getlist('selectedSessFormats')
        session["selectedTopics"] = request.form.getlist('selectedTopics')
        session["selectedTypes"] = request.form.getlist('selectedTypes')
        session["selectedSponsors"] = request.form.getlist('selectedSponsors')
        
        print(request.form.getlist('selectedSessions')) # list of the session_ids as str

        '''
            request.form.getlist() returns list of strings, not objects
            * it looks like getlist() has an optional second parameter that takes a callable type
              to convert the items to, but I have not figured that out yet... *
              
                So, this is my workaround, which takes the session_ids of the selected sessions
            and finds the corresponding session objects.  It is not efficient or elegant.

            In sum, I need to be able to get the list of selected objects (unscheduled sessions & available rooms)
            from the HTML forms.  This appears to be an issue for Step1 and Step3.
        '''

        session["selectedSessions"] = list()
        for i in request.form.getlist('selectedSessions'):
            for sess in day_schedule.get_unscheduled_sessions():
                if int(i) == sess.session_id:
                    session["selectedSessions"].append(sess)
       

        print("selected session formats:  ", session["selectedSessFormats"])
        print("selected session topics:  ", session["selectedTopics"])
        print("selected session types:  ", session["selectedTypes"])
        print("selected session sponsors:  ", session["selectedSponsors"])
        print("selected sessions:  ", session["selectedSessions"])
        
        return redirect(url_for('stepTwo'))

    else:
        unscheduledSessions = day_schedule.get_unscheduled_sessions()
        sessionFormats = day_schedule.get_session_formats()
        sessionTopics = day_schedule.get_session_topics()
        sessionTypes = day_schedule.get_session_types()
        sessionSponsors = day_schedule.get_session_sponsors()

        return render_template('Step1.html', unscheduled_sessions=unscheduledSessions, sessFormats=sessionFormats, 
                                                   topics=sessionTopics, types=sessionTypes, sponsors=sessionSponsors)




@app.route('/StepTwo', methods = ['POST', 'GET'])
def stepTwo():
    """ Renders the Step2 page. 
        For POST requests, stores the Step2 form data in the session and renders the Step3 page. """
    if request.method == 'POST':
        session["selectedDates"] = list()
        session["selectedTimes"] = list()        

        for d in request.form.getlist('selectedDates'):
            session["selectedDates"].append(datetime.strptime(d, '%Y-%m-%d %H:%M:%S'))
           
        for t in request.form.getlist('selectedTimes'):
            session["selectedTimes"].append(datetime.strptime(t, '%Y-%m-%d %H:%M:%S'))

        print("selected days:  ", session["selectedDates"])
        print("selected times:  ", session["selectedTimes"])     
        
        return redirect(url_for('stepThree'))

    else:        
        return render_template('Step2.html', dates=day_schedule.days, 
                               sTimes=day_schedule.start_times, eTimes=day_schedule.end_times)  



# TODO: dynamically modify the list of available rooms displayed based on filter selections    
# TODO: add number of selected sessions & range of est. capacity for selected sessions
# TODO: error handling for when no rooms are selected
@app.route('/StepThree', methods = ['POST', 'GET'])
def stepThree():
    """ Renders the Step3 page. 
        For POST requests, stores the Step2 form data in the session and renders the Step4 page. """
    if request.method == 'POST':        
        session["selectedProperties"] = request.form.getlist('selectedProperties')       
        session["maxCapacity"] = request.form.get('maxCapacity', type=int)
        session["selectedRoomFormats"] = request.form.getlist('selectedRoomFormats')
        session["selectedAVSetups"] = request.form.getlist('selectedAVSetups')
        session["selectedRooms"] = request.form.getlist('selectedRooms')    # ISSUE: must be Room object type, but str type (see Step1)
        
        print("selected propertiess:  ", session["selectedProperties"])       
        print("selected max capacity:  ", session["maxCapacity"])
        print("selected room formats:  ", session["selectedRoomFormats"])
        print("selected AV setups:  ", session["selectedAVSetups"])
        print("selected rooms:  ", session["selectedRooms"])
        
        return redirect(url_for('stepFour'))

    else:        
        selected_sessions = session['selectedSessions']  
        minCapacity = day_schedule.get_session_min_capacity(selected_sessions)
        maxCapacity = day_schedule.get_room_max_capacity()
        roomProperties = day_schedule.get_room_properties()


        ''' ISSUE: rooms initially have no format/equipment, causing 
            get_room_format() and get_room_equipment() to return empty lists
            and get_filtered_room_availability() to fail
        '''
        roomFormats = day_schedule.get_session_formats()    #   .get_room_formats()
        roomEquipment =  ['Mic', 'Wifi']                    #   day_schedule.get_room_equipment()
        
        
        #avbleRooms = day_schedule.get_filtered_room_availability(day_schedule.days, day_schedule.start_times, 
        #                                                   roomEquipment, minCapacity, roomFormats, selected_sessions)
               
        return render_template('Step3.html', properties=roomProperties, min=minCapacity, max=maxCapacity,
                              formats=roomFormats, avSetups=roomEquipment, availableRooms=rooms) 
        
        


        
@app.route('/StepFour', methods = ['POST', 'GET'])
def stepFour():
    """ Renders the Step4 page. """
    if request.method == 'POST':
        # store generated schedule on server 
        return render_template('Step4.html')
    else:
        day_schedule.create_schedule(session["selectedSessions"], session["selectedRooms"], 
                                     session["selectedDays"], session["selectedTimes"])
        return render_template('Step4.html') 




if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
   


    
