
import time
from protocols.home_easy import HomeEasy
from driver.arduino import Arduino433

a = HomeEasy(address="19266510", device="1", onoff="1")

devices = Arduino433.list_devices()
print(devices)

b = Arduino433(devices[1])
b.open()

c = True
while 1:
    a.set_onoff(c)
    a.generate_bit_code()
    b.send(a.get_transmit_data())
    c = not c
# time.sleep(2)
# b.send(a.get_transmit_data())
# time.sleep(2)
# b.send(a.get_transmit_data())
# time.sleep(2)
# b.send(a.get_transmit_data())
# time.sleep(2)
# b.send(a.get_transmit_data())
# time.sleep(2)
# b.send(a.get_transmit_data())
