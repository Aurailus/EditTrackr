from pypresence import Presence
from pyxhook import HookManager
import time
import os

arraylength = 5 #Smoothness of log in val/4 secs

key_history = [None] * arraylength
last_wpm = 0
wpm = 0
curr_minute = round(time.time()/60)

last_keypress = int(time.time());

for x in range(arraylength):
	key_history[x] = 0

pointer = 0

cli_id = 'your_client_id_here'
RPC = Presence(cli_id)

def getProjectAndFile():
	command = os.popen('wmctrl -l')
	windows = command.read()

	project = ""
	file = ""

	for window in windows.splitlines():
		if "Sublime Text" in window:
			projectStart = window.find("(")+1
			projectEnd = window.find(")")

			if (projectStart > 0 and projectEnd > 0):
				project = window[projectStart:projectEnd]

			fileStart = window.rfind("/")+1
			fileEnd = window[0:projectStart].rfind(" ")

			if (fileStart > 0 and fileEnd > 0):
				file = window[fileStart:fileEnd]

	return {"file": file, "project": project}



def OnKeyPress(key):
	global last_keypress, wpm

	key_history[pointer] += 1;
	last_keypress = int(time.time())

	wpm += 0.2


hook = HookManager()
hook.KeyDown = OnKeyPress
hook.HookKeyboard()
hook.start()

def avg_keys_per_second():
	return round(sum(key_history[0:arraylength]) / (arraylength/4), 2)

RPC.connect()

def update_rpc():
	global curr_minute, last_wpm, wpm

	if (round(time.time()/60) != curr_minute):
		last_wpm = wpm
		wpm = 0
		curr_minute = round(time.time()/60)

	prinfo = getProjectAndFile()
	current_time = int(time.time())

	state_string = ""
	state_image = ""

	if (current_time - last_keypress < 5):
		state_string = "Active"
		state_image = "green"
	elif (current_time - last_keypress < 120):
		state_string = "Thinking"
		state_image = "yellow"
	elif (current_time - last_keypress < 240):
		state_string = "Inactive"
		state_image = "red"
	else:
		state_string = "Dead"
		state_image = "off"

	RPC.update(
		state="Project " + prinfo["project"] + "/" + prinfo["file"], 
		details=str(avg_keys_per_second()) + " kps | " + str(last_wpm) + " wpm",
		start=last_keypress,
	  small_text=state_string,
	  small_image=state_image,
	  large_text="EditTrackr",
	  large_image="logo"
	)

getProjectAndFile()

while True:
	time.sleep(0.25)
	pointer += 1
	pointer%=5
	key_history[pointer] = 0
	update_rpc()