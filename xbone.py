#XBONE PY by Griffin Brown
#This software is released under the MIT license. Use it however you want.
 
import os
import platform

#Get the current OS so we can import the right things and use proper logic depending on OS
currentOS = platform.system()

#Check if device found and/or device connected
bDeviceFound = False
bDeviceConnected = False

#Seconds of no events from device to consider a disconnect
timeoutSeconds = 30
timeoutSecondsLeft = 0

#Values of analog inputs and button inputs
vAnalogL = [0, 0] #Left stick
vAnalogR = [0, 0] #Right stick
vAnalogD = [0, 0] #D-Pad, this is an analog because it's two axes that can equal -1, 0, or 1.
vAnalogZ = [0, 0] #Triggers

vBtnFace = [0, 0, 0, 0] #Face buttons in order of [A, B, X, Y]
vBtnFront = [0, 0] #Front buttons in order of [Start, Select]. On the controller Start and Select are the left and right buttons respectively.
vBtnTr = [0, 0] #Trigger buttons in order of [Left Trigger, Right Trigger]

#Check OS and import the proper prerequisites
if currentOS == "Windows":
    from inputs import devices, get_gamepad, DeviceManager
    print("Currently running Windows")
else:
    print("Operating System: " + str(currentOS) + " not supported. Now exiting!")
    exit()

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

#Try to make sure we have a device before continuing to main loop
findDevice()

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