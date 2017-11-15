# microbit-ble

How to read data from micro:bit via Bluetooth on Linux.

## No /dev/ttySOMETHING for UART

Maybe due to the Bluetooth Low Energy protocol or implementation, I have not found the possibility to create a serial device in Linux. So the simplest way to read data from the micro:bit is Python. In this case I use **bluepy** https://github.com/IanHarvey/bluepy

## Testing Bluetooth services from the shell

For testing purposes, you can use the `bluetoothctl`, `hcidump` (to sniff the bluetooth communication) and `gatttool` commands from **bluez** package.

## micro:bit UART

In the micro:bit device, using MakeCode, it is possible to enable UART in order to send and receive arbitrary data to and from the connected device.
In order to get data from UART, you have to enable notification, writing "0200" on the Client Characteristic Configuration Descriptor (CCCD) of the UART Service Characteristic. The CCCD is 2902.

### UART known issue: need to reset

Using UART there is a known issue: https://lancaster-university.github.io/microbit-docs/ble/uart-service/#example-microbit-application-animal-vegetable-mineral-game *[...] This prevents the event handler from exiting. Under normal circumstances this is fine. If however the connected application loses its connection and then reconnects, the onConnected method will not execute and therefore the 'connected' variable which tracks the Bluetooth connection state will not update. The micro:bit application will now behave as though it is not in a connection and therefore functions such as sending text by pressing a button will not work. In this situation the user should simply reset their micro:bit and reconnect their smartphone application. An API which allows serial reads to unblock or perhaps threads to be terminated is under consideration for a future release of the micro:bit runtime.*"

In short: if the connection is interrupted, or the Phyton program exits without sending the disconnection message, the "forever block" containing the "Bluetooth UART write" block seems to get stuck. Even after reconnection (or rather starting the Python program again), there is no way to read any data. This lead to the need to reset the micro:bit

## Useful links

micro:bit Bluetooth profile specification: https://lancaster-university.github.io/microbit-docs/resources/bluetooth/bluetooth_profile.html

## Disclaimer

I'm not a Python developer and my knowledge of Bluethoot protocol is close to zero. So sorry for the imperfections.
