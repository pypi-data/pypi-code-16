from pysics.Vector import vector

class engine:
	def __init__(self, parent, Rigid = False):
		self.parent = parent
		self.Rigid = Rigid
		self.gravityconstant = 9.81

	def applyphysics():
		accel = self.parent.position.acceleration
		speed = self.parent.position.speed
		
		