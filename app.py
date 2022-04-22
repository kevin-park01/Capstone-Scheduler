"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
from re import search
from typing import Tuple
import schedule
import parse
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = "secret"
wsgi_app = app.wsgi_app     

'''
room1 = schedule.Room(1, 150, 'Room 1', 'WSCC', 1, 'Rountable')
room2 = schedule.Room(2, 50, 'Room 2', 'BYENG', 2, 'Theatre')

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

selectedSessions = list[schedule.Session]()
selectedRooms = list[schedule.Room]()
'''

speakers = None
sessions = None
rooms = None
days = None
start_times= None
end_times = None
day_schedule = None
selectedSessions = None
selectedRooms = None


def makeChecked(all: list[str], selected: list[str]) -> dict[(str, str)]:
    """Forms a dict that is used to maintain the 'checked' state of a HTML checkbox."""

    checked = dict.fromkeys(all, "")

    for k, v in checked.items():
        if k in selected:
            checked[k] = "checked"
            
    return checked
    


@app.route('/', methods = ['POST', 'GET'])
def main():
    """Defines the entry point of the application."""
    return redirect(url_for('stepZero'))
 


@app.route('/StepZero', methods = ['POST', 'GET'])
def stepZero():
    """ Renders the Step0 page.
    For POST requests, stores the Step0 form data in the session and renders the Step1 page. """

    if request.method == 'POST':
        global day_schedule
        global selectedRooms
        global selectedSessions
        global start_times
        global end_times
        global speakers 
        global days

        d = request.form['datesInput']
        days = parse.parseDays(d)

        s = request.form['speakersInput']  
        speakers = parse.parseSpeakers(s)
         
        t = request.form['timeInput']
        start_times, end_times = parse.parseTime(t)

        r = request.form['roomsInput']
        rooms = parse.parseRooms(r)

        s1 = request.form['sessionsInput']
        sessions = parse.parseSession(s1)
        
        day_schedule = schedule.Schedule(start_times, end_times, days, sessions, rooms, speakers)
        day_schedule.init()

        selectedSessions = list[schedule.Session]()
        selectedRooms = list[schedule.Room]()

        return redirect(url_for('stepOne'))

    else:
        return render_template('Step0.html')

    

@app.route('/StepOne', methods = ['POST', 'GET'])
def stepOne():       
    """Render the 'Step 1' page or redirect to the 'Step 2' page."""

    # The user has submitted form data.
    # Reload Step 1 to update the page in response to user selections (apply the selected filters )
    # or navigate to Step 2.
    if request.method == 'POST':
        # Store the checked filter fields in the session state as lists of strings
        session['selectedSessFormats'] = request.form.getlist('selectedSessFormats')
        session['selectedTopics'] = request.form.getlist('selectedTopics')
        session['selectedTypes'] = request.form.getlist('selectedTypes')
        session['selectedSponsors'] = request.form.getlist('selectedSponsors')
  
        # Reloading the page to display the filtered sessions and checked fields
        if 'applyFilters' in request.form:         
            unscheduledSessions = day_schedule.get_filtered_sessions(session["selectedTypes"], 
                                                                     session["selectedSessFormats"], 
                                                                     session['selectedSponsors'], 
                                                                     session['selectedTopics'])
            
            # store the form data as dicts that store checkbox states 
            sessionFormats = makeChecked(list(day_schedule.get_session_formats()), session['selectedSessFormats'])
            sessionTopics = makeChecked(list(day_schedule.get_session_topics()), session['selectedTopics'])
            sessionTypes = makeChecked(list(day_schedule.get_session_types()), session['selectedTypes'])
            sessionSponsors = makeChecked(list(day_schedule.get_session_sponsors()), session['selectedSponsors'])

            return render_template('Step1.html', unscheduled_sessions=unscheduledSessions, sessFormats=sessionFormats, 
                                                 topics=sessionTopics, types=sessionTypes, sponsors=sessionSponsors)


        # Navigating to the next page (Step 2).
        elif 'nextStep' in request.form:        
            # get the session objects corresponding to the selected sessions 
            selectedSessions.clear()
            for i in request.form.getlist('selectedSessions', type=int):
                for sess in day_schedule.get_unscheduled_sessions():
                    if i == sess.session_id:
                        selectedSessions.append(sess)
            
            return redirect(url_for('stepTwo'))
        
    # Render the 'Step 1' page
    # This should occur when the page is first loaded and no selections have been made by the user. 
    else:    
        # store the form data as dicts that store checkbox states 
        unscheduledSessions = day_schedule.get_unscheduled_sessions()
        sessionFormats = dict.fromkeys(list(day_schedule.get_session_formats()), "")
        sessionTopics = dict.fromkeys(list(day_schedule.get_session_topics()), "")
        sessionTypes = dict.fromkeys(list(day_schedule.get_session_types()), "")
        sessionSponsors = dict.fromkeys(list(day_schedule.get_session_sponsors()), "")
        
        return render_template('Step1.html', unscheduled_sessions=unscheduledSessions, sessFormats=sessionFormats, 
                                             topics=sessionTopics, types=sessionTypes, sponsors=sessionSponsors)




@app.route('/StepTwo', methods = ['POST', 'GET'])
def stepTwo():
    """ Renders the Step2 page. 
    For POST requests, stores the Step2 form data in the session and renders the Step3 page. """

    # Dates and times have been selected, navigating to Step 3
    if request.method == 'POST':
        # convert the selected dates and times to datetime objects & store in session state
        session["selectedDates"] = [datetime.strptime(date, '%Y-%m-%d %H:%M:%S') for date in request.form.getlist('selectedDates')]
        session["selectedTimes"] = [datetime.strptime(time, '%Y-%m-%d %H:%M:%S') for time in request.form.getlist('selectedTimes')]       

        return redirect(url_for('stepThree'))

    # The page is loaded, no user selections have been made yet
    else:        
        return render_template('Step2.html', dates=day_schedule.days, sTimes=day_schedule.start_times, eTimes=day_schedule.end_times)  




@app.route('/StepThree', methods = ['POST', 'GET'])
def stepThree():
    """Renders the 'Step 1' page or redirect to the 'Step 2' page."""

    # The user has submitted form data.
    # Reload Step 3 to update the page in response to user selections (apply the selected filters)
    # or navigate to Step 4.
    if request.method == 'POST':      
        # Store the checked filter fields in the session state
        session["selectedProperties"] = request.form.getlist('selectedProperties')       
        session["maxCapacity"] = request.form.get('maxCapacity', type=int)
        session["selectedRoomFormats"] = request.form.getlist('selectedRoomFormats')
        session["selectedAVSetups"] = request.form.getlist('selectedAVSetups')
       
        # Reloading the page to display the filtered rooms and checked fields
        if 'applyFilters' in request.form:   
            # the dates & times used for scheduling are set to all dates & times if unselected
            selectedDates =  session['selectedDates'] if not session.get('selectedDates') == None else day_schedule.days
            selectedTimes = session['selectedTimes'] if not session.get('selectedDates') == None else day_schedule.start_times
        
            minCapacity = day_schedule.get_session_min_capacity(selectedSessions)            
            maxCapacity = session["maxCapacity"] if not session.get('maxCapacity') == None else day_schedule.get_room_max_capacity()                
    
            # store the form data as dicts that store checkbox states 
            roomProperties = makeChecked(list(day_schedule.get_room_properties()), session["selectedProperties"])
            roomFormats = makeChecked(list(day_schedule.get_room_formats()), session["selectedRoomFormats"])          
            roomEquipment = makeChecked(list(day_schedule.get_room_equipment()), session["selectedAVSetups"])         

            # get the available rooms based on the room filters, sessions, dates & times selected
            avbleRooms = day_schedule.get_filtered_room_availability(selectedDates, selectedTimes, 
                                                                     session["selectedProperties"],
                                                                     session["selectedAVSetups"], 
                                                                     maxCapacity, 
                                                                     session["selectedRoomFormats"], 
                                                                     selectedSessions)         

            return render_template('Step3.html', properties=roomProperties, min=minCapacity, max=maxCapacity,
                                                 formats=roomFormats, avSetups=roomEquipment, availableRooms=avbleRooms) 
            
        # Navigating to the next page (Step 4).
        elif 'nextStep' in request.form:                  
            # get the room objects corresponding to the selected rooms   
            selectedRooms.clear() 
            for i in request.form.getlist('selectedRooms', type=int):
                for room in day_schedule.all_rooms:
                    if i == room.room_id:
                        selectedRooms.append(room)
                          
            return redirect(url_for('stepFour'))

    # Render the 'Step 3' page.
    # This should occur when the page is first loaded and no selections have been made by the user. 
    else:        
        selectedDates =  session['selectedDates'] if not session.get('selectedDates') == None else day_schedule.days
        selectedTimes = session['selectedTimes'] if not session.get('selectedTimes') == None else day_schedule.start_times

        minCapacity = day_schedule.get_session_min_capacity(selectedSessions)
        maxCapacity = day_schedule.get_room_max_capacity()

        # store the form data as dicts that store checkbox states 
        roomProperties = dict.fromkeys(list(day_schedule.get_room_properties()), '')
        roomFormats = dict.fromkeys(list(day_schedule.get_room_formats()), '')
        roomEquipment =  dict.fromkeys(list(day_schedule.get_room_equipment()), '')   
       
        # get the available rooms based on the room filters, sessions, dates & times selected
        avbleRooms = day_schedule.get_filtered_room_availability(selectedDates, selectedTimes, 
                                                                 day_schedule.get_room_properties(), 
                                                                 day_schedule.get_room_equipment() , 
                                                                 maxCapacity, 
                                                                 day_schedule.get_room_formats(), 
                                                                 selectedSessions)
               
        return render_template('Step3.html', properties=roomProperties, min=minCapacity, max=maxCapacity,
                                             formats=roomFormats, avSetups=roomEquipment, availableRooms=avbleRooms) 
        
        


        
@app.route('/StepFour', methods = ['POST', 'GET'])
def stepFour():
    """ Renders the Step4 page. """
    if request.method == 'POST':    
        # Save the generated schedule as a CSV file   
      
        return render_template('Step4.html', schedule=day_schedule.get_scheduled_sessions()) 

    else:
        day_schedule.create_schedule(selectedSessions, selectedRooms, 
                                    session["selectedDates"], session["selectedTimes"])

        return render_template('Step4.html', schedule=day_schedule.get_scheduled_sessions()) 




if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
   


    
