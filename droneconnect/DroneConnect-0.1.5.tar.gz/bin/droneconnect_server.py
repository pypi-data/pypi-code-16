#!/usr/bin/env python

# Copyright 2015, Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of Google Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""GRPC server for droneconnect"""
from concurrent import futures
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command, Vehicle
from pymavlink import mavutil
from optparse import OptionParser
from itertools import islice
import collections, sys, time, grpc, socket
import droneconnect_pb2
import re
import dronekit_sitl
import types
import threading



UDP_IP = "127.0.0.1"
UDP_PORT = 5234
_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class NewVehicle(Vehicle):

    def __init__(self, *args):
        super(NewVehicle, self).__init__(*args)
        self._safety = True
        
    @property
    def safety(self):
        """
        This attribute is used to get and set the safety mode (switch on top of drone).
        """
        return self._safety
    
    @safety.setter    
    def safety(self, s):
        if s == True:
            self._master.mav.set_mode_send(self._master.target_system,
                                              mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY,
                                              1)
            self._safety = True 
        elif s == False:
            self._master.mav.set_mode_send(self._master.target_system,
                                              mavutil.mavlink.MAV_MODE_FLAG_DECODE_POSITION_SAFETY,
                                              0)
            self._safety = False                    

    
class DroneConnect(droneconnect_pb2.DroneConnectServicer):
  
    def __init__(self, vehicle):
        self.vehicle = vehicle
        #self.thread = threading.Thread(target=self.print_position)
        #self.thread.start()
  
    def SayHello(self, request, context):
        return droneconnect_pb2.HelloReply(message='Hello, %s!' % request.name)
    
    def getAutopilotInfo(self, request, context):
        """Returns Autopilot release information.""" 

        response = droneconnect_pb2.AutopilotInfo(identifier=request.identifier,
                                    autopilot_firmware_version = str(self.vehicle.version),
                                    major_version_number = self.vehicle.version.major,
                                    minor_version_number = self.vehicle.version.minor,
                                    patch_version_number = self.vehicle.version.patch,
                                    release_type = self.vehicle.version.release_type(),
                                    release_version = self.vehicle.version.release_version(),
                                    stable_release = self.vehicle.version.is_stable())
                                    
        return response
                                    
        
    def getPosition(self, request, context):
        """Returns Autopilot release information.""" 
        
        # The latitude and longitude are relative to the WGS84 coordinate system. 
        # The altitude is relative to mean sea-level (MSL)
        globalLocation = str(self.vehicle.location.global_frame)
        
        # LocationGlobalRelative:lat=0.0,lon=0.0,alt=6.6
        # Altitude relative to the home location.  The lat and long values for this and the above
        # variable will be the same.
        relativeLocation = str(self.vehicle.location.global_relative_frame)
        
        latitude, longitude, altGPS, altHome = None, None, None, None
        
        match = re.search(r"lat=(.*),lon=(.*),alt=(.*)$", globalLocation)
        if match:
            latitude = match.group(1)
            longitude = match.group(2)
            altGPS = match.group(3)
            
        match = re.search(r"lat=(.*),lon=(.*),alt=(.*)$", relativeLocation)
        if match:
            altHome = match.group(3)
        
        return droneconnect_pb2.Position(lat = float(latitude),
                                         lon = float(longitude),
                                         gpsAltitude = float(altGPS),
                                         relativeAltitude = float(altHome))
        
    def setMode(self, request, context):
        """Sets the mode of the drone which is represented as a string in the request"""
        
        self.vehicle.mode = VehicleMode(str(request.mode))
        self.vehicle.wait_ready('mode')
        
        return droneconnect_pb2.Null()
        
    def hasMode(self, request, context):
        droneMode = str(self.vehicle.mode).rpartition(':')[2]
        
        return droneconnect_pb2.Mode(mode=droneMode)
        
    def setArmed(self, request, context):
        """Sets the armed state of the drone, TRUE indicates armed."""
        
        self.vehicle.armed = request.arm 
            
        return droneconnect_pb2.Null()
        
    def isArmed(self, request, context):
        """Returns the armed state of the drone."""
        
        return droneconnect_pb2.Armed(arm=self.vehicle.armed)
        
    def setSafety(self, request, context):
        """Sets the safety switch on the drone, TRUE indicates safety is on."""
        self.vehicle.safety = request.safety
            
        return droneconnect_pb2.Null()
        
    def getSafety(self, request, context):
        """Returns the state of the safety switch on the drone."""
        
        return droneconnect_pb2.Safety(safety=self.vehicle.safety)
        
    def setPath(self, request, context):
        """Uploads a series of positions to the drone in order to create a mission."""
        
        cmds = self.vehicle.commands
        coordFrame, alt = None, None
        
        # The idea behind stripping off the first position is to determine what reference frame to
        # to use.  Future proto changes will removed the coordinate frame boolean flag from the 
        # request making the code unnecessary.  For now, this is the way it is.
        firstPosition = nth(request, 0)
        lat = firstPosition.lat
        lon = firstPosition.lon
        
        useRelativeAltitude = firstPosition.useRelativeAltitude
        
        if useRelativeAltitude:
            alt = firstPosition.relativeAltitude
            coordFrame = mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT
        else:
            alt = firstPosition.gpsAltitude
            coordFrame = mavutil.mavlink.MAV_FRAME_GLOBAL

        print ('First position at ({0},{1}) -> {2}'.format(lat, lon, alt))
        
        # Make sure the drone is not in AUTO mode.   
        self.vehicle.mode = VehicleMode("LOITER")
        self.clear_mission(cmds, coordFrame)
        
        # Add first position
        cmds.add(Command( 0, 0, 0, coordFrame, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, alt))
        
        # Add the remaining positions
        for position in request:
            lat = position.lat
            lon = position.lon
            if useRelativeAltitude:
                alt = position.relativeAltitude
            else:
                alt = position.gpsAltitude
            print ('Point at ({0},{1}) -> {2}'.format(lat, lon, alt))
            cmds.add(Command( 0, 0, 0, coordFrame, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, lat, lon, alt))
            
        print ("Uploading new commands to drone")
        cmds.upload()
        
        print "Starting mission"
        # Reset mission set to first (0) waypoint
        self.vehicle.commands.next = 0
        self.vehicle.mode = VehicleMode("AUTO")
        
        self.print_mission() 
        
        return droneconnect_pb2.Null()
        
    def takeoff(self, request, context):
      """Arms vehicle and fly to target altitude relative to HOME position."""
      print "Arming motors"
      # Copter should arm in GUIDED mode
      self.vehicle.mode = VehicleMode("GUIDED")
      self.vehicle.armed = True    

      # Confirm vehicle armed before attempting to take off
      timeout = 0
      while not self.vehicle.armed:      
          print " Waiting for arming..."
          time.sleep(1)
          timeout = timeout + 1
          if timeout == 20:
              return self.getPosition(request, context)

      print "Taking off!"
      self.vehicle.simple_takeoff(request.altitude) # Take off to target altitude

      # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
      #  after Vehicle.simple_takeoff will execute immediately).
      while True:
          print " Altitude: ", self.vehicle.location.global_relative_frame.alt 
          #Break and return from function just below target altitude.        
          if self.vehicle.location.global_relative_frame.alt >= request.altitude * 0.95: 
              print "Reached target altitude"
              break
          time.sleep(1)
          
      return self.getPosition(request, context)
      
    def clear_mission(self, cmds, coordFrame):
        """
        Creates consistent behavior when clearing commands from drone.
        
        If the drone doesn't have any stored commands and an attempt is made to upload a new list of
        commands the first member of the new list appears to be deleted. Uploading and clearing
        a dummy waypoint appears to be a workaround.
        
        It's likely that coordFrame doesn't need to be set here but it's included for consistency.
        """
        cmds.clear()
        
        #Add dummy waypoint since Ardupilot overwrites first waypoint
        cmds.add(Command( 0, 0, 0, coordFrame, mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0, 0, 0, 0, 0, 0, 0, 0, 0))
        cmds.upload()
        cmds.clear()
      
    def download_mission(self):
        """
        Downloads the current mission and returns it in a list.
        """
        print " Download mission from vehicle"
        missionlist = []
        cmds = self.vehicle.commands
        cmds.download()
        cmds.wait_ready()
        for cmd in cmds:
            missionlist.append(cmd)
        return missionlist
        
    def print_mission(self):
        """
        Print a mission in the Waypoint file format 
        (http://qgroundcontrol.org/mavlink/waypoint_protocol#waypoint_file_format).
        """   
        #Download mission from vehicle
        missionlist = self.download_mission()
        
        #Add commands
        for cmd in missionlist:
            commandline="%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (cmd.seq,cmd.current,cmd.frame,cmd.command,cmd.param1,cmd.param2,cmd.param3,cmd.param4,cmd.x,cmd.y,cmd.z,cmd.autocontinue)
            print commandline
            
    def print_position(self):
        """
        Testing method for printing drone position
        """
        while True:
            lat = self.vehicle.location.global_relative_frame.lat
            lon = self.vehicle.location.global_relative_frame.lon
            print ('{0},{1}'.format(lat, lon))
            time.sleep(1) 

def nth(iterable, n, default=None):
    """
    Returns the nth item or a default value
    """
    return next(islice(iterable, n, None), default)
    
def distance_to_current_waypoint():
    """
    Gets distance in metres to the current waypoint. 
    It returns None for the first waypoint (Home location).
    """
    nextwaypoint = vehicle.commands.next
    if nextwaypoint==0:
        return None
    missionitem=vehicle.commands[nextwaypoint-1] #commands are zero indexed
    lat = missionitem.x
    lon = missionitem.y
    alt = missionitem.z
    targetWaypointLocation = LocationGlobalRelative(lat,lon,alt)
    distancetopoint = get_distance_metres(vehicle.location.global_frame, targetWaypointLocation)
    
    return distancetopoint
    
def connect_to_drone(sitlOption, lat, lon):
    """Connects to drone and returns vehicle object."""
    
    vehicle = None
    
    if sitlOption:
        print("Using sitl simulator")
        sitl = dronekit_sitl.start_default(lat, lon)
        
        connection_string = sitl.connection_string()
        print connection_string
        vehicle = connect(connection_string, wait_ready=True, vehicle_class=NewVehicle)
    else:
        serial_list = mavutil.auto_detect_serial(preferred_list=['*FTDI*',"*Arduino_Mega_2560*", "*3D_Robotics*", "*USB_to_UART*", '*PX4*', '*FMU*'])
        print('Auto-detected serial ports are:')
        for port in serial_list:
            print("%s" % port)
       
        connection_string = str(serial_list[0].device)
        vehicle = connect(connection_string, wait_ready=True, baud=57600, heartbeat_timeout=120, vehicle_class=NewVehicle)
        
    print ("Connected to drone")
    print (connection_string)
    
    return vehicle


def serve():
    """Sets ups grpc server and opens communication with drone."""
    parser = OptionParser()
    
    # Port to to run grpc 
    parser.add_option("--sitl", action="store_true", dest="sitlOption", default=False,
                      help="Connect to a sitl simulator rather than a real drone")
    
    # Specifies lat and long for HOME position when SITL is being used.
    parser.add_option("--lat", action="store", type="float", dest="lat", default=None)
    parser.add_option("--lon", action="store", type="float", dest="lon", default=None)
    
    (options, args) = parser.parse_args()
    
    vehicle = connect_to_drone(options.sitlOption, options.lat, options.lon)
    print "Set default/target airspeed to 2"
    vehicle.airspeed = 2
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    droneconnect_pb2.add_DroneConnectServicer_to_server(DroneConnect(vehicle), server)
    #server.add_insecure_port('134.87.169.25:50051')
    server.add_insecure_port('[::]:50051')
    
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        print ("Stopping grpc server")
        #Close vehicle object before exiting script
        print ("Closing connection to drone.")
        vehicle.close()
        server.stop(0)

if __name__ == '__main__':
    serve()
    
