#FHT-METAR
#Author FHT
#2022-02-22

""" Import Libraries """
import xml.etree.ElementTree as ET
import urllib.request
import time
import datetime
import neopixel
import board
import requests
import json
try:
    import astral
except ImportError:
    astral = None

""" Import Airport List """
with open("/home/pi/METARmap/Airports") as f:
    airports = f.readlines()
airports = [x.strip() for x in airports]

""" LED Colors """
COLOR_VFR = (0,255,0) # Green
COLOR_MVFR = (0, 0, 255) # Blue
COLOR_IFR = (255,0,0) # Red
COLOR_LIFR = (125,0,125) # Magenta
COLOR_CLEAR = (0,0,0) # Clear
COLOR_ORANGE = (255,165,0) # Orange

""" Setup Dimming Based on Time """
brightLED = 0.5 # Brightness ratio for bright LEDs (0 - 1)
dimmingRatio = 0.2 # Brightness ratio for dim LEDs (0 - 1)
cityNearest = "Boston" # Set to city location, refer to https://astral.readthedocs.io/en/latest/#cities)
timeBright = datetime.time(7,0) # Set default bright time
timeDim = datetime.time(19,0) # Set default dim time

# Determine sunrise/sunset times for bright/dim adjustment)
if astral is not None:
    try:
        ast = astral.Astral()
        try:
            city = ast[cityNearest]
        except KeyError:
            print("Error: Location not recognized")
        else:
            print(city)
            sun = city.sun(date = datetime.datetime.now(), local = True)
            timeBright = sun['sunrise'].time()
            timeDim = sun['sunset'].time()
    except AttributeError:
        import astral.geocoder
        import astral.sun
        try:
            city = astral.geocoder.lookup(cityNearest, astral.geocoder.database())
        except KeyError:
            print("Error: Location not recognized")
        else:
            print(city)
            sun = astral.sun.sun(city.observer, date = datetime.datetime.now().date(), tzinfo=city.timezone)
            timeBright = sun['sunrise'].time()
            timeDim = sun['sunset'].time()
    print("Current time is: " + str(datetime.datetime.now()))
    print("Sunrise:" + timeBright.strftime('%H:%M') + " Sunset:" + timeDim.strftime('%H:%M'))

"""LED Configuration"""
timeNow = datetime.datetime.now().time()
if timeBright < timeNow and timeNow < timeDim:
    bright = True
    print("It's daytime! The lights are bright!")
else:
    bright = False
    print("It's nighttime! The lights are dim!")

LED_COUNT = len(airports) # Number of LEDS --> Equals # of airports in list
LED_PIN = board.D18 # GPIO pin connected to neopixels (18 uses PWM)
ORDER = neopixel.GRB
pixels = neopixel.NeoPixel(
    LED_PIN, LED_COUNT, brightness = dimmingRatio if (bright == False) else brightLED,
    auto_write=False, pixel_order=ORDER)

""" Determine Scheduled/Actual Flight """
#endpoint = "https://aeroapi.flightaware.com/aeroapi/flights/N1446C"
#api_key = "9zRxOB4Ue5iXo6lm4Gf4vcBrjHCZI9ro"
#jsonData = requests.get(endpoint, headers = {"x-apikey":api_key}).json()
jsonData = json.load(open("/home/pi/METARmap/testJSON.json"))
flightData = jsonData['flights'][0]

actual_off = flightData['actual_off']
estimated_off = flightData['estimated_off']
actual_on = flightData['actual_on']
estimated_on = flightData['estimated_on']
scheduled_off = flightData['scheduled_off']
scheduled_on = flightData['scheduled_on']
origin = flightData['origin']['code']
destination = flightData['destination']['code']
utcNow = datetime.datetime.utcnow().replace(second=0, microsecond=0)

times = {"actual_off":actual_off, "actual_on":actual_on,
         "estimated_off":estimated_off, "estimated_on":estimated_on,
         "scheduled_off":scheduled_off, "scheduled_on":scheduled_on}

for key in times:
    try:
        tempTime = datetime.datetime.strptime(times[key].replace('T', ' ')[0:-1], '%Y-%m-%d %H:%M:%S')
        times[key] = tempTime
    except:
        continue

departTime = max([val for key, val in times.items() if "off" in key and val is not None])
arriveTime = max([val for key, val in times.items() if "on" in key and val is not None])

""" Get METAR Info """
url = 'https://aviationweather.gov/adds/dataserver_current/httpparam?datasource=metars&requestType=retrieve&format=xml&mostRecentForEachStation=constraint&hoursBeforeNow=1.25&stationString='
for airport in airports:
    url += (airport + ",")
url = url[:-1]

try:
    with urllib.request.urlopen(url) as response:
            xml_metar = response.read()
    metar = ET.fromstring(xml_metar)
except Exceptions:
    time.sleep(60)
    pass

conditionDict = {"NULL": {"flightCategory" : ""}}
conditionDict.pop("NULL")

stationList = []
for metarInfo in metar.iter('METAR'):
    stationID = metarInfo.find('station_id').text
    if metarInfo.find('flight_category') is None:
            continue
    flightCategory = metarInfo.find('flight_category').text
    conditionDict[stationID] = flightCategory

""" Organize METAR Info """
organizedWeather = {}
for airport in airports:
    organizedWeather[airport] = "NONE"

for key in organizedWeather:
    try:
        organizedWeather[key] = conditionDict[key]
    except Exception as e:
        organizedWeather[key] = "NONE"

if departTime <= utcNow and utcNow <= arriveTime:
    print("in flight")
else:
    print("not flying")

""" Set LED Colors """
i=0
for key in organizedWeather:
    if organizedWeather[key] == "VFR":
        pixels[i] = COLOR_VFR
        continue
    elif organizedWeather[key] == "MVFR":
        pixels[i] = COLOR_MVFR
        continue
    elif organizedWeather[key] == "IFR":
        pixels[i] = COLOR_IFR
        continue
    elif organizedWeather[key] == "LIFR":
        pixels[i] = COLOR_LIFR
        continue
    else:
        pixels[i] = COLOR_CLEAR
        continue
    i+=1

for key in organizedWeather:
    print("At " + key + " the current weather is " + organizedWeather[key])
pixels.show()
