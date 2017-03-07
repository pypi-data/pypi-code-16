#!/usr/bin/python
import RPi.GPIO as GPIO
import Adafruit_PCA9685

class forgeHat_servo:
	def __init__(self,port,angle):
		global pwm
		self.port=port
		pwm = Adafruit_PCA9685.PCA9685()
		pwm.set_pwm_freq(60)
		
	def write(self,angle):
		pwm.set_pwm(self.port, 0, self.angleToUnits(angle))
		
	def angleToUnits(self,angle):
		OldMax=180
		OldMin=0
		NewMax=600
		NewMin=150
		OldRange = (OldMax - OldMin)  
		NewRange = (NewMax - NewMin)  
		units = int((((angle - OldMin) * NewRange) / OldRange) + NewMin)
		return(units)
		
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
