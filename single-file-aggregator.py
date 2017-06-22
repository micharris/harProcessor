# create new file with first entry as timestamp
# create list of all onload times from all the HAR files - calculate the mean - save it as pageload
# loop into first entry - check all files for that entry - build list for matching entries - calculate the mean of the 'time' field.  Save it as 'url':'time'
    # if no matching entries - save the entry with that valued
    # move to next entry in 'entries' array
    # work from the last HAR file - if it's missing entries, then fuck it, don't pick them up from the other files.

# keep the same format as original HAR file so that we can reuse this script to aggregate the runs from different dates

import glob
import json
import statistics
import collections
import time
import sys

ts = str( time.time() )

target = sys.argv[0]
# EG: login/


def set_target_dir():
    if 'aggregated' in target:
        target_dir = target
    else:
        #get the newest subdirectory
        newest_subdir = max(glob.glob(os.path.join(target, '*/')), key=os.path.getmtime)
        return newest_subdir


def set_output_dir(target):
    if 'aggregated' in target:
        output_dir = target
    else:
        output_dir = target+'/aggregated'
    
    return output_dir


def get_data(target_dir, output_dir):
    page_load = []
    page_items = collections.defaultdict(list)

    for filename in glob.iglob(target_dir+'/*.har'):
        #print('/foobar/%s' % filename)
        with open(filename) as json_data:
            d = json.load(json_data)
            #print d
            page_load.append( d['log']['pages'][0]['pageTimings']['onContentLoad'] )
            time_stamp = d['log']['pages'][0]['startedDateTime']

            for item in d['log']['entries']:
                load_time = item['time']
                url = item['request']['url']
                #print load_time
                page_items[url].append( load_time )

    page_load = statistics.median(page_load)
    page_load = ("%.2f" % page_load)
    #print page_load
    #print time_stamp
    aggregate(page_items, page_load, time_stamp, output_dir)


def aggregate(page_items, page_load, time_stamp, output_dir):
    entry_data = ''
    for key in page_items:
        mean = statistics.median(page_items[key])
        mean = ("%.2f" % mean)
        entry_data += '{ "time" : '+str(mean)+', "request" : { "url": "'+key+'"} },'

    entry_data = entry_data[:-1]

    file = open(output_dir+'/'+ts+'-aggregated.har','w') 
     
    file.write('{"log": {"version": "1.2", "creator": {"name": "WebInspector", "version": "537.36"}, "pages": [{"startedDateTime": "'+time_stamp+'", "id": "page_1", "title": "https://presto.gannettdigital.com/", "pageTimings": {"onContentLoad": '+str(page_load)+', "onLoad": 0 } } ],')
    file.write(' "entries": [ ')
    file.write(entry_data)
    file.write(']}}')
    file.close() 

target_dir = set_target_dir(target)
output_dir = set_output_dir(target)
get_data(target_dir, output_dir)