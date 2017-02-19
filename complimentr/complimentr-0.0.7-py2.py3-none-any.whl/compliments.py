from complimentr.messageSender import sendCompliment

def runComplimentrApp ():
  print("Welcome to complimentr! \n You will need set up a Twilio Account before using this app")
  sendCompliment()
  print("Compliment sent!")
  return
