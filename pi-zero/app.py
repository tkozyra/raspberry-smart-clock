from flask import Flask, jsonify, request, session, redirect, url_for, escape, Session, make_response, send_from_directory

import os, sys, os.path
import functools
import time
from dateutil import parser
import traceback
import config
import logging
from datetime import datetime
import drivers
from alarm import *
display = drivers.Lcd()

clock_running = False
saved_time = False

WEEKDAYS = {"Mo": 0, "Tu": 1, "We": 2, "Th": 3, "Fr": 4, "Sa": 5, "Su": 6}
WEEKDAYS_REVERSE = {v: k for (k, v) in WEEKDAYS.iteritems()}

app = Flask(__name__)

@app.route("/<path:path>")
def static_content(path):
    return send_from_directory('build/', path)

@app.route("/")
def index():
	return send_from_directory('build/', "index.html")
	
@app.route("/stat")
def stat():
	stat = {}
	status = "None"
	if app.alarm.days_of_week:
		stat = json.loads(repr(app.alarm))
		stat["time"] = parser.parse(stat["time"]).strftime("%H:%M:%S")
		stat["weekdays"] = [WEEKDAYS[x] for x in stat ["weekdays"]]
		status = "OK"
	return jsonify({"status": status, "stat": stat})

@app.route("/set2", methods=["POST"])
def set2():
	data = request.get_json(force=True)
	args = request.args
	date_time = parser.parse(args["time"])
	days_of_week = [WEEKDAYS[x] for x in data["daysOfTheWeek"] if x in WEEKDAYS and data["daysOfTheWeek"][x] == True]
	app.alarm.times_of_week = TimesOfWeek(date_time, days_of_week)
	app.alarm.to_file(app.statePath)
	return jsonify({"status": "OK"})

@app.route("/clear", methods=["GET"])
def clear():
	print("Clearing alarm...")
	date_time = datetime.datetime.now()
	days_of_week = []
	app.alarm.times_of_week = TimesOfWeek(date_time, days_of_week)
	app.alarm.to_file(app.statePath)
	return jsonify({"status": "OK"})

def main():
	app.statePath = config.statePath
	app.alarm = Alarm()
	if os.path.exists(app.statePath):
		try:
			app.alarm = Alarm.from_file(app.statePath)
		except Exception as e:
			os.remove(app.statePath)
			print("Cannot read app-state from " + app.statePath, e)

	print("Starting with alarm", str(app.alarm))
	app.alarm.start()
	app.run(host=config.host, port=config.port, threaded=config.threaded)

if __name__ == "__main__":
	main()
