""" bootstrap your kervi dashboards here """
from kervi.dashboard import Dashboard, Camboard, DashboardPanel

#Create the dashboards for your Kervi application here.

#A camboard is a special dashbord where the background is a video feed.
#is_default signals that this dashbord is shown first when ui starts.
#cam1 is the id of the camera that should be used as video source.
MAIN = Camboard("cam", "Main", "cam1", is_default=True)
MAIN.add_panel(DashboardPanel("section1"))

#Standard dashboard with several panels where sensors are placed.
#Each sensor create links to one or more dashboard panels 
SYSTEM = Dashboard("system", "System")
SYSTEM.add_panel(DashboardPanel("cpu", columns=2, rows=2, collapsed=True))
SYSTEM.add_panel(DashboardPanel("memory", columns=2, rows=2, collapsed=True))
SYSTEM.add_panel(DashboardPanel("log", columns=2, rows=2, title="Log", user_log=True))
SYSTEM.add_panel(DashboardPanel("disk", columns=1, rows=1))
SYSTEM.add_panel(DashboardPanel("power", columns=1, rows=1, title="Power"))
SYSTEM.add_panel(DashboardPanel("light", columns=2, rows=1, title="Light"))
