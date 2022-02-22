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

"""Import Airport List"""

with open("/home/pi/METARmap/Airports") as f:
    airports = f.readlines()
airports = [x.strip() for x in airports]

""" LED Configuration """
LED_COUNT = len(airports) # Number of LEDS --> Equals # of airports in list
LED_PIN = board.D18 # GPIO pin connected to neopixels (18 uses PWM)
ORDER = neopixel.GRB

pixels = neopixel.NeoPixel(
    LED_PIN, LED_COUNT, brightness=0.2, auto_write=False, pixel_order=ORDER
)

#print(pixels)

""" Pixel Colors """

COLOR_VFR = (0,255,0) # Green
COLOR_MVFR = (0, 0, 255) # Blue
COLOR_IFR = (255,0,0) # Red
COLOR_LIFR = (125,0,125) # Magenta
COLOR_CLEAR = (0,0,0) # CLEAR

""" Get METAR Info """

url = 'https://aviationweather.gov/adds/dataserver_current/httpparam?datasource=metars&requestType=retrieve&format=xml&mostRecentForEachStation=constraint&hoursBeforeNow=1.25&stationString='
for airport in airports:
    url += (airport + ",")

url = url[:-1]
url = url +(',7B3')
#print(url)

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
#       print(stationID)
        if metarInfo.find('flight_category') is None:
                continue
        flightCategory = metarInfo.find('flight_category').text
#       print(flightCategory)
        conditionDict[stationID] = flightCategory

#print(conditionDict)

""" Organize METAR Info """

organizedWeather = {}
for airport in airports:
        organizedWeather[airport] = "NONE"

for key in organizedWeather:
        organizedWeather[key] = conditionDict[key]
#print(conditionDict)
#print(organizedWeather)

""" Set LED Colors """
i=0
for key in organizedWeather:
        if organizedWeather[key] == "VFR":
                pixels[i] = COLOR_VFR
        elif organizedWeather[key] == "MVFR":
                pixels[i] = COLOR_MVFR
        elif organizedWeather[key] == "IFR":
                pixels[i] = COLOR_IFR
        elif organizedWeather[key] == "LIFR":
                pixels[i] = COLOR_LIFR
        else:
                pixels[i] = COLOR_CLEAR
        i+=1

for key in organizedWeather:
        print("At " + key + " the current weather is "
              + organizedWeather[key])

#print(pixels) # Uncomment to check color assignnment for each LED
pixels.show()
