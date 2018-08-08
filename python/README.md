These Python examples make use of [bluepy](https://github.com/IanHarvey/bluepy): a Python interface to Bluetooth LE on Linux

* `tempnotify.py` print temperature data with handleNotification [micro:bit blocks](https://github.com/alcir/microbit-ble/raw/master/img/makeblocktemp1.png)
* `readtemp.py` read the temperature value and exit [micro:bit blocks](https://github.com/alcir/microbit-ble/raw/master/img/makeblocktemp1.png)
* `uart_collector.py` receive a string from the micro:bit via UART, using notification handler. Reconnect on disconnection. [micro:bit blocks](https://github.com/alcir/microbit-ble/raw/master/img/makeblockuart4.png)
* `accelerometerBall.py`, a simple game to move a ball on an OLED screen connected to a Raspberry Pi, using data collected from the micro:bit accelerometer https://youtu.be/AE-GGFhqqPo Note: using bluetooth notify handler, there is a general slowdown due to the OLED interface, leading to ball moves heavily lagged compared to the accelerometer data
* `robotcar.py` moving a robot car using micro:bit as remote. The accelerometer moves the car (forward, backward, right, left). The A and B buttons enable or disable the L293D IC.
* `microbitremote.py` use the micro:bit buttons as a remote controller to present your slides on, for instance, Libreoffice Impress on Linux, using evemu-event command line utility [micro:bit blocks](https://github.com/alcir/microbit-ble/raw/master/img/microbitremote.png)
