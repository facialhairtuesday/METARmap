# METARmap #
## By FHT ##

METARmap uses an internet-connected Raspberry Pi to pull ADDS XML feed, and drive NeoPixel LEDs to indicate flight category at airports.

Inspired by post by /u/Grimace06

**Requires rpi_ws281x from JGarff**

Follow instructions here [here](https://learn.adafruit.com/neopixels-on-raspberry-pi/software) to install on RPi

## To customize code for your chart: ##
* Under "Airport List", modify the list to include the airports you will be using in your METARmap.  Use full ICAO name (K---, etc.) you would use if looking up METARs online.  Each airport name should be in quotes ("X") and separated by commas. ** Airports in the list must be in the order that you will wire the NeoPixels**
* In "LED CONFIGURATION" Section, change number of LEDs ("LED_COUNT") to the number of NeoPixels you are using (should match the number of airports in your list)
* You can change the brightness of the LEDs by adjusting the values in the flight category LED settings.  Current value (127) is 1/2 brightness.  Values can range from 0 (off) to 255 (Full on)
* Currently updates every 10 minutes (time.sleep(600)), but can be altered for shorter or longer updates if desired
* Troubleshooting section at the end can be used to print out airports list, flight category, etc. if you're having issues with things working.
