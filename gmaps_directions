import datetime
import os

import math
import statistics
from collections import namedtuple
from typing import *
import googlemaps
import joblib
from rich import print
from tqdm import tqdm
import better_exceptions
better_exceptions.hook()

MAPS_KEY_FOR_DIRECTION_GEOLOC = os.environ["GMAPS_KEY"]
cache_wrapper_get_from_to = joblib.Memory(f'/tmp/aio-cache/transit22/{datetime.date.today()}', verbose=False)
RouteAnalysis = namedtuple('RouteAnalysis', 'avg_duration,min_duration,max_duration,durations,objects')

DATETIMES = [
            datetime.datetime(2020, 5, 21, 18, 0, 0),
            datetime.datetime(2020, 5, 21, 17, 30, 0),
            datetime.datetime(2020, 5, 21, 18, 30, 0),
            datetime.datetime(2020, 5, 21, 19, 0, 0)
             ]


gmaps = googlemaps.Client(key=MAPS_KEY_FOR_DIRECTION_GEOLOC)

# Geocoding an address
addr_work = "Raffelstrasse 22, Zurich"
addr_apt = 'Vulkanplatz 27, Zurich'

geocode_work = gmaps.geocode(addr_work)
geocode_apt = gmaps.geocode(addr_apt)
print ('geocode_work=',geocode_work)
print ('geocode_apt', geocode_apt)


@cache_wrapper_get_from_to.cache
def wrapper_get_from_to(source, destination, time):
    directions_result = gmaps.directions(source,
                                         destination,
                                         mode="transit",
                                         departure_time=time,
                                         alternatives=True)
    nonce=222

    return directions_result



def get_travel_times_sec(route_objects:List[dict]) -> List[float]:
    def get_duration_seconds(travel_obj):
        try:
            return travel_obj['legs'][0]['duration']['value']
        except KeyError as e:
            print ("||||||||||||||| BAD OBJECT")
            print (travel_obj)
            raise

    return list(map(get_duration_seconds, route_objects))




def travel_times_for_route(source, destination):
    leave_times = DATETIMES

    travel_objects = []

    for leave_at in DATETIMES:
        for route_j in  wrapper_get_from_to(source, destination, leave_at):
            travel_objects.append(route_j)

    durations = get_travel_times_sec(travel_objects)
    avg_duration = statistics.mean(durations)
    min_duration = min(durations)
    max_duration = max(durations)

    return RouteAnalysis(avg_duration,min_duration,max_duration,durations,travel_objects)


def pretty_time(seconds:float):
    return f"{int(seconds)/60:.2f} min"


def pretty_route(ra:RouteAnalysis):
    return(f"""
    avg={pretty_time(result.avg_duration)} ({pretty_time(ra.min_duration)}..{pretty_time(ra.max_duration)})
    """)

def extract_addrs(msg):
    pass

def inbound_email(msg):
    addrs = extract_addrs()


if __name__ == "__main__":
    result = (travel_times_for_route(addr_work, addr_apt))

    print(pretty_route(result))
