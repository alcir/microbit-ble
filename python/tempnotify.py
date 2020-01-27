import sys
import time
from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print "A notification was received: {}".format(ord(data))

p = btle.Peripheral("XX:XX:XX:XX:XX:XX", btle.ADDR_TYPE_RANDOM)

# Without this, the reading of the temperature characteristic fails 
p.setSecurityLevel("medium")

print "Debug Services..."
for svc in p.services:
    print str(svc)

print 'Debug Characteristics...'
for ch in svc.getCharacteristics():
    print str(ch)

# Setup to turn notifications on, e.g.
svc = p.getServiceByUUID("e95d6100-251d-470a-a062-fa1922dfa9a8")
ch = svc.getCharacteristics("e95d9250-251d-470a-a062-fa1922dfa9a8")[0]
#temperature_handle = ch.getHandle()

CCCD_UUID = 0x2902

ch_cccd=ch.getDescriptors(forUUID=CCCD_UUID)[0]
ch_cccd.write(b"\x01\x00", False)

p.setDelegate( MyDelegate() )
cont=0

while True:
    if p.waitForNotifications(1.0):
       # handleNotification() was called
       continue

    print("Waiting...")
