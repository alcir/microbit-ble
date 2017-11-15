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

## Makecode projects

Please remember that, every time you upload new code to the micro:bit, you have to pair again the device.

### Makecode blocks for UART

![makecodeuart1](https://github.com/alcir/microbit-ble/raw/master/img/makeblockuart2.png)

Please note the reset block.
In the Python program, if we will not receive any notification (aka data from UART) for a while, we will reset the device, then try to reconnect: this is a kind of workaround for the known issue described before. 

### Makecode blocks for Temperature sensor

![makecodetemp1](https://github.com/alcir/microbit-ble/raw/master/img/makeblocktemp1.png)

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

### Using gatttool command

To read the temperature value.

<pre>
$ sudo gatttool -b E4:6D:B6:FC:83:A8  -I -t random
[XX:XX:XX:XX:XX:XX][LE]> connect 
Attempting to connect to XX:XX:XX:XX:XX:XX
Connection successful
[XX:XX:XX:XX:XX:XX][LE]> primary 
attr handle: 0x0001, end grp handle: 0x0007 uuid: 00001800-0000-1000-8000-00805f9b34fb
attr handle: 0x0008, end grp handle: 0x000b uuid: 00001801-0000-1000-8000-00805f9b34fb
attr handle: 0x000c, end grp handle: 0x000e uuid: e95d93b0-251d-470a-a062-fa1922dfa9a8
attr handle: 0x000f, end grp handle: 0x0015 uuid: 0000180a-0000-1000-8000-00805f9b34fb
attr handle: 0x0016, end grp handle: 0x0020 uuid: e95d93af-251d-470a-a062-fa1922dfa9a8
attr handle: 0x0021, end grp handle: 0xffff uuid: e95d6100-251d-470a-a062-fa1922dfa9a8
[XX:XX:XX:XX:XX:XX][LE]> char-desc 0x0021 0xffff
handle: 0x0021, uuid: 00002800-0000-1000-8000-00805f9b34fb
handle: 0x0022, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0023, uuid: e95d9250-251d-470a-a062-fa1922dfa9a8
handle: 0x0024, uuid: 00002902-0000-1000-8000-00805f9b34fb
handle: 0x0025, uuid: 00002803-0000-1000-8000-00805f9b34fb
handle: 0x0026, uuid: e95d1b25-251d-470a-a062-fa1922dfa9a8
[XX:XX:XX:XX:XX:XX][LE]> char-read-hnd 0x0023
Indication   handle = 0x000a value: 0c 00 ff ff 
Characteristic value/descriptor: 19 
</pre>

To read the notification interval (Temperature Interval) of the temperature (when enabled, see below).

<pre>
[E4:6D:B6:FC:83:A8][LE]> char-read-hnd 0x0026
Characteristic value/descriptor: e8 03
</pre>

`e8 08` that is 59395 milliseconds (UINT16 - Big Endian (AB))

So to receive temperature updates (as seen before, every 1 second circa) we have to write `0100` to the Client Characteristic Configuration Descriptor (CCCD), and `0000` in order to stop notifications.

<pre>
[XX:XX:XX:XX:XX:XX][LE]> char-write-req 0x0024 0100
Characteristic value was written successfully
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
Notification handle = 0x0023 value: 19 
[XX:XX:XX:XX:XX:XX][LE]> char-write-req 0x0024 0000
Characteristic value was written successfully
</pre>

Please note: the value to write to the UART CCCD in order to enable notifications is `0200` and not `0100`

## Bluetooth services and characteristics

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
| Primary Service | e95d6100-251d-470a-a062-fa1922dfa9a8 | MicroBit Temperature Service |
| Descriptor      | 00002902-0000-1000-8000-00805f9b34fb | Client Characteristic Configuration |
| Characteristic  | e95d9250-251d-470a-a062-fa1922dfa9a8 | Vendor specific (the temperature value) |
| Characteristic  | e95d1b25-251d-470a-a062-fa1922dfa9a8 | MicroBit Temperature Period |

## Useful links

- micro:bit Bluetooth profile specification: https://lancaster-university.github.io/microbit-docs/resources/bluetooth/bluetooth_profile.html
- Makecode Bluetooth Pairing https://makecode.microbit.org/reference/bluetooth/bluetooth-pairing

## Disclaimer

I'm not a Python developer and my knowledge of Bluethoot protocol is close to zero. So sorry for the imperfections.
