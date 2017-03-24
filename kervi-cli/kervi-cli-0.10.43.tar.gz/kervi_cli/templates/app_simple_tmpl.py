if __name__ == '__main__':
    from kervi.bootstrap import Application
    APP = Application()
    #Important GPIO must be imported after application creation
    from kervi.hal import GPIO

    from kervi.dashboard import Dashboard, DashboardPanel
    DASHBOARD = Dashboard("app", "App", is_default=True)
    DASHBOARD.add_panel(DashboardPanel("light", columns=2, rows=2, title="Light"))

    SYSTEMBOARD = Dashboard("system", "System")
    SYSTEMBOARD.add_panel(DashboardPanel("cpu", columns=2, rows=2))
    SYSTEMBOARD.add_panel(DashboardPanel("cam", columns=2, rows=2))

    #Create a streaming camera server
    from kervi.camera import CameraStreamer
    CAMERA = CameraStreamer("cam1", "camera 1")

    #link camera as background
    CAMERA.link_to_dashboard("app")
    #link camera to a panel
    #CAMERA.link_to_dashboard("system", "cam")

    from kervi.sensor import Sensor
    from kervi_devices.platforms.common.sensors.cpu_use import CPULoadSensorDeviceDriver
    #build in sensor that measures cpu use
    SENSOR_1 = Sensor("CPULoadSensor", "CPU", CPULoadSensorDeviceDriver())
    #link to sys area top right
    SENSOR_1.link_to_dashboard("*", "sys-header")
    #link to a panel, show value in panel header and chart in panel body
    SENSOR_1.link_to_dashboard("system", "cpu", type="value", size=2, link_to_header=True)
    SENSOR_1.link_to_dashboard("system", "cpu", type="chart", size=2)


    #More on sensors https://kervi.github.io/sensors.html


    #define a light controller
    from kervi.controller import Controller, UISwitchButtonControllerInput
    class MyController(Controller):
        def __init__(self):
            Controller.__init__(self, "lightController", "Light")
            self.type = "light"

            #define an input and link it to the dashboard panel
            light1 = UISwitchButtonControllerInput("lightctrl.light1", "Light", self)
            light1.link_to_dashboard("app", "light", label_icon="light", size=0)

            #define GPIO
            GPIO.define_as_output(12)

        def input_changed(self, changed_input):
            GPIO.set(12, changed_input.value)

    MY_CONTROLLER = MyController()

    APP.run()