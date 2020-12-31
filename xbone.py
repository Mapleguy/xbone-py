#XBONE PY by Griffin Brown
#This software is released under the MIT license. Use it however you want.
#
#SETTINGS - EDIT THESE TO CONFIGURE XBONE PY
#
sendType = "UDP"                #Types UDP, TCP (NOT IMPLEMENTED), SERIAL (NOT IMPLEMENTED)
sendAddress = "10.0.0.255"      #Address to send processed controller data to
sendComplement = "5001"         #Complement (port or baud rate) of the sending address
sendRate = 2                    #Rate to send data at in Hz

import threading
import time
from inputs import devices, get_gamepad

if sendType == "UDP" or sendType == "TCP":
    import socket

#Check if device found and/or device connected
bDeviceFound = False
bDeviceConnected = False

#Seconds of no events from device to consider a disconnect
timeoutSeconds = 5
timeoutSecondsLeft = 0

#Values of analog inputs and button inputs
vAnalogL = [0, 0] #Left stick
vAnalogR = [0, 0] #Right stick
vAnalogD = [0, 0] #D-Pad, this is an analog because it's two axes that can equal -1, 0, or 1.
vAnalogZ = [0, 0] #Triggers

vBtnFace = [0, 0, 0, 0] #Face buttons in order of [A, B, X, Y]
vBtnFront = [0, 0] #Front buttons in order of [Start, Select]. On the controller Start and Select are the left and right buttons respectively.
vBtnTr = [0, 0] #Trigger buttons in order of [Left Trigger, Right Trigger]

def make_sendable(num):
    val = (num).to_bytes(2, byteorder="big", signed=True)
    return val

#Create packet of data
def createPacket():
    pack = bytearray(19)

    #Starting byte of 101
    pack[0] = 0b01100101

    av1 = make_sendable(vAnalogL[0])
    pack[1] = av1[0]
    pack[2] = av1[1]

    av2 = make_sendable(vAnalogL[1])
    pack[3] = av2[0]
    pack[4] = av2[1]

    av3 = make_sendable(vAnalogR[0])
    pack[5] = av3[0]
    pack[6] = av3[1]

    av4 = make_sendable(vAnalogR[1])
    pack[7] = av4[0]
    pack[8] = av4[1]

    av5 = make_sendable(vAnalogD[0])
    pack[9] = av5[0]
    pack[10] = av5[1]

    av6 = make_sendable(vAnalogD[1])
    pack[11] = av6[0]
    pack[12] = av6[1]

    av7 = make_sendable(vAnalogZ[0])
    pack[13] = av7[0]
    pack[14] = av7[1]

    av8 = make_sendable(vAnalogZ[1])
    pack[15] = av8[0]
    pack[16] = av8[1]

    #Buttons
    #This works by setting bits within the byte, each of 8 buttons corresponding to 1 of 8 bits
    bbyte = 0
    bbyte = bbyte + vBtnFace[0]  * 0b00000001
    bbyte = bbyte + vBtnFace[1]  * 0b00000010
    bbyte = bbyte + vBtnFace[2]  * 0b00000100
    bbyte = bbyte + vBtnFace[3]  * 0b00001000
    bbyte = bbyte + vBtnTr[0]    * 0b00010000
    bbyte = bbyte + vBtnTr[1]    * 0b00100000
    bbyte = bbyte + vBtnFront[0] * 0b01000000
    bbyte = bbyte + vBtnFront[1] * 0b10000000
    pack[17] = bbyte

    #Closing byte of 201
    pack[18] = 0b11001001
    return pack

#Find a proper device from a list of found devices
def findDevice():
    global bDeviceFound
    global bDeviceConnected
    print("Finding Device...")
    try:
        devices = DeviceManager()
        bDeviceFound = True
        bDeviceConnected = True
        print("Found Device")
    except:
        bDeviceFound = False
        bDeviceConnected = False
        print("No device!")

#Read analog values from event
def readAnalogs(event):
    try:
        code = event.code
        value = event.state
        if code == "ABS_X":
            vAnalogL[0] = value
        elif code == "ABS_Y":
            vAnalogL[1] = value
        elif code == "ABS_RX":
            vAnalogR[0] = value
        elif code == "ABS_RY":
            vAnalogR[1] = value
        elif code == "ABS_Z":
            vAnalogZ[0] = value
        elif code == "ABS_RZ":
            vAnalogZ[1] = value
        elif code == "ABS_HAT0X":
            vAnalogD[0] = value
        elif code == "ABS_HAT0Y":
            vAnalogD[1] = value
    except:
        pass

#Read buttons from event
def readButtons(event):
    try:
        code = event.code
        value = event.state
        if code == "BTN_SOUTH":
            vBtnFace[0] = value
        elif code == "BTN_EAST":
            vBtnFace[1] = value
        elif code == "BTN_WEST":
            vBtnFace[2] = value
        elif code == "BTN_NORTH":
            vBtnFace[3] = value
        elif code == "BTN_TL":
            vBtnTr[0] = value
        elif code == "BTN_TR":
            vBtnTr[1] = value
        elif code == "BTN_START":
            vBtnFront[0] = value
        elif code == "BTN_SELECT":
            vBtnFront[1] = value
    except:
        pass

class readThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):     
        while True:
            try:
                event = get_gamepad()[0]
            except:
                pass

            if event is not None:
                if event.ev_type == "Absolute":
                    readAnalogs(event)
                if event.ev_type == "Key":
                    readButtons(event)

class sendUDP(threading.Thread):
    def __init__(self, address, complement, rate):
        threading.Thread.__init__(self)
        self.address = address
        self.complement = complement
        self.rate = rate

        #Create UDP socket
        self.UDP = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDP.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def run(self):     
        while True:
            self.UDP.sendto(createPacket(), (self.address, int(self.complement)))
            time.sleep(1 / self.rate)

rThread = readThread()
rThread.start()

if sendType == "UDP":
    sThread = sendUDP(sendAddress, sendComplement, sendRate)
    sThread.start()