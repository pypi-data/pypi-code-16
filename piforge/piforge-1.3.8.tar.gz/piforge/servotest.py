import RPi.GPIO as GIPO
import servo
import time

myServo=servo.pi_servo(18,0)

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
