import RPi.GPIO as GIPO
import servo
import time

myServo=servo.forgeHat_servo(0,0)

while 1:
	myServo.write(0)
	print "xero degrees"
	time.sleep(5)
	myServo.write(90)
	print "ninty degrees"
	time.sleep(5)
	myServo.write(180)
	print "one eighty"
	time.sleep(5)
