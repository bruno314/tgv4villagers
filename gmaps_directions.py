import copy
import datetime
import time
import os
import math
import statistics
from collections import namedtuple
from typing import *
import googlemaps
import joblib
import random
import re
import requests
from rich import print
from tqdm import tqdm
import better_exceptions
better_exceptions.hook()

MAPS_KEY_FOR_DIRECTION_GEOLOC = os.environ["GMAPS_KEY"]
hit_only_once_semi_pure = joblib.Memory(f'/tmp/aio-cache/transit22/{datetime.date.today()}', verbose=False)
RouteAnalysis = namedtuple('RouteAnalysis', 'avg_duration,min_duration,max_duration,durations,objects')

DATETIMES = [
            datetime.datetime(2020, 5, 21, 18, 0, 0),
            datetime.datetime(2020, 5, 21, 17, 30, 0),
            datetime.datetime(2020, 5, 21, 18, 30, 0),
            datetime.datetime(2020, 5, 21, 19, 0, 0)
             ]

addr_work = "Raffelstrasse 22, Zurich"
addr_apt = 'Vulkanplatz 27, Zurich'
ZurichHB = "Zurich HB Main Station"
###################################################################################

gmaps = googlemaps.Client(key=MAPS_KEY_FOR_DIRECTION_GEOLOC)

# Geocoding an address


geocode_work = gmaps.geocode(addr_work)
geocode_apt = gmaps.geocode(addr_apt)
print ('geocode_work=',geocode_work)
print ('geocode_apt', geocode_apt)


@hit_only_once_semi_pure.cache
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
    avg={pretty_time(ra.avg_duration)} ({pretty_time(ra.min_duration)}..{pretty_time(ra.max_duration)})
    """)

def extract_links_from_mail(msg:str):
    pass

@hit_only_once_semi_pure.cache
def wrapper_immo_once(url):

    time.sleep(3) #take that, replace by poisson
    print("[bold red]*HITTING SERVER*[/bold red]")
    try:
        return requests.get(url).text
    except Exception as e:
        print(e)
        raise


def extract_coord(link):
    res = wrapper_immo_once(link)

    coordregexp = re.compile(r'maps.google.com/maps\?cbll=(.*)%2C(.*?)&amp')
    try:
        return re.findall(coordregexp, res)[0]
    except IndexError:
        print("[bold magenta]failed assumption (regexp GPS)[/bold magenta]")
    except Exception:
        raise('uwotm8')

def inbound_email(msg):

    # links = extract_links_from_mail()

    links= [
        'https://www.immomapper.ch/en/objekts/GaolJrOA61-apartment-for-rent-in-uster-zh?utm_source=search_abo_email&utm_medium=email',
        'https://www.immomapper.ch/en/objekts/omzdJ97L6A-apartment-for-rent-in-uster-zh?utm_source=search_abo_email&utm_medium=email'
    ]

    gps_coord = {link:{'coord':extract_coord(link)} for link in links}
    return gps_coord

def patch_with_times(apts:dict):
    apts = copy.deepcopy(apts)

    for url in apts.keys():
        apts[url]['time'] = pretty_route(travel_times_for_route(ZurichHB, apts[url]['coord']))

    return apts

if __name__ == "__main__":
    print (patch_with_times(inbound_email('')))





