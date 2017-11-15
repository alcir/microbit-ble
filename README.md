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

## Makecode project for UART

...

## Makecode project for Temperature sensor

...

## Pairing from Linux with bluetoothctl

See Makecode Bluetooth Pairing for instructions on how to put the micro:bit pairing mode (A+B, + reset, release reset, release A+B)

<pre>
$ bluetoothctl
[NEW] Controller YY:YY:YY:YY:YY:YY pc [default]
Agent registered
[bluetooth]# scan on
Discovery started
[CHG] Controller YY:YY:YY:YY:YY:YY Discovering: yes
[NEW] Device XX:XX:XX:XX:XX:XX BBC micro:bit [pogeg]
[bluetooth]# pair XX:XX:XX:XX:XX:XX
Attempting to pair with XX:XX:XX:XX:XX:XX
...
[bluetooth]# scan off

</pre>

Usage examples

<pre>
[bluetooth]# connect XX:XX:XX:XX:XX:XX

Attempting to connect to XX:XX:XX:XX:XX:XX
[CHG] Device XX:XX:XX:XX:XX:XX Connected: yes
[CHG] Device XX:XX:XX:XX:XX:XX Name: BBC micro:bit
[CHG] Device XX:XX:XX:XX:XX:XX Alias: BBC micro:bit
Connection successful
...
[BBC micro:bit]# list-attributes 
...
[BBC micro:bit]# select-attribute 00002a26-0000-1000-8000-00805f9b34fb
[BBC micro:bit:/service000f/char0014]# read
Attempting to read /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX/service000f/char0014
[CHG] Attribute /org/bluez/hci0/dev_XX_XX_XX_XX_XX_XX/service000f/char0014 Value:
  32 2e 30 2e 30 2d 72 63 39 2d 2d 67              2.0.0-rc9--g    
  32 2e 30 2e 30 2d 72 63 39 2d 2d 67              2.0.0-rc9--g 
[BBC micro:bit:/service000f/char0014]# disconnect 
Attempting to disconnect from XX:XX:XX:XX:XX:XX
[CHG] Device XX:XX:XX:XX:XX:XX ServicesResolved: no
Successful disconnected
[CHG] Device XX:XX:XX:XX:XX:XX Connected: no
[CHG] Device YY:YY:YY:YY:YY:YY RSSI: -71
</pre>

Test UART data (we have to select TX characteristic). Note that read method is pointless, we have to use notification in order to get useful data. Conversely, in order to get temperature data, we can use read or notification. This is valid also for the Python programs.

<pre>
[BBC micro:bit]# select-attribute 6e400002-b5a3-f393-e0a9-e50e24dcca9e
[BBC micro:bit:/service0021/char0022]# attribute-info 
Characteristic - Nordic UART TX
	UUID: 6e400002-b5a3-f393-e0a9-e50e24dcca9e
	Service: /org/bluez/hci0/dev_E4_6D_B6_FC_83_A8/service0021
	Value:
  00                                               .               
	Notifying: no
	Flags: indicate
[BBC micro:bit:/service0021/char0022]# notify on 
...
[CHG] Attribute /org/bluez/hci0/dev_E4_6D_B6_FC_83_A8/service0021/char0022 Value:
  34 30 33 39                                      4039            
[CHG] Attribute /org/bluez/hci0/dev_E4_6D_B6_FC_83_A8/service0021/char0022 Value:
  34 30 34 32                                      4042            
[BBC micro:bit:/service0021/char0022]# notify off
[CHG] Attribute /org/bluez/hci0/dev_E4_6D_B6_FC_83_A8/service0021/char0022 Notifying: no
Notify stopped
</pre>

These are the services that we will use in the Python program.

For UART

| Type | UUID | Description |
| ---- | ---- | ----------- |
| Primary Service | 6e400001-b5a3-f393-e0a9-e50e24dcca9e | Nordic UART Service |
| Descriptor      | 00002902-0000-1000-8000-00805f9b34fb | Client Characteristic Configuration |
| Characteristic  | 6e400002-b5a3-f393-e0a9-e50e24dcca9e | Nordic UART TX |
| Characteristic  | 6e400003-b5a3-f393-e0a9-e50e24dcca9e | Nordic UART RX |

For temperature sensor

| Type | UUID | Description |
| ---- | ---- | ----------- |
| Primary Service |  |  |
| Descriptor      |  | Client Characteristic Configuration |
| Characteristic  |  |  |
| Characteristic  |  |  |

## Useful links

- micro:bit Bluetooth profile specification: https://lancaster-university.github.io/microbit-docs/resources/bluetooth/bluetooth_profile.html
- Makecode Bluetooth Pairing https://makecode.microbit.org/reference/bluetooth/bluetooth-pairing

## Disclaimer

I'm not a Python developer and my knowledge of Bluethoot protocol is close to zero. So sorry for the imperfections.
