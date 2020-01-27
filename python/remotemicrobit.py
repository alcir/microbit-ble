import time
import subprocess
from threading import Thread
from bluepy import btle

# Guess your keyboard using "sudo evemu-describe" or "ls /dev/input/by-path/"
kbdDevice="/dev/input/by-path/your_keyboard"

# This is the MAC address of the microbit
device_mac="XX:XX:XX:XX:XX:XX"

# handle for button A
handleA = 0
# handle for button B
handleB = 0

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        # print "A notification was received: {}".format(ord(data))
        if(cHandle == handleA and ord(data) == 1):
            print ("Button A")
            subprocess.call(["evemu-event", kbdDevice, "--type", "EV_KEY", "--code", "KEY_LEFT", "--value", "1", "--sync"])
            subprocess.call(["evemu-event", kbdDevice, "--type", "EV_KEY", "--code", "KEY_LEFT", "--value", "0", "--sync"])

        elif(cHandle == handleB and ord(data) == 1):
            print ("Button B")
            subprocess.call(["evemu-event", kbdDevice, "--type", "EV_KEY", "--code", "KEY_RIGHT", "--value", "1", "--sync"])
            subprocess.call(["evemu-event", kbdDevice, "--type", "EV_KEY", "--code", "KEY_RIGHT", "--value", "0", "--sync"])

class microbitCollector(Thread):

    def __init__(self, device_name, device_mac, sampling_interval_sec=1,
                 retry_interval_sec=5):
        Thread.__init__(self)
        print("microbit")
        self.conn = None
        self.device_name = device_name
        self.device_mac = device_mac
        self._sampling_interval_sec = sampling_interval_sec
        self._retry_interval_sec = retry_interval_sec
        # Connects with re-try mechanism
        self._re_connect()
        self.start()

    def _connect(self):
        print ("Connecting...")
        self.conn = btle.Peripheral(self.device_mac, btle.ADDR_TYPE_RANDOM)
        self.conn.setSecurityLevel("medium")
        print ("Connected...")

    def run(self):
        while True:
            while True:
                try:
                    # svc = self.conn.getServiceByUUID(
                    #             "e95d0753-251d-470a-a062-fa1922dfa9a8")
                    # ch = svc.getCharacteristics(
                    #             "e95dca4b-251d-470a-a062-fa1922dfa9a8")[0]

                    CCCD_UUID = 0x2902

                    # ch_cccd = ch.getDescriptors(forUUID=CCCD_UUID)[0]
                    # # print(ch_cccd)
                    # ch_cccd.write(b"\x00\x00", False)

                    svcButton = self.conn.getServiceByUUID(
                        "e95d9882-251d-470a-a062-fa1922dfa9a8")
                    chA = svcButton.getCharacteristics(
                        "e95dda90-251d-470a-a062-fa1922dfa9a8")[0]
                    chB = svcButton.getCharacteristics(
                        "e95dda91-251d-470a-a062-fa1922dfa9a8")[0]

                    ch_cccdA = chA.getDescriptors(forUUID=CCCD_UUID)[0]
                    ch_cccdA.write(b"\x01\x00", False)

                    ch_cccdB = chB.getDescriptors(forUUID=CCCD_UUID)[0]
                    ch_cccdB.write(b"\x01\x00", False)

                    global handleA
                    handleA = chA.getHandle()
                    global handleB
                    handleB = chB.getHandle()

                    self.conn.setDelegate(MyDelegate())

                    while True:
                        if self.conn.waitForNotifications(0.1):
                            # handleNotification() was called
                            continue

                except Exception as e:
                    print (str(e))
                    self.conn.disconnect()
                    break

            time.sleep(self._retry_interval_sec)
            self._re_connect()

    def _re_connect(self):
        while True:
            try:
                self._connect()
                break
            except Exception as e:
                print (str(e))
                time.sleep(self._retry_interval_sec)


def main():
    microbitCollector(device_name="microbit",
                      device_mac=device_mac,
                      sampling_interval_sec=1)

    while True:
        time.sleep(100)
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
pass
