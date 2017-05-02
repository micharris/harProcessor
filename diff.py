# loop through pageLoad and entries in latest aggregated file
# compare against the rolling mean aggregated file
# if there is an entry match:
    # then if the latest agg file entry is 20% higher value or more
        # then add that entry key to a list

# after looping through the lastest agg file and rolling mean file
# using the list, get all the previous agg values for each entry in the list and put in dict (endpoint: value, value, value, value)
# build a google graph using that data
# graph should show the endpoint, values line, and timestamp for each value point 

import glob
import os
import json
import statistics
import collections
import time
import sys

target_dir = sys.argv[0]
ts = str( time.time() )

# compares the last run against the rolling means and finds endpoints that exceed 10% slower
def get_diff_array(rolling_mean, last_run):
    diff_array = []
    with open(last_run) as last_data:
        with open(rolling_mean) as rolling_data:
            rolling = json.load(rolling_data)
            last = json.load(last_data)

            rolling_page_load = rolling['log']['pages'][0]['pageTimings']['onContentLoad']
            last_page_load = last['log']['pages'][0]['pageTimings']['onContentLoad']
            load_diff = last_page_load / rolling_page_load

            if( load_diff >= 1.1 ):
                diff_array.append('page_load')

            for last_item in last['log']['entries']:
                for rolling_item in rolling['log']['entries']:
                    if( last_item['request']['url'] == rolling_item['request']['url']):
                        last_item_load = last_item['time']
                        roll_item_load = rolling_item['time']
                        item_diff = last_item_load / roll_item_load
                        
                        #print "last_run: "+str(last_item_load)+" : "+last_item['request']['url']
                        #print "rolling: "+str(roll_item_load)+" : "+rolling_item['request']['url']
                        if( item_diff >= 1.1 ):
                            diff_array.append( last_item['request']['url'] )

    return diff_array



def get_last_run(target_dir):
    list_of_files = glob.glob(target_dir+'/aggregated/*.har') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


def get_rolling_aggregate(target_dir):
    list_of_files = glob.glob(target_dir+'/*.har') # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file


# load each file - up to 20 in chronological order
# pull the endpoints that match the diff list 
# create dict with endpoint as key and value 
    # if endpoint missing from that file - set value as 'null'
def get_history(diff_array):
    i = 0
    page_items = collections.defaultdict(list)
    date_list = []
    row = ''

    for filename in glob.iglob(target_dir+'/aggregated/*.har'):
        if (i == 20):
            break

        with open(filename) as json_data:
            d = json.load(json_data)
            page_items['page_load'].append( d['log']['pages'][0]['pageTimings']['onContentLoad'] )
            
            date_val = d['log']['pages'][0]['startedDateTime']
            date_val = date_val[5:-5]
            date_val = date_val.replace("T"," ")
            date_list.append(date_val)
            row += '["'+date_val+'",'

            for endpoint in diff_array:
                match = False

                for item in d['log']['entries']:
                    if( endpoint == item['request']['url'] ):
                        row += str(item['time'])+","
                        match = True
                if match == False:
                    row += 'null,'

            row = row[:-1]+"],"

        i += 1
    
    row = row[:-1]
    #print row

    return {'row':row, 'urls':diff_array, 'date_list': date_list}


def create_graph(target_dir, data):
    target = open(target_dir+'/graphs/'+ts+'.html', 'w')

    target.write('<html><head> <!--Load the AJAX API--> <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script> <script type="text/javascript">')
    target.write(' google.charts.load("current", {"packages":["corechart"]}); google.charts.setOnLoadCallback(drawChart); function drawChart() {var data = new google.visualization.DataTable();')
    
    target.write('data.addColumn("string", "Date");')

    for urls in data['urls']:
        target.write('data.addColumn("number", "'+urls+'");')

    target.write('data.addRows([')
    target.write(data['row'])

    target.write(']);')

    target.write('var options = {title:"Slowing Endpoints", hAxis:{direction:-1, slantedText:true, slantedTextAngle:45},hAxis:{title:"Date of run"}, vAxis:{title:"Load Time Milliseconds"},\
         "width":1600, "lineWidth": 2, "curveType": "none", "height":800};')
    target.write(' var chart =  new google.visualization.LineChart(document.getElementById("chart_div")); chart.draw(data, options); } </script> </head>')
    target.write(' <body> <!--Div that will hold the pie chart--> <div id="chart_div"></div> </body> </html>')
    target.close()


rolling_mean = get_rolling_aggregate(target_dir)
last_run = get_last_run(target_dir)
diff_array = get_diff_array(rolling_mean, last_run)
data = get_history(diff_array)
create_graph(target_dir, data)
