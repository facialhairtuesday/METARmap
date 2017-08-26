 #Metar Map V1
 #Author: FHT
 #2017-06-11

""" Code to Customize METARmap """

# Airport List --> PUT IN SAME ORDER AS LEDs ARE WIRED ON MAP
#airports = ["KBOS", "KBED", "KLWM", "KPSM", "KPYM"]
airports = ["KBOS", "KSAW","KHYR","KPIA","KDEN"]

# Brightnesss Time Settings
morn = 7 # Local time in morning (hour only) for LEDs to go to bright setting, default 0700
nite = 22 # Local time in evening (hour only) for LEDs to go to dim setting, default 2200

""" Import Stuff """
import xml.etree.ElementTree as ET
import urllib
import time
import datetime
from neopixel import *



""" LED Configuration """
LED_COUNT = len(airports)		# Number of LEDs --> Should equal number of airports in list
LED_PIN = 18				# GPIO pin connected to neopixels (18 uses PWM)
LED_FREQ_HZ = 800000			# LED signal frequency in Hz (usually 800 kHz)
LED_DMA = 5				# DMA channel to use for generating signal
LED_BRIGHTNESS = 255			# Set to 0 for darkest and 255 for brightest
LED_INVERT = False			# Set to true to invert signal when using NPN transistor level shift
LED_CHANNEL = 0				# Set to '1' for GPIOs 13, 19, 41, 45, or 53
LED_STRIP = ws.WS2811_STRIP_GRB		#Strip type and color ordering, Neopixel breadboards actually RGB, didn't want to mess with code

if __name__ == '__main__':

	""" Create NeoPixel object with appropriate configuration """
	strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL, LED_STRIP)

	""" Initialize library (must be called once before other functions) """
	strip.begin()

	while True:
		
		""" Get current time to set LED brightness """
		now = datetime.datetime.now()
		
		if now.hour >= morn and now.hour < nite:
			LED_Level = 127
		else:
			LED_Level = 15

		""" Url Setup + Add airport identifiers from airport list + remove last character (,) """
		url = 'https://aviationweather.gov/adds/dataserver_current/httpparam?datasource=metars&requestType=retrieve&format=xml&mostRecentForEachStation=constraint&hoursBeforeNow=1.25&stationString='
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
				strip.setPixelColor(i, Color(0,LED_Level,0)) # Green
				strip.show()
			elif cat == "MVFR":
				strip.setPixelColor(i, Color(0,0,LED_Level)) # Blue
				strip.show()
			elif cat == "IFR":
				strip.setPixelColor(i, Color(LED_Level,0,0)) # Red
				strip.show()
			elif cat == "LIFR":
				strip.setPixelColor(i,Color(LED_Level,0,LED_Level)) # Purple
				strip.show()

		time.sleep(5)

		""" Troubleshooting --> Uncomment to print info """
		
		"""#print('VFR = GREEN, MVFR = BLUE, IFR = RED, LIFR = PURPLE')
		#print(weather)
		#print(airports)
		time.sleep(5)

		#for i in range(0, strip.numPixels(),1):
		#	strip.setPixelColor(i,Color(0,0,0))
		#	strip.show()

		#time.sleep(2) """
