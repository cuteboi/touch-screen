from evdev import InputDevice
from select import select

dev = InputDevice('/dev/input/event1')

while True:
   r,w,x = select([dev], [], [])
   for event in dev.read():
       print(event)
