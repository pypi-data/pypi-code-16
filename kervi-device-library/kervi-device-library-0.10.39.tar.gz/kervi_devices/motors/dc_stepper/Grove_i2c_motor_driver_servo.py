

from kervi.hal import i2c
from kervi.hal.dc_motor_controller import DCMotorControllerBase

MOTOR_SPEED_SET = 0x82
PWM_FREQUENCE_SET = 0x84
DIRECTION_SET = 0xaa
MOTOR_SET_A = 0xa1
MOTOR_SET_B = 0xa5
NOTHING = 0x01
ENABLE_STEPPER = 0x1a
UNENABLE_STEPPER = 0x1b
STEPERNU = 0x1c
I2C_MOTOR_DRIVER_ADD = 0x0f #Set the address of the I2CMotorDriver



class MotorDeviceDriver(DCMotorControllerBase):
    def __init__(self, address=I2C_MOTOR_DRIVER_ADD, bus=None):
        DCMotorControllerBase.__init__(self, "Grove i2c motor driver", 2)
        self.i2c = i2c(address, bus)
        



    ##set the steps you want, if 255, the stepper will rotate continuely;
    def SteperStepset(stepnu):
        bus.write_i2c_block_data(I2C_MOTOR_DRIVER_ADD,STEPERNU,[stepnu,NOTHING])

    ## Enanble the i2c motor driver to drive a 4-wire stepper. the i2c motor driver will
    ## driver a 4-wire with 8 polarity  .
    ## Direction: stepper direction ; 1/0
    ## motor speed: defines the time interval the i2C motor driver change it output to drive the stepper
    ## the actul interval time is : motorspeed * 4ms. that is , when motor speed is 10, the interval time 
    ## would be 40 ms

    def StepperMotorEnable(Direction,motorspeed):
            bus.write_i2c_block_data(I2C_MOTOR_DRIVER_ADD,ENABLE_STEPPER,[Direction,motorspeed])

    ##function to uneanble i2C motor drive to drive the stepper.
    def StepperMotorUnenable():
        bus.write_i2c_block_data(I2C_MOTOR_DRIVER_ADD,UNENABLE_STEPPER,[NOTHING,NOTHING])

    ##Re-maps a number from one range to another. That is, a value of fromLow would get mapped to toLow, 
    ##a value of fromHigh to toHigh, values in-between to values in-between, etc.
    ##see http://www.arduino.cc/en/Reference/Map
    def Map(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    ##Function to set the 2 DC motor speed
    ##motorSpeedA : the DC motor A speed; should be 0~100;
    ##motorSpeedB: the DC motor B speed; should be 0~100;

    def MotorSpeedSetAB(MotorSpeedA , MotorSpeedB):
        MotorSpeedA=Map(MotorSpeedA,0,100,0,255)
        MotorSpeedB=Map(MotorSpeedB,0,100,0,255)
        bus.write_i2c_block_data(I2C_MOTOR_DRIVER_ADD,MOTOR_SPEED_SET,[MotorSpeedA,MotorSpeedB])

    ##set the prescale frequency of PWM, 0x03 default;
    def MotorPWMFrequenceSet(Frequence):   
        bus.write_i2c_block_data(I2C_MOTOR_DRIVER_ADD,PWM_FREQUENCE_SET,[Frequence,NOTHING])

    ##set the direction of DC motor. 
    ## Adjust the direction of the motors 0b0000 I4 I3 I2 I1
    def MotorDirectionSet(Direction):
        bus.write_i2c_block_data(I2C_MOTOR_DRIVER_ADD,DIRECTION_SET,[Direction,NOTHING]) 

    ##you can adjust the driection and speed together
    def MotorDriectionAndSpeedSet(Direction,MotorSpeedA,MotorSpeedB) :
        MotorDirectionSet(Direction)
        MotorSpeedSetAB(MotorSpeedA,MotorSpeedB)

    def stepperrun():
        print(&quot;sent command to + direction, very fast&quot;)
        SteperStepset(255)
        StepperMotorEnable(1, 1) #ennable the i2c motor driver a stepper.
        time.sleep(5)
        print(&quot;sent command to - direction, slow&quot;)
        SteperStepset(255);
        StepperMotorEnable(0, 20)
        time.sleep(5)
        print(&quot;sent command to - direction, fast&quot;)
        StepperMotorEnable(0, 2) # ennable the i2c motor driver a stepper.
        delay(5000);
        print(&quot;sent command to + direction,100 steps, fast&quot;)
        SteperStepset(100)
        StepperMotorEnable(1,5)
        time.sleep(5)

        print(&quot;sent command to shut down the stepper&quot;)
        StepperMotorUnenable();
        time.sleep(5)

        print(&quot;sent command to - direction, slow, and 10 steps then stop&quot;)
        SteperStepset(10)
        StepperMotorEnable(0,40)
        time.sleep(5)
        print(&quot;sent command to shut down the stepper&quot;)
        StepperMotorUnenable()
        delay(5000);

    
