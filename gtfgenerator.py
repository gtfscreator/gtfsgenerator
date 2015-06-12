import sys
import os
import csv
import itertools
import datetime
import json

class InvalidStopError(Exception):
    pass


ROUTE_DATA = {
    "short_name" : "test",
    "long_name" : "test",
    "agency_id" : "1",
    "route_type" : 2
}


def validate_stop(stop):
    return True


def load_stops(filename):
    out = []
    with open(filename) as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if not validate_stop(row):
                raise InvalidStopError
            row['stop_id'] = i
            out.append(row)
        #print reader
    return out

def load_times(route_id, filename):



    with open(filename) as f:
        
        #trips = f.readline().replace("\n", "").split(",")
        services = f.readline().replace("\n", "").split(",")

        trips = {}
        for s, service in enumerate(services[1:]):
            trip_id = route_id + "_" + str(s)
            trips[trip_id] = { "service_id" : service, "stops":{}}


        stops = []

        for line in f.readlines():
            line = line.replace("\n", "")
            pieces = line.split(",")
            
            stop_name = pieces[0]
            stops.append(stop_name)
            for i, p in enumerate(pieces[1:]):
                trip_id = route_id + "_" + str(i)
                if p:
                    trips[trip_id]['stops'][stop_name] = p

        
        #print trips
        stop_times = []
        for trip_id in trips:
            trip_stop_times = []
            service_id = trips[trip_id]["service_id"]
            for stop, time in trips[trip_id]['stops'].items():
                trip_stop_times.append((time, stop))
            trip_stop_times = sorted(trip_stop_times)
            headsign = trip_stop_times[-1][1]
            #print trip_stop_times
            for i, x in enumerate(trip_stop_times):
                stop_time = {"trip_id" : trip_id, "stop_id" : x[1], "stop_time":x[0], "stop_sequence":i, "service_id":service_id, "trip_headsign":headsign}
                stop_times.append(stop_time)

        out_stops = []    
        out_trips = []
        tps = {}

        for x in stop_times:
            s = {k: x[k] for k in ('stop_sequence', 'trip_id', 'stop_id')}
            s['departure_time'] = x['stop_time' ]
            s['arrival_time'] = x['stop_time' ]
            s['time_point'] = 0
            out_stops.append(s)

            if x['trip_id'] not in tps:
                t  = {k: x[k] for k in ('service_id', 'trip_headsign', 'trip_id')}
                t['route_id'] = route_id
                out_trips.append(t)
                tps[x['trip_id']] = True

        return out_stops, out_trips



def generate_calendar(filename):
    out_calendar = []
    out_calendar_dates = []
    with open(filename) as f:
        reader = csv.reader(f)
        header = reader.next()
        fixed_header = header[:10]
        for row in reader:
            clean_row = [x for x in row if x]
            lr = len(clean_row)
            if lr > 10:
                diff = lr-10
                for k in range(diff/2):
                    start_date = row[10+k*2]
                    end_date = row[11+k*2]

                    s = datetime.datetime.strptime(start_date, "%Y/%M/%d")
                    e = datetime.datetime.strptime(end_date, "%Y/%M/%d")
                    while s < e:
                        r = { "service_id":row[0], "date" : datetime.datetime.strftime(s, "%Y/%M/%d"), "exception_type" : 2}
                        s = s + datetime.timedelta(days=1)
                        out_calendar_dates.append(r)
                
                
            else:
                out_calendar.append(dict(zip(fixed_header, clean_row)))


    return  out_calendar, out_calendar_dates







def generate_route(route_id, route_data):
    return route_data.update({"route_id" : route_id})


def generate_stops_stimes(times):
    for t in times:
        pass



def generate_gtfs_data(folder):
    """
    Takes a folder, validates files and generates gtfs
    """

    route_id = os.path.basename(folder)

    route = generate_route(route_id, ROUTE_DATA)

    times_file = os.path.join(folder, "time.csv")
    stop_times, trips = load_times(route_id, times_file)
    
    #stop_times = generate_stops_times(times)
    #trips = generate_trips()


    return {
        "trips": trips,
        "stop_times" : stop_times,
        "routes" : [route]
    }


def merge_gtfs_data(gtfs_data_dict):

    keys = ["trips", "stop_times", "routes"]
    out = { k:[] for k in keys}

    for route_id, data in gtfs_data_dict.items():
        for k in keys:
            out[k].extend(data[k])

    return out


def parse_agency_folder(folder):

    gtfs_data = {}

    stops_file = os.path.join(folder, "stops.csv")
    stops = load_stops(stops_file)

    calendar_file = os.path.join(folder, "calendar.csv")
    calendar, calendar_dates = generate_calendar(calendar_file)


    files = os.listdir(folder)
    for f in files:
        full_f = os.path.join(folder, f)
        if os.path.isdir(full_f):
            gtfs_data[f] = generate_gtfs_data(full_f) 
            
    final_gtfs_data = merge_gtfs_data(gtfs_data)

    out = {
        "stops" : stops,
        "calendar" : calendar,
        "calendar_dates" : calendar_dates
    }        

    out.update(final_gtfs_data)


    return out


def serialize_gtfs(data):

    mp = {
        'stops' : ['stop_id','stop_name','stop_desc','stop_lat','stop_lon','stop_url','location_type','parent_station'],
        'trips' : ['route_id','service_id','trip_id','trip_headsign','block_id'],
        'stop_times' : ['trip_id','arrival_time','departure_time','stop_id','stop_sequence','pickup_type','drop_off_type', 'time_point'],
    }

    for d in data:
        out_file = os.path.join('output', d+".txt")
        if d not in mp:
            continue
        with open(out_file, "wb") as f:
            writer = csv.DictWriter(f, delimiter=",", quoting=csv.QUOTE_ALL, fieldnames=mp[d])
            writer.writeheader()
            writer.writerows(data[d])



def main(folder):
    gtfs_data = parse_agency_folder(folder)
    #print json.dumps(gtfs_data, indent=4)
    serialize_gtfs(gtfs_data)
    #print gtfs_data


if __name__ == '__main__':
    folder = sys.argv[1]
    main(folder)