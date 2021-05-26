
#!/usr/bin/python3
import RPi.GPIO as GPIO
import sys
import os
import signal
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
import datetime
from time import sleep
import drivers
display = drivers.Lcd()
import threading
import subprocess
import time
import sys
import json
import collections
from dateutil import parser

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
prev_input = GPIO.input(17)

### SPOTIFY CONFIG ###
username = 'YOUR_USERNAME'
playlist = 'SPOTIFY_PLAYLIST_LINK'
spotconnect_device_name = 'raspotify (raspberrypi)'
SP_CLIENT_ID = 'YOUR_CLIENT_ID'
SP_CLIENT_SECRET = 'YOUR_CLIENT_SECRET'
SP_REDIRECT_URI = 'http://localhost/'
######################

global alarm_turned_off
alarm_turned_off = False
global alarm_run
alarm_run = True
global alarm_process
alarm_process = None

global alarm_playing
alarm_playing = None

global token
global playing
global device
token = ''
playing = False
device = ''
scope = 'user-library-read, user-read-playback-state, user-modify-playback-state'

def initializeAccess():
    print('Initializing access')
    global token
    auth_manager=SpotifyOAuth(username=username, scope=scope, client_id=SP_CLIENT_ID, client_secret=SP_CLIENT_SECRET,redirect_uri=SP_REDIRECT_URI, open_browser=False)
    token=auth_manager.get_access_token(as_dict=False)
    print('Created token:', token)

def initializeDevices():
    print('Initializing device')
    global token
    try:
        global device
        sp = spotipy.Spotify(auth=token)
        devices = sp.devices()
        devices = devices['devices']
        dictionary = {}
        for item in devices:
            dictionary[item['name']] = item['id']
        device = dictionary[spotconnect_device_name]
        print('Device resolved as', device)
    except:
        print('Cannot initialize device - emptying token')
        token = ''

def spotifyPlayStop():
    global token
    global playing
    try:
        if playing:
            print('Currently playing - trying to stop')
            sp = spotipy.client.Spotify(auth=token)
            sp.pause_playback()
            playing = False
        else:
            print('Not playing - trying to start')
            sp = spotipy.Spotify(auth=token)
            sp.start_playback(device_id=device, context_uri=playlist)
            sp.shuffle(True)
            sp.next_track()
            playing = True
    except:
        print('Cannot change state - emptying token')
        token = ''
        initializeAccess()
        spotifyPlayStop()

def spotifyStop():
		global token
		global playing
		try:
				if playing:
					print('ALARM - STOPPING MUSIC')
					sp = spotipy.client.Spotify(auth=token)
					sp.pause_playback()
					playing = False
		except:
				print('Cannot change state - emptying token')
				token = ''
				initializeAccess()

custom_char_mapping = {
                    "[bell]": {"address": 1,
                                "character":
                                [
                                0b00100,
                                0b01110,
                                0b01110,
                                0b01110,
                                0b11111,
                                0b00000,
                                0b00100,
                                0b00000]},
                    "[heart]": {"address": 2,
                                 "character":
                                 [
                                 0b00000,
                                 0b01010,
                                 0b11111,
                                 0b11111,
                                 0b01110,
                                 0b00100,
                                 0b00000,
                                 0b00000]}
                }

TimesOfWeek = collections.namedtuple("WeekTimes", ["time_of_day", "days_of_week"])
EMPTY_TIMES_OF_WEEK = TimesOfWeek(datetime.datetime.now(), [])

def print_on_lcd(display, message, line):
		for key in custom_char_mapping.keys():
			message = message.replace(key, chr(custom_char_mapping[key]["address"]))
		display.lcd_display_string(message, line)

class Alarm(threading.Thread):
	def __init__(self, times_of_week=EMPTY_TIMES_OF_WEEK, length=30):
		super(Alarm, self).__init__()
		self._times_of_week = times_of_week
		self.length = length
		self.setDaemon(True)
		self._is_finished = False
		self._lock = threading.Lock()

	@property
	def time_of_day(self):
		#the time of day at which the alarm is set
		return self.times_of_week.time_of_day

	@property
	def days_of_week(self):
		#the days of the week the alarm is set for
		return self.times_of_week.days_of_week

	@property
	def is_finished(self):
		with self._lock:
			return self._is_finished

	@is_finished.setter
	def is_finished(self, is_finished):
		with self._lock:
			self._is_finished = is_finished

	@property
	def times_of_week(self):
		with self._lock:
			return self._times_of_week

	@times_of_week.setter
	def times_of_week(self, times_of_week):
		with self._lock:
			self._times_of_week = times_of_week

	def run(self):
		display.lcd_clear()
		print("running alarm")
		global alarm_turned_off
		alarm_turned_off = False
		global alarm_run
		alarm_run = True

		for key in custom_char_mapping.keys():
			display.set_custom_char(custom_char_mapping[key]["address"] << 3, custom_char_mapping[key]["character"])
		while not self.is_finished:
			try:
				self.tick()
			except Exception as e:
				print(sys.exc_info()[0])

	def tick(self):
		now = datetime.datetime.now()
		idle = 0
		global token
		global prev_input
		global alarm_turned_off
		global alarm_run
		global alarm_process
		global alarm_playing

		if now.weekday() in self.days_of_week and now.strftime("%H:%M") == self.time_of_day.strftime("%H:%M") and not alarm_turned_off:
			alarm_playing = True
		elif not (now.weekday() in self.days_of_week and now.strftime("%H:%M") == self.time_of_day.strftime("%H:%M")):
			alarm_turned_off = False

		if token == '':
				initializeAccess()
				initializeDevices()
		if idle == 3600:
				idle = 0
				token = ''
		else:
				idle += 1

		print_on_lcd(display, str(now.strftime("%a, %d.%m.%Y")), 1)

		if not alarm_turned_off and alarm_playing and alarm_process is None:
			print_on_lcd(display, str(now.strftime("   [bell] %H:%M:%S")), 2)
			spotifyStop()
			print("RUNNING ALARM SUBPROCESS")
			alarm_process = subprocess.Popen(['aplay ./alarm.wav'], shell=True, preexec_fn=os.setsid)
			alarm_turned_off = True
		elif not alarm_playing:
			print_on_lcd(display, str(now.strftime("   [heart] %H:%M:%S")), 2)
			input_state = GPIO.input(17)
			if input_state != prev_input:
					if input_state == 1:
							spotifyPlayStop()
			prev_input = input_state

		if alarm_playing and alarm_process is not None:
			print_on_lcd(display, str(now.strftime("   [bell] %H:%M:%S")), 2)
                        input_state = GPIO.input(17)
			if input_state != prev_input:
					if input_state == 1:
							print("KILLING ALARM")
							os.killpg(os.getpgid(alarm_process.pid), signal.SIGTERM)
							alarm_playing = False
							alarm_process = None
			prev_input = input_state

	def __repr__(self):
		return json.dumps({"time": self.time_of_day.isoformat(),
			"weekdays": self.days_of_week,
			"length": self.length})

	def to_file(self, file_name):
		with open(file_name, "w") as f:
			f.write(repr(self))

	@staticmethod
	def load(state_dict):
		times_of_week = TimesOfWeek(
			parser.parse(state_dict["time"]),
			state_dict["weekdays"])

		return Alarm(times_of_week,
			state_dict["length"])

	@staticmethod
	def from_file(file_path):
		with open(file_path, "r") as f:
			state_dict = json.load(f)
			return Alarm.load(state_dict)

if __name__ == "__main__":
	import pdb; pdb.set_trace()
	alarm = Alarm(TimesOfWeek(datetime.datetime.now(), [0, 1, 2, 3]))
	state_path = "alarm.state.json"
	alarm.to_file(state_path)
	state2 = Alarm.from_file(state_path)
	print("state2", state2)
	print("alarm started")
	alarm.is_finished = True
