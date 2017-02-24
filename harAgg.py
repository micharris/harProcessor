import re
import time
import datetime 
import os
import numpy as np

regex = re.compile("/imgad\?id=CICA")
regex_start = re.compile("startedDateTime")

duration_list = []
load_time_list = []

for filename in os.listdir("har_files"):
	fp = open("har_files/"+filename)
	lines = fp.readlines()
	num_lines = len(lines)
	got_time = True;
	time_list = []

	i = 0
	while i < num_lines:
		if got_time == True:
			if regex_start.search(lines[i]):
				got_time = False;
				start_time = lines[i].split('"')
				start_time = start_time[3]
				start_time = start_time[:-1]

		if regex.search(lines[i]):
			duration = lines[i-3]
			duration = duration.split(":")
			duration = duration[1]
			duration = duration[:-2]
			duration = duration.strip()
			if duration != "":
				duration = float(duration)
				duration_list.append(duration)
			time_start = lines[i-4]
			time_start = time_start.split('"')
			time_start = time_start[3]
			if time_start != "unknown":
				time_start = time_start[:-1]
				time_list.append(time_start)

		i = i+1

	try:
		if len(time_list) > 0 :
			time_list = time_list[1] #first entry is always wrong timestamp
			duration_val = duration_list[1]
		else:
			time_list = time_list[0] #first entry is always wrong timestamp
			duration_val = duration_list[0]

		dt = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%f")
		epoch = datetime.datetime.fromtimestamp(0)
		start_time = (dt - epoch).total_seconds()

		dt = datetime.datetime.strptime(time_list, "%Y-%m-%dT%H:%M:%S.%f")
		epoch = datetime.datetime.fromtimestamp(0)
		end_time = (dt - epoch).total_seconds()
		total_time = end_time - start_time
		load_time_list.append(total_time)
	except IndexError:
		error = IndexError

#print load_time_list
#print duration_list

print "time to init: "+str(np.mean(load_time_list))+" seconds"
print "load time after init: "+str(np.mean(duration_list))+" milliseconds"
