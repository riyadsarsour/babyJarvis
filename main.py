from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import time
import pyaudio
import speech_recognition as sr
import pyttsx3
import subprocess

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
#Global Variables for date adjustment google cal
MONTHS = ["january", "february", "march", "april", "may", "june","july", "august", "september","october", "november", "december"]
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
DAY_EXTENTIONS = ["rd", "th", "st", "nd"]

#take text and speak 
def speak(text):
	engine = pyttsx3.init()
	engine.say(text)
	engine.runAndWait()

    # tts = gTTS(text = text, lang= "en")
    # filename = "voice.mp3"
    # tts.save(filename)
    # playsound.playsound(filename)
    #subprocess.call(['say', text])

#listen to speech
def hearAudio():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		audio = r.listen(source)
		said = ""

		try:
		    said = r.recognize_google(audio)
		    print(said)
		except Exception as e:
		    print("Exception: " + str(e))

	return said

# log in creds for google in general
def authenticate_gCal():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    return service

# pull events off google cal
def get_calEvents(date, service):
    # Call the Calendar API
	date = datetime.datetime.combine(day, datetime.datetime.min.time())
	end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
	utc = pytz.UTC
	date = date.astimezone(utc)
	end_date = end_date.astimezone(utc)
	
	events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                        singleEvents=True,
                                        orderBy='startTime').execute()
	events = events_result.get('items', [])
	if not events:
		speak('No upcoming events found.')
	else:
		speak(f"You have {len(events)} events on this day.")
		
		for event in events:
			start = event['start'].get('dateTime', event['start'].get('date'))
			print(start, event['summary'])
			start_time = str(start.split("T")[1].split("-")[0])
			if int(start_time.split(":")[0]) < 12:
				start_time = start_time + "am"
			else:
				start_time = str(int(start_time.split(":")[0])-12) + start_time.split(":")[1]
				start_time = start_time + "pm"
			speak(event["summary"] + " at " + start_time)

def get_date(text):
	text = text.lower()
	today = datetime.date.today()

	if text.count.count("today") > 0:
		return today
	
	day = -1
	dayOfWeek = -1
	month =-1
	year = today.year

	for word in text.split():
		if word in MONTHS:
			month= MONTHS.index(month) +1
		elif word in DAYS:
			dayOfWeek = DAYS.index(word)
		elif word.isdigit():
			day = int(word)
		else:
			for ext in DAY_EXTENTIONS:
				found = word.find(ext)
				if found > 0:
					try:
						day = int(word[:found])
					except:
						pass 
	if month < today.month and month != -1:  # if the month mentioned is before the current month set the year to the next
		year = year+1
	if month == -1 and day != -1:  # if we didn't find a month, but we have a day
		if day < today.day:
			month = today.month + 1
		else:
			month = today.month

	if month == -1 and day == -1 and dayOfWeek != -1:
		current_day_of_week = today.weekday()
		dif = dayOfWeek - current_day_of_week
		
		if dif < 0:
			dif += 7
			if text.count("next") >= 1:
				dif += 7
		return today + datetime.timedelta(dif)
	if day != -1:  # FIXED FROM VIDEO
		return datetime.date(month=month, day=day, year=year)



WAKE  = "Hey Jarvis"
SERVICE = authenticate_gCal()
while True:
	print("Listening")
	text = hearAudio()
	
	if text.count(WAKE) > 0:
		speak("I am ready")
		text = hearAudio()
		
		CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
		for phrase in CALENDAR_STRS:
			if phrase in text:
				date = get_date(text)
				if date:
					get_calEvents(date, SERVICE)
				else:
					speak("I don't understand")
		
		NOTE_STRS = ["make a note", "write this down", "remember this"]
		for phrase in NOTE_STRS:
			if phrase in text:
				speak("What would you like me to write down?")
				note_text = hearAudio()
				note(note_text)
				speak("I've made a note of that.")	

