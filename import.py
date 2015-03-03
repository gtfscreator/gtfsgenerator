import os
from toolz import itemfilter

route_id = 1

#fileinput = os.path.abspath('input/calendar.csv')
fileinput = os.path.abspath('input/time.csv')
fileoutput = os.path.abspath('output/stop_time.csv')

#stops = ['stop_id', 'stop_name', 'stop_desc', 'stop_lat', 'stop_lon', 'stop_url', 'location_type', 'parent_station']


def parse_time(row,row_number):
    d = {}
    #if row_number == 0:
    #    pass
    d['stop_id'] = row.split(',') [0]
    #d['time'] = row.split(',') [1]
    print row.split(',')
    return d


def write_stops(fileoutput, stop_id, stop_name = '',stop_desc = '',stop_lat = '',stop_lon = '',stop_url = '',location_type = '',parent_station = ''):
    fileoutput.write(stop_id + ',' + stop_name + ',' + stop_desc + ',' + stop_lat + ',' + stop_lon + ',' + stop_url + ',' + location_type + ',' + parent_station + '\n')


def write_trips(fileoutput,route_id,service_id,trip_id,trip_headsign,block_id):
    fileoutput.write(route_id + ',' + service_id + ',' + trip_id + ',' + trip_headsign + ',' + block_id)

def write_stop_times():
    pass

def write_calendar(service_id):
    pass

def write_calendar_dates():
    pass

def main():
    f_i = open(fileinput, 'rU')
    f_o = open(fileoutput, 'w')
    for row_number,row in enumerate(f_i):
        write_stops (f_o,**parse_time(row,row_number))


if __name__ == "__main__":
    main()
