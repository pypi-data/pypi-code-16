from tfs.network import Network
class LeNet(Network):
  def setup(self):
    (self.conv2d([5,5],10,[1,1])
     .conv2d([5,5],10,[1,1])
     .fc(256)
     .fc(10, activation=None)
    )
