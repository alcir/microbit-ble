import RPi.GPIO as GPIO
import numpy as np
import time
from threading import Thread

from bluepy import btle

GPIO.setmode(GPIO.BOARD)


class us():
    def __init__(self):
        self.TRIG = 16
        self.ECHO = 18
        GPIO.setup(self.TRIG, GPIO.OUT)
        GPIO.setup(self.ECHO, GPIO.IN)

    def _misura(self):
        # set Trigger to HIGH
        GPIO.output(self.TRIG, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(self.TRIG, False)

        StartTime = time.time()
        StopTime = time.time()

        self.timeout = 0
        # save StartTime
        count = 0
        while GPIO.input(self.ECHO) == 0:
            StartTime = time.time()
            count += 1
            if (count > 1000):
                self.timeout = 1
                break
        # save time of arrival
        count = 0
        while GPIO.input(self.ECHO) == 1:
            StopTime = time.time()
            count += 1
            if (count > 1000):
                self.timeout = 1
                break

        if (self.timeout != 1):
            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            distance = (TimeElapsed * 34300) / 2
        else:
            distance = 10000

        return distance


class luci():
    def __init__(self, quale, PIN):
        self.quale = quale
        self.PIN = PIN
        GPIO.setup(PIN, GPIO.OUT)
        self.stato = 1
        print("Init luce "+str(self.quale))
        self._spegni()

    def _accendi(self):
        if (self.stato == 0):
            print("Luci "+str(self.quale)+" accendi")
            GPIO.output(self.PIN, GPIO.HIGH)
            self.stato = 1

    def _spegni(self):
        if (self.stato == 1):
            print("Luci "+str(self.quale)+" spegni")
            GPIO.output(self.PIN, GPIO.LOW)
            self.stato = 0


class motore():
    def __init__(self, A, B, EN, INVERTITO, NOME):
        self.stato = 1
        # self.luceRossa = luci("rossa")
        # self.luceVerde = luci("verde")
        # self.luceBianca = luci("bianca")

        self.INVERTITO = INVERTITO
        self.A = A
        self.B = B
        self.EN = EN

        GPIO.setup(A, GPIO.OUT)
        GPIO.setup(B, GPIO.OUT)
        GPIO.setup(EN, GPIO.OUT)
        self.FREQ = 1024
        self.pwm = GPIO.PWM(EN, self.FREQ)
        if (self.INVERTITO == 1):
            print("INV "+NOME)
            # self.pwm.start(self.FREQ)
            self.pwm.start(0)
        else:
            print("NON "+NOME)
            self.pwm.start(0)

        print("Motore "+NOME+" inizializzato")
        self._ferma()

    def __dutycycle(self, speed):
        print("speed: "+str(speed))
        if (self.INVERTITO == 1):
            return self.FREQ - speed
        else:
            return speed

    def __printspeed(self, speed):
        print("speed: "+str(speed))
        return speed

    def _attiva(self):
        GPIO.output(self.EN, True)

    def _ferma(self):
        GPIO.output(self.A, False)
        GPIO.output(self.B, False)
        # GPIO.output(self.EN, False)

    def _disattiva(self):
        GPIO.output(self.A, False)
        GPIO.output(self.B, False)
        GPIO.output(self.EN, False)

    def __normal(self, speed):
        if (speed <= 10):
            return 0
        elif (speed > 10 and speed <= 50):
            return 50
        elif (speed > 50 and speed <= 70):
            return 70
        elif (speed > 70 and speed <= 100):
            return 100

    def _avanti(self, speed):
        GPIO.output(self.A, True)
        GPIO.output(self.B, False)
        self.pwm.ChangeDutyCycle(self.__dutycycle(self.__normal(speed)))

    def _indietro(self, speed):
        GPIO.output(self.A, False)
        GPIO.output(self.B, True)
        self.pwm.ChangeDutyCycle(self.__printspeed(self.__normal(speed)))


class movimento():
    def __init__(self):
        self.stato = 1
        self.luceRossa = luci("rossa", 29)
        self.luceVerde = luci("verde", 26)
        self.luceBianca = luci("bianca", 24)
        self.luceBlu = luci("blu", 22)
        self.motoreS = motore(36, 38, 40, 0, "SX")
        self.motoreD = motore(35, 33, 31, 0, "DX")
        # luceRossa._accendi()
        # luceVerde._spegni()
        print("Movimento inizializzato")
        self._stop()
        self.us = us()
        # print("Stato: "+str(self._getStato()))

    def _stop(self):
        if (self._getStato() == 1):
            print("Motori fermi")
            self.motoreS._ferma()
            self.motoreD._ferma()
            self.luceVerde._spegni()
            self.luceBianca._spegni()
            self.luceBlu._spegni()
            self.luceRossa._accendi()
            self._setStato(0)

    def _disattiva(self):
        if (self._getStato() == 1):
            print("Motori disattiva")
            self.motoreS._disattiva()
            self.motoreD._disattiva()
            self.luceVerde._spegni()
            self.luceBianca._accendi()
            self._setStato(0)
            self.luceRossa._accendi()

    def _start(self):
        if (self._getStato() == 0):
            print("Motori attivi")
            self.motoreS._attiva()
            self.motoreD._attiva()
            self.luceVerde._accendi()
            self.luceBianca._spegni()
            self.luceRossa._spegni()
            self._setStato(1)

    def _setStato(self, stato):
        self.stato = stato
        # print("Setstato: "+str(stato))

    def _getStato(self):
        return self.stato

    class _coordinate():
        def __init__(self, coord):
            # print("COO")
            # self.x = translate(coord[0], 32, 1040)
            # self.y = translate(coord[1], 32, 980)

            self.xorig = coord[0]
            self.yorig = coord[1]

        # def _getx(self):
        #     return self.x
        #
        # def _gety(self):
        #     return self.y

        def _getxorig(self):
            # if (self.xorig < 0):
            #     if (self.xorig < 980):
            #         valore = 980
            #     else:
            #         valore = self.xorig
            #
            #     self.xorig = valore * 1024 / 980

            return self.xorig

        def _getyorig(self):
            return self.yorig

    def _avanti(self, coord):
        self.luceBianca._spegni()

        if (abs(coord._getyorig()) > 1024):
            valore = 1024
        else:
            valore = abs(coord._getyorig())

        if (coord._getxorig() > 1024):
            modificatore = 1024
        elif (coord._getxorig() < -1024):
            modificatore = -1024
        else:
            modificatore = coord._getxorig()

        if (modificatore > 0):
            speedDX = valore - modificatore
            speedSX = valore
        elif (modificatore < 0):
            speedDX = valore
            speedSX = valore + modificatore
        else:
            speedDX = speedSX = valore

        print("Avanti: "+str(valore))

        # self.motoreS._avanti(trasla(valore, 1024, 100))
        # self.motoreD._avanti(trasla(valore, 1024, 100))
        self.motoreS._avanti(minmax(trasla(speedSX, 1024, 100), 0, 100))
        self.motoreD._avanti(minmax(trasla(speedDX, 1024, 100), 0, 100))

    def _indietro(self, coord):

        self.luceBianca._accendi()
        if (abs(coord._getyorig()) > 1024):
            valore = 1024
        else:
            valore = abs(coord._getyorig())

        if (coord._getxorig() > 1024):
            modificatore = 1024
        elif (coord._getxorig() < -1024):
            modificatore = -1024
        else:
            modificatore = coord._getxorig()

        if (modificatore > 0):
            speedDX = valore - modificatore
            speedSX = valore
        elif (modificatore < 0):
            speedDX = valore
            speedSX = valore + modificatore
        else:
            speedDX = speedSX = valore

        print("Indietro: "+str(valore))
        self.motoreS._indietro(minmax(trasla(speedSX, 1024, 100), 0, 100))
        self.motoreD._indietro(minmax(trasla(speedDX, 1024, 100), 0, 100))

    # def _dritto(self):
    #     print("Dritto")
    #
    # def _destra(self):
    #     print("Destra")
    #
    # def _sinistra(self):
    #     print("Sinistra")

    def _manovra(self, coord):
        # print("manovra")
        if (self._getStato() == 1):
            self._start()
            xy = self._coordinate(coord)
            # print("aaaa")
            # print(xy._getx())

            # if(xy._getx() > 4):
            #     self._destra()
            # elif(xy._getx() < -4):
            #     self._sinistra()
            # else:
            #     self._dritto()
            print(xy._getyorig())
            if(xy._getyorig() > 100):
                self._indietro(xy)
            else:
                if (self.us._misura() <= 10):
                    self.luceBlu._accendi()
                    self.motoreS._avanti(0)
                    self.motoreD._avanti(0)
                else:
                    self.luceBlu._spegni()
                    self._avanti(xy)
        # else:
        #     self._stop()


# def translate(value, min, max):
#     # return value * min / max
#     if (value > max):
#         value = max
#     if (value < min):
#         value = min
#     return value * 1024 / min


def trasla(value, maxorig, maxtrasl):
    return value * maxtrasl / maxorig


def minmax(value, min, max):
    if (value < min):
        return min
    elif (value > max):
        return max
    else:
        return value


# try:
# muovi = movimento()
# sleep(3)
# print("cane")
# muovi._start()
# muovi._manovra([100, 900])
#
# for ics in range(-200, 200):
#     for ipsilo in range(-1024, 1024):
#         print(ics, ipsilo)
#         muovi._manovra([ics, ipsilo])
#     # sleep(1)
# # for count in range(0, 1040, 140):
# #     print(count)
# #     muovi._manovra([0, -count])
# #     sleep(0.1)
# #
# # sleep(3)
# # print("indietro")
# # sleep(3)
# # for count in range(0, 1040, 4):
# #     print("indietr", count)
# #     muovi._manovra([0, count])
# #     sleep(0.1)
#
# sleep(3)
#
# muovi._stop()
#
# GPIO.cleanup()


class MyDelegate(btle.DefaultDelegate):
    def __init__(self, muovi):
        btle.DefaultDelegate.__init__(self)
        self.muovi = muovi

    def handleNotification(self, cHandle, data):
        # print "A notification was received: {}".format(ord(data))
        if(cHandle == 35 and ord(data) == 1):
            print "Button A"
            self.muovi._stop()
            # motore._setStato(self.motore, 0)
            # print("mmmm "+str(self.motore._getStato()))

        elif(cHandle == 38 and ord(data) == 1):
            print "Button B"
            self.muovi._start()
            # motore._setStato(self.motore, 1)
            # print("mmmm "+str(self.motore._getStato()))


class microbitCollector(Thread):

    def __init__(self, device_name, device_mac, sampling_interval_sec=1,
                 retry_interval_sec=5):
        Thread.__init__(self)
        print("microbit")
        self.muovi = movimento()
        self.conn = None
        self.device_name = device_name
        self.device_mac = device_mac
        self._sampling_interval_sec = sampling_interval_sec
        self._retry_interval_sec = retry_interval_sec
        # Connects with re-try mechanism
        self._re_connect()
        self.start()

    def _connect(self):
        print "Connecting..."
        self.conn = btle.Peripheral(self.device_mac, btle.ADDR_TYPE_RANDOM)
        self.conn.setSecurityLevel("medium")
        print "Connected..."

        # self._enable()

    def run(self):
        while True:

            while True:
                try:
                    svc = self.conn.getServiceByUUID(
                                "e95d0753-251d-470a-a062-fa1922dfa9a8")
                    ch = svc.getCharacteristics(
                                "e95dca4b-251d-470a-a062-fa1922dfa9a8")[0]

                    CCCD_UUID = 0x2902

                    ch_cccd = ch.getDescriptors(forUUID=CCCD_UUID)[0]
                    # print(ch_cccd)
                    ch_cccd.write(b"\x00\x00", False)

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

                    self.conn.setDelegate(MyDelegate(self.muovi))

                    while True:
                        coord = np.fromstring(ch.read(), dtype=np.int16, count=3)
                        if self.conn.waitForNotifications(0.1):
                            # handleNotification() was called
                            continue
                        self.muovi._manovra(coord)

                except Exception as e:
                    print str(e)
                    self.muovi._stop()
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
                print str(e)
                self.muovi._stop()
                time.sleep(self._retry_interval_sec)


def main():
    microbitCollector(device_name="microbit",
                      device_mac="E4:6D:B6:FC:83:A8",
                      sampling_interval_sec=1)

    while True:
        time.sleep(100)
        pass


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        GPIO.cleanup()
        pass
