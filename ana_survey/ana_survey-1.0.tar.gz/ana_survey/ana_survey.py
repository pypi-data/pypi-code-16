from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from numpy import *
from pandas import *
from math3d import *
from math3d.geometry import *
from math3d.dynamics import *
from math3d.interpolation import *
from math3d.reference_system import *

def GetPCBCM(CA,CB,CC,CD):
    '''
    Calculate the PCB geometry center based on its 4 corners
    '''
    x=0.5*(0.5*(CA[0]+CB[0])+0.5*(CC[0]+CD[0]))
    y=0.5*(0.5*(CA[1]+CB[1])+0.5*(CC[1]+CD[1]))
    z=0.5*(0.5*(CA[2]+CB[2])+0.5*(CC[2]+CD[2]))
    return x,y,z

def GetPCBOr(CA,CB,CC,CD):
    '''
    Obtaine the oreintation of PCB
    ''' 
    
    RotZx = 0.5*(0.5*(CC[0]+CD[0])-0.5*(CA[0]+CB[0])) 
    RotZy = 0.5*(0.5*(CC[1]+CD[1])-0.5*(CA[1]+CB[1]))
    RotZz = 0.5*(0.5*(CC[2]+CD[2])-0.5*(CA[2]+CB[2]))
    
    RotXx = 0.5*(CB[0]-CA[0])
    RotXy = 0.5*(CB[1]-CA[1])
    RotXz = 0.5*(CB[2]-CA[2])
    
    RotZ = Vector(RotZx,RotZy,RotZz)
    RotX = Vector(RotXx,RotXy,RotXz)
    RotY = RotZ.cross(RotX)
    
    #obtain the rotaion of VX, VY from original X and Y
    o1= Orientation.new_from_xy(RotX,RotY)
    gamm, beta, alph = o1.to_euler("xyz")
    return gamm, beta, alph  


def GetSensorPo(CA,CB,CC,CD):
    '''
    Obtaine the position of Hall probe in the Belle frame
    ''' 
    
    #Vector of B sensor in PCB CM frame
    #VB_PCB=[1.62,-1.6,-17.88]
    #Just for test
    VB_PCB=[0.0,-10.0,0.0]

    #Obtain the orientaiton of B sensor in Belle frame
    gamm,beta,alph=GetPCBOr(CA,CB,CC,CD)
    
    #Rotate the vector on B sensor in PCB CM frame to Belle frame
    RT = Orientation.new_euler((gamm,beta,alph),'xyz')
    VB_Belle=RT*VB_PCB
    
    #Obtain the position of PCB in Belle frame
    VPCB_Belle=GetPCBCM(CA,CB,CC,CD)
    
    #Add the vector of B sensor to the vector of PCB
    Sensor_Belle = VB_Belle + VPCB_Belle
    return Sensor_Belle

def GetPCBOr_pin(CA,CB,CC):
    '''
    Obtaine the orientation of Hall probe in the Belle frame based on 3 pins' position
    ''' 
    
    VAC = Vector((array(CC)-array(CA))[0],(array(CC)-array(CA))[1],(array(CC)-array(CA))[2])
    VAB = Vector((array(CB)-array(CA))[0],(array(CB)-array(CA))[1],(array(CB)-array(CA))[2])
    VY = VAC.cross(VAB)
    
    PZ = 0.39266*(array(CB)-array(CC))+array(CC)
    VZ = Vector((PZ-array(CA))[0],(PZ-array(CA))[1],(PZ-array(CA))[2])
    
    VX = VY.cross(VZ)
    
    #obtain the rotaion of VX, VY from original X and Y
    o1= Orientation.new_from_xy(VX,VY)
    gamm, beta, alph = o1.to_euler("xyz")

    return gamm, beta, alph 

def GetSensorPo_pin(CA,CB,CC):
    '''
    Obtaine the position of Hall probe in the Belle frame based on 3 pins' postion
    ''' 

    #Vector of B sensor in PCB frame, origin if A
    VB_PCB=Vector(6.697,-1.6,6.44)
    VCA = Vector(CA[0],CA[1],CA[2])
    #Only for test
    #VB_PCB=[0.0,-10.0,0.0]
    
    #Obtain the orientaiton of B sensor in Belle frame
    gamm,beta,alph=GetPCBOr_pin(CA,CB,CC)
    
    #Rotate the vector on B sensor in PCB CM frame to Belle frame
    RT = Orientation.new_euler((gamm,beta,alph),'xyz')
    VB_Belle=RT*VB_PCB
    
    #Add the vector of B sensor to the vector of PCB        
    Sensor_Belle = VB_Belle + VCA
    
    return Sensor_Belle.get_array()

def Robot_2Dto3D(x,y,plane):
    '''
    Transform the position of pins on plane to 3D spactial coordinate
    '''

    z = x
    R = 155 #unit: mm, need to be updated 
    theta = pi/6.0 #assumed number
    E1 = 0.0 #depth of edge A
    E2 = 0.0 #depth of edge B
    La = y # or La = W - y, depend on the defination of reference side
    r = sqrt((R - La*cos(theta))**2+(La*sin(theta))**2)
    
    Delthe = d/cos(theta)/R
    if plane == "1A": phi0 = 0    
    if plane == "1B": phi0 = Delthe    
    if plane == "2A": phi0 = pi*2/3    
    if plane == "2B": phi0 = pi*2/3+Delthe    
    if plane == "3A": phi0 = pi*4/3    
    if plane == "3B": phi0 = pi*4/3+Delthe    

    phip = arcsin((La*sin(theta))/r)
    
    phi = phi0 + phip
    
    return r, phi, z    


def Sel_points(d,d_new):
    d1=d[d['Feature Name'].str.contains('Point')]
    d1=d1.reset_index(drop=True)
    d1.to_csv("../result/"+d_new+".csv")
    x=[]
    y=[]
    z=[]
    for i in range(len(d1['Feature Name'])):
        if i%4 == 0: x.append(d1['Actual'][i])
        if i%4 == 1: y.append(d1['Actual'][i])
        if i%4 == 2: z.append(d1['Actual'][i])
    return x, y, z

def Plot_points(x, y, z, name='PCB_3D'):
    fig = plt.figure(figsize=(12,12))
    ax = fig.gca(projection='3d')
    ax.scatter(array(x), array(z), array(y), c='r', marker='o')
    ax.view_init(elev=20., azim=-50)
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    fig.savefig("../result/"+name+".pdf")




