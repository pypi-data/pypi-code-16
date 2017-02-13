#!/usr/bin/python
import RPi.GPIO as GPIO

class pi_servo:
	def __init__(self,pin,angle):
		global p
		self.pin=pin
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(pin,GPIO.OUT)          # initialize pin as an output
		p = GPIO.PWM(pin,100)          # pin as PWM output, with 50Hz frequency
		#p.start(10)
		p.start(self.getDutyCycle(angle)) # generate PWM signal 
	
	def write(self,angle):
		#p.ChangeDutyCycle(dc)
		p.ChangeDutyCycle(self.getDutyCycle(angle))
		
		
	def getDutyCycle(self,angle):
		#convert angle to duty cycle
		
		OldMax=180.0
		OldMin=0.0
		NewMax=25.0
		NewMin=5.0
		OldRange = (OldMax - OldMin)  
		NewRange = (NewMax - NewMin)  
		dutyCycle = float((((angle - OldMin) * NewRange) / OldRange) + NewMin)
		print dutyCycle
		return(dutyCycle)
