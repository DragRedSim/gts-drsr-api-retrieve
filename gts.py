import argparse
import requests
import json
import time
import configparser
import re
import os

parser = argparse.ArgumentParser(description="Calls the GTS API for a specific User ID, and reports the latest DR value")
parser.add_argument('username', metavar='user_id', type=str, help='The GTS User ID or PlayStation Network ID of the driver to get info for. GTS User ID can be obtained from the URL of their profile page on the GTS community website.')
parser.add_argument('-d', '--hide_dr', default=False, action='store_true', help='Disable showing the DR value')
parser.add_argument('-s', '--hide_sr', default=False, action='store_true', help='Disable showing the SR value')
parser.add_argument('-f', '--separate_files', default=False, action='store_true', help='Write each value to separate files. Assumed if --hide_dr is used.')
parser.add_argument('-i', '--interval', default=60, type=int, help='Set the interval to update the values, in seconds. Defaults to 60. Minimum of 60 in order to avoid getting access refused.')
parser.add_argument('-o', '--runonce', default=False, action='store_true', help='Run once and exit (default is to continue running and updating)')
args = parser.parse_args()

config = configparser.ConfigParser()
termsize = os.get_terminal_size().columns - 1

def initConfig():
	time.sleep(0)
	#we'll need this later, just defining it as effectively a no-op for now

def getUserIDFromTextName():
	config.read('gtsapi.ini')
	username = str.lower(args.username)
	if username in config.sections():
		# we have the ID already
		user_no = config[username]['id']
	else:
		# get KudosPrime
		kudos_request_params = {'mode': 'get_profile_by_name', 'output': 'links', 'online_id[]': args.username}
		kudos_info = requests.post('https://www.kudosprime.com/gts/gt_com_api.php', data=kudos_request_params)
		kudos_response_text = kudos_info.text
		user_no = re.search(r'(?<==)\d+',kudos_response_text)[0]
		username = re.search(r'(?<=">)\w+',kudos_response_text)[0].lower()
		config.add_section(username)
		config.set(username, 'id', user_no)
		with open('gtsapi.ini', 'w') as ini:
			config.write(ini)
	return int(user_no)
		
def mainLoop():
	print('Checking DR/SR'.ljust(termsize), end='\r')
	f = requests.post('https://www.gran-turismo.com/us/api/gt7sp/profile/',data=gt_request_params)
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
	
	if args.separate_files == True:
		with open("drstatus.txt", "w") as dr_output_text:
			if args.hide_dr == False: print("DR: " + str(driver_point) + " (" + dr_letter + ")", file=dr_output_text)
		with open("srstatus.txt", "w") as sr_output_text:
			if args.hide_sr == False: print("SR: " + str(manner_point) + " (" + sr_letter + ")", file=sr_output_text)
	
	if args.hide_dr == True:
		with open("srstatus.txt", "w") as sr_output_text:
			if args.hide_sr == False: print("SR: " + str(manner_point) + " (" + sr_letter + ")", file=sr_output_text)
	else:
		with open("drstatus.txt", "w") as output_text:
			if args.hide_dr == False: print("DR: " + str(driver_point) + " (" + dr_letter + ")", file=output_text)
			if args.hide_sr == False: print("SR: " + str(manner_point) + " (" + sr_letter + ")", file=output_text)


if args.username.isnumeric():
	gt_request_params = {'job': 3, 'user_no': int(args.username)}
else:
	gt_request_params = {'job': 3, 'user_no': getUserIDFromTextName()}
	
while True:
	mainLoop()
	if args.runonce == True: break
	for i in range (max(60, args.interval), 0, -1):
		if i != 1:
			print('Updating in %d seconds...'.ljust(termsize) % i, end='\r')
		else:
			print('Updating in 1 second...'.ljust(termsize), end='\r')
		time.sleep(1)
	
