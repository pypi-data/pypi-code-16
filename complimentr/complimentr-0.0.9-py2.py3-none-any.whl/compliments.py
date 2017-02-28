from complimentr.messageSender import sendCompliment
import time
import numpy as np

def runComplimentrApp ():
  print("Welcome to complimentr! \n You will need set up a Twilio Account before using this app")
  compliment_count = 0
  while (compliment_count <= 45):
      sendCompliment()
      waitForOnAverage3Hours()
      compliment_count = compliment_count + 1

  print("Compliment sent!")
  return

def waitForOnAverage3Hours():
    mean = 3*60*60
    standard_deviation = 1.5*60*60
    sleep_time = np.random.normal(mean, standard_deviation)
    if (sleep_time <=1):
      sleep_time = 1

    time.sleep(sleep_time)
    return
