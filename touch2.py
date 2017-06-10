#!/usr/bin/python
import struct
import time
import sys

infile_path = "/dev/input/event" + (sys.argv[1] if len(sys.argv) > 1 else "0")
rpi_brightness_file = "/sys/class/backlight/rpi_backlight/brightness"
rpi_backlight_file = "/sys/class/backlight/rpi_backlight/bl_power"


#long int, long int, unsigned short, unsigned short, unsigned int
FORMAT = 'llHHI'
EVENT_SIZE = struct.calcsize(FORMAT)
EVENT_KEYS = ['tv_sec', 'tv_usec', 'type', 'code', 'value']

# http://stackoverflow.com/questions/2272149/round-to-5-or-other-number-in-python
def myround(x, base=5):
	return int(base * round(float(x)/base))


f = open(rpi_backlight_file, "rb")
rpi_backlight = int(f.read())
f.close()

if rpi_backlight == 1:
	print "Display is off"
else:
	print "Display is on"

f = open(rpi_brightness_file)
rpi_brightness = int(f.read())
f.close()

print "Brightness at: " + str(int(round(rpi_brightness * (100.0/255)))) + "%"


#open file in binary mode
in_file = open(infile_path, "rb")

event = in_file.read(EVENT_SIZE)

touch_event = {}
previous_touch_event = {}
button_press = 0
display_set = False

while event:
    evstruct = dict(zip(EVENT_KEYS,struct.unpack(FORMAT, event)))

    if evstruct["type"] != 0 or evstruct["code"] != 0 or evstruct["value"] != 0:
	if evstruct["code"] == 330:
		
		touch_event["time"] = int(round((float(str(evstruct["tv_sec"])+"."+'%06d' % evstruct["tv_usec"])*1000)))
		touch_event["tv_sec"] = evstruct["tv_sec"]
		touch_event["tv_usec"] = evstruct["tv_usec"]
		
		if(evstruct["value"] == 1):
			touch_event["button"] = "pressed"
		else:
			touch_event["button"] = "released"
	if(evstruct["code"] == 0):
		touch_event["X"] = evstruct["value"]
	if(evstruct["code"] == 1):
		touch_event["Y"] = evstruct["value"]
	if(evstruct["code"] == 47):
		touch_event["finger"] = evstruct["value"]
    else:
        # Events with code, type and value == 0 are "separator" events
	if(touch_event.get("button",0)):
		if touch_event["button"] == "released":
			if display_set == False :
				print(touch_event.get("finger",0)+1, touch_event["button"],touch_event["X"],touch_event["Y"], int(touch_event["time"] - button_press))
			button_press = 0
			display_set = False
		else:
			if rpi_backlight == 0 and touch_event["X"] < 50:
				brightness = int(round(touch_event["Y"] * float( 255.0 / 480.0 )))

				steps = (100.0/255)
				rounded_to5 = myround(int(round(brightness * steps)))
				brightness = int((float(rounded_to5) / 100) * 255)
				if brightness != rpi_brightness and rounded_to5 >= 5:
					print "Brightness set to : " + str(rounded_to5)
					f = open(rpi_brightness_file, "w")
					f.write(str(brightness) + "\n")
					f.close()

					rpi_brightness = brightness
				display_set = True
			elif ( touch_event["X"] > 750 and touch_event["Y"] < 50 and display_set == False) :
				f = open(rpi_backlight_file, "r+")
				val  = f.read()
				if int(val) == 1 :
					print "Display is on"
					rpi_backlight = 0
					f.write("0\n")
				else :
					print "Display is off"
					f.write("1\n")
					rpi_backlight = 1

				f.close()
				display_set = True
			elif button_press == 0:
				button_press = touch_event["time"]
				print(touch_event.get("finger",0)+1, touch_event["button"], touch_event["X"], touch_event["Y"])



					
		previous_touch_event = touch_event
    event = in_file.read(EVENT_SIZE)

in_file.close()
