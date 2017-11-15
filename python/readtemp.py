from bluepy import btle

p = btle.Peripheral("XX:XX:XX:XX:XX:XX", btle.ADDR_TYPE_RANDOM)

# Without this, the reading of the temperature characteristic fails 
p.setSecurityLevel("medium")

svc = p.getServiceByUUID("e95d6100-251d-470a-a062-fa1922dfa9a8")
ch = svc.getCharacteristics("e95d9250-251d-470a-a062-fa1922dfa9a8")[0]

print "Temperature: {}".format(ord(ch.read()))
