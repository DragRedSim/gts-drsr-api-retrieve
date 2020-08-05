import argparse
import requests
import json
import time

parser = argparse.ArgumentParser(description="Calls the GTS API for a specific User ID, and reports the latest DR value")
parser.add_argument('user_no', metavar='user_id', type=str, help='The User ID of the driver to report. Obtained from the URL of their profile page on the GTS community website.')
parser.add_argument('-d', '--hide_dr', default=False, action='store_true', help='Disable showing the DR value')
parser.add_argument('-s', '--hide_sr', default=False, action='store_true', help='Disable showing the SR value')
parser.add_argument('-o', '--runonce', default=False, action='store_true', help='Run once and exit (default is to continue running and updating every 60 seconds)')
args = parser.parse_args()

request_params = {'job': 3, 'user_no': args.user_no}

def mainLoop():
	print('Checking DR/SR')
	f = requests.post('https://www.gran-turismo.com/us/api/gt7sp/profile/',data=request_params)
	data = f.json()
	
	if args.hide_dr == False: 
		driver_point = int(data['stats']['driver_point'])
		if (driver_point >= 50000):
			dr_letter = "A+"
		elif (driver_point >= 30000):
			dr_letter = "A"
		elif (driver_point >= 10000):
			dr_letter = "B"
		elif (driver_point >= 5000):
			dr_letter = "C"
		else:
			dr_letter = "D"
	
	if args.hide_sr == False:
		manner_point = int(data['stats']['manner_point'])
		if (manner_point > 80):
			sr_letter = "S"
		elif (manner_point > 65):
			sr_letter = "A"
		elif (manner_point > 40):
			sr_letter = "B"
		elif (manner_point > 20):
			sr_letter = "C"
		elif (manner_point > 10):
			sr_letter = "D"
		else:
			sr_letter = "E"
	
	with open("drstatus.txt", "w") as output_text:
		if args.hide_dr == False: print("DR: " + str(driver_point) + " (" + dr_letter + ")", file=output_text)
		if args.hide_sr == False: print("SR: " + str(manner_point) + " (" + sr_letter + ")", file=output_text)
		
while True:
	mainLoop()
	if args.runonce == True: break
	time.sleep(60)