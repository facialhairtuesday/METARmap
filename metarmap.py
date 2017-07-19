#Metar Map V1
 #Author: FHT
 #2017-06-11


""" Import Stuff """
import xml.etree.ElementTree as ET
import urllib
import time
from neopixel import *

""" Airport List --> PUT IN SAME ORDER AS LEDs ARE WIRED ON MAP """
airports = ["KBOS", "KBED", "KLWM", "KPSM", "KPYM"]


""" LED Configuration """
LED_COUNT = 5           # Number of LEDs --> Should equal number of airports in list
LED_PIN = 18            # GPIO pin connected to neopixels (18 uses PWM)
LED_FREQ_HZ = 800000    # LED signal frequency in Hz (usually 800 kHz)
LED_DMA = 5             # DMA channel to use for generating signal
LED_BRIGHTNESS = 255    # Set to 0 for darkest and 255 for brightest
LED_INVERT = False      # Set to true to invert signal when using NPN transistor level shift
LED_CHANNEL = 0         # Set to '1' for GPIOs 13, 19, 41, 45, or 53
LED_STRIP = ws.WS2811_STRIP_GRB         #Strip type and color ordering, Neopixel breadboards actually RGB, didn't want to mess with$

if __name__ == '__main__':

        """ Create NeoPixel object with appropriate configuration """
        strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

        """ Initialize library (must be called once before other functions) """
        strip.begin()

        while True:

                """ Url Setup + Add airport identifiers from airport list + remove last character (,) """
                url = 'https://aviationweather.gov/adds/dataserver_current/httpparam?datasource=metars&requestType=retrieve&format=$
                for airport in airports:
                        url += (airport + ',')

                url = url[:-1]

                """ Get XML METAR and parse """
                xml_metar = ET.parse(urllib.urlopen(url))
                metar = xml_metar.getroot()

                """ Add Airport & Flight Category Info to Lists """
                stationList = []
                for station in metar.iter('station_id'):
                        stationList.append(station.text)

                flightCat = []
                for category in metar.iter('flight_category'):
                        flightCat.append(category.text)

                """ Generate weather dictionary with assembled airport and category info """
                weather = {}
                for station in range(len(stationList)):
                        weather[stationList[station]] = flightCat[station]

                # Neopixel colors:
                # Color(255, 0, 0) = RED
                # Color(0, 255, 0) = GREEN
                # Color(0, 0, 255) = BLUE

                """ Turn off all LEDs to reset """
                for i in range(0, strip.numPixels(),1):
                        strip.setPixelColor(i, Color(0, 0, 0))
                        strip.show()

                """ Turn on LEDs in the order of the airport list """
                for i in range(0, strip.numPixels(),1):
                        cat = weather[airports[i]]
                        if cat == "VFR":
                                strip.setPixelColor(i, Color(0,127,0)) # Green, 1/2 brightness
                                strip.show()
                        elif cat == "MVFR":
                                strip.setPixelColor(i, Color(0,0,127)) # Blue, 1/2 brightness
                                strip.show()
                        elif cat == "IFR":
                                strip.setPixelColor(i, Color(127,0,0)) # Red, 1/2 brightness
                                strip.show()
                        elif cat == "LIFR":
                                strip.setPixelColor(i,Color(127,0,127)) # Purple, 1/2 brightness
                                strip.show()
                time.sleep(600)

                """ Troubleshooting --> Uncomment to print info """
                """
                print('VFR = GREEN, MVFR = BLUE, IFR = RED, LIFR = PURPLE')
                print(weather)
                print(airports)
                time.sleep(5)

                for i in range(0, strip.numPixels(),1):
                        strip.setPixelColor(i,Color(0,0,0))
                        strip.show()

                time.sleep(2)
                """
