#!/usr/bin/env python

from __future__ import print_function
from optparse import OptionParser
import grpc
import droneconnect_pb2
import sys, time
import gpxpy
import gpxpy.gpx

def readGPXFile(pathFile):
    """ Reads the route contained within the .gpx file .

    Returns:
        The full contents of the route gpx file as a sequence of droneconnect_pb2.Position.
    """
    gpx_file = open(pathFile, 'r')
    gpx = gpxpy.parse(gpx_file)
    
    position_list = []
    for route in gpx.routes:
        for point in route.points:
            position = droneconnect_pb2.Position(
                lat = point.latitude,
                lon = point.longitude,
                gpsAltitude = point.elevation, 
                relativeAltitude = 10,
                useRelativeAltitude = True)
            position_list.append(position)
    
    return position_list
  

def droneInfo(stub):
    response = stub.getAutopilotInfo(droneconnect_pb2.UavIdentifier(identifier=666))
    print("Identifier: " + str(response.identifier))
    print("Autopilot firmware version: " + response.autopilot_firmware_version)
    print("Major version number: " + str(response.major_version_number))
    print("Minor version number: " + str(response.minor_version_number))
    print("Patch version number: " + str(response.patch_version_number))
    print("Release type: " + response.release_type)
    print("Release version: " + str(response.release_version))
    print("Stable release?: " + str(response.stable_release))

    return 
  
def droneReboot(stub):
  stub.reboot(droneconnect_pb2.Null())
  
  return
  
def getPosition(stub):
    response = stub.getPosition(droneconnect_pb2.Null())
    print("lat: " + str(response.lat))
    print("long: " + str(response.lon))
    print("GPS altitude: " + str(response.gpsAltitude))
    print("Altitude relative to HOME: " + str(response.relativeAltitude))
  
    return
    
def setMode(stub, newMode):
    newMode = newMode.upper()
    response = stub.setMode(droneconnect_pb2.Mode(mode=newMode))
        
    return
    
def hasMode(stub):
    response = stub.hasMode(droneconnect_pb2.Null())
    print("Mode: " + response.mode)
    
    return
    
def setArmed(stub, armChoice):
    response = stub.setArmed(droneconnect_pb2.Armed(arm = armChoice))
        
    return
    
def isArmed(stub):
    response = stub.isArmed(droneconnect_pb2.Null())
    print("Armed: " + str(response.arm))
    
    return
    
def setPath(stub, pathFile):
    position_list = readGPXFile(pathFile)
    path_iterator = iter(position_list)
    response = stub.setPath(path_iterator)

    return
    
def setSafety(stub, newSafety):
    response = stub.setSafety(droneconnect_pb2.Safety(safety = newSafety))
    
    return
    
def getSafety(stub):
    response = stub.getSafety(droneconnect_pb2.Null())
    safety = response.safety
    if safety:
        print("Safety is on.")
    elif safety == False:
        print("Safety is off!")
    
    return
    
def takeoff(stub, takeoffAltitude):
    print ("Taking off to {0} meters.".format(takeoffAltitude))
    response = stub.takeoff(droneconnect_pb2.TakeoffToAltitude(altitude = takeoffAltitude))
    print("Altitude relative to HOME: " + str(response.relativeAltitude))
        
    return
  
def main():
    parser = OptionParser()
    parser.add_option("--address", action="store", type="string", dest="address")
    parser.add_option("--port", action="store", type="string", dest="port")
    (options, args) = parser.parse_args()
    
    if (not options.address) or (not options.port): 
        print ("Usage: droneconnect_client.py --address address --port port") 
        sys.exit (1)
    
    try:
        channel = grpc.insecure_channel('{0}:{1}'.format(options.address, options.port))
        #channel = grpc.insecure_channel('206.87.166.221:50051')
        stub = droneconnect_pb2.DroneConnectStub(channel)
    
        moreCommands = True
        while moreCommands:
            print("")
            hasMode(stub)
            isArmed(stub)
            getSafety(stub)
            print ("""-----------------------------------------
      1.  Retrieve autopilot info
      2.  Reboot drone
      3.  Get position of drone
      4.  Set mode
      5.  Arm/Disarm drone
      6.  Safety on/off
      7.  Set path
      8.  Take off to altitude
      9.  Refresh state
      
      Press "Enter" key to exit
            """)
            ans=raw_input("What would you like to do? ") 
            if ans == "1": 
                droneInfo(stub) 
            elif ans == "2":
                print ("\nRebooting drone has not been implemented yet.")
            elif ans == "3":
                print("")
                getPosition(stub)
            elif ans == "4": 
                print("\nModes available are:")
                # TODO: Get modes directly from drone, for now just print them out
                print ("RTL, POSHOLD, LAND, OF_LOITER, STABILIZE, AUTO, GUIDED, THROW, DRIFT, FLIP, ")
                print ("AUTOTUNE, ALT_HOLD, BRAKE, LOITER, AVOID_ADSB, POSITION, CIRCLE, SPORT, ACRO")
                newMode = raw_input("\nNew mode: ")
                setMode(stub, newMode)
                time.sleep(1)
            elif ans == "5":
                newMode = raw_input("\nType 'arm' to arm or anything else to 'disarm': ")
                if newMode == 'arm':
                    setArmed(stub, True)
                else: 
                    setArmed(stub, False)
            elif ans == "6":
                safety = raw_input("\nType 'off' to turn safety off or anything else for 'on': ")
                if safety == 'off':
                    setSafety(stub, False)
                else: 
                    setSafety(stub, True)
                time.sleep(1)
            elif ans == "7":
                pathFile = raw_input("\nPath file: ")
                #pathFile = "route3.gpx"
                setPath(stub, pathFile)
            elif ans == "8":
                takeoffAltitude = raw_input("\nAltitude: ")
                takeoff(stub, float(takeoffAltitude))
            elif ans == "9":
                continue
            elif ans == "":
              moreCommands = False 
    except: # catch *all* exceptions
        print ("Could not connect to drone.") 
        sys.exit (1)

if __name__ == '__main__':
    main()
