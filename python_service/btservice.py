import osascript
import serial
import time
import traceback

from sys import platform

HELLO_WORLD     = "11\n"
HELLO_WORLD_ACK = "12"
BUTTON_PRESS    = "21\n"
BUTTON_PRESS_MUTE_ACK   = "22"
BUTTON_PRESS_UNMUTE_ACK = "23"
RST_BUTTON_PRESS = "31\n"
RST_BUTTON_PRESS_ACK = "32";
ERROR_ACK = "99"
SLEEP_MS = 0.5 # 500ms

def toString(byteString):
    return byteString.decode(encoding='UTF-8')

def readLine(serialObject):
    try:
        return toString(serialObject.readline())
    except:
        traceback.print_exc()
        return False

def openSerialObject(port,baud=9600, timeout=2):
    try:
        return serial.Serial(port, baud, timeout=timeout)
    except:
        return False

def getPort(platform, iterNumber=0):
    if platform in ["linux", "linux2"]:
        return "/dev/rfcomm%s"%iterNumber
    if platform == "darwin":
        return "/dev/tty.HC-05-SerialPort"
    else:
        raise Exception("Platform Not Known!")

def shouldItBeMute(count):
    """
        odd number of times toggle means its not muted
        as initially it was muted
    """
    return True if not count % 2 else False

def toggleMuteButton(platform):
    """
    Returns True if successful or False if error
    """
    if platform == "darwin":
        code, out, err = osascript.run("""tell application "Firefox"
            activate
            tell application "System Events" to keystroke "d" using command down
            end tell""")
        if code == 0:
            return (True, "")
        else:
            return (False, err)
    
    # TODO Implement for linux using xdotool
    if platform in ['linux', 'linux2']:
        pass

def writeLine(serialObject, flag):
    return serialObject.write(bytes(flag, 'utf-8'))


def writeButtonAck(isMute, serialObject):
    if isMute:
        writeLine(serialObject, BUTTON_PRESS_MUTE_ACK)
    else:
        writeLine(serialObject, BUTTON_PRESS_UNMUTE_ACK)


def main():

    # Find the correct bluetooth comm port based on OS (Mac and Linux)
    serialObject = False
    while(not serialObject):
        commRange = list(range(10))
        for i in commRange:
            port = getPort(platform, i)
            serialObject = openSerialObject(port)

            if not serialObject:
                print("Error opening serial object %s"%port)

            time.sleep(SLEEP_MS)

    receivedHW = False
    readData   = readLine(serialObject)

    # Wait for handshake signal from HC05
    while (readData != HELLO_WORLD):
        readData = readLine(serialObject)
        time.sleep(SLEEP_MS)
        print("Waiting for initial data ", readData)

    # Send Acknowledgement signal
    serialObject.write(bytes(HELLO_WORLD_ACK,'utf-8'))
    print("HW latched, ready to use")
    isHardwareLatched = True
 
    # Go to listening mode
    # Assumes the call starts with mute
    count = 0
    isMute = True
    while (isHardwareLatched):
        readData = readLine(serialObject)
        print("READ Data", readData)
        if readData == BUTTON_PRESS:
            successful, error = toggleMuteButton(platform)
            if successful:
                count += 1
                isMute = not isMute
                writeButtonAck(isMute, serialObject)               
                print("Successfully Toggled: isMute? %s | shouldBeMuted? %s "%(isMute, 
                        shouldItBeMute(count)))

            else:
                serialObject.write(bytes(ERROR_ACK,'utf-8'))
                print("Error Muting", error)

        elif readData == RST_BUTTON_PRESS:
            print("Reseting the systems by releasing latch")
            writeLine(serialObject, RST_BUTTON_PRESS_ACK)
            isHardwareLatched = False

        # For the condition when Software is latched but the  hardware reset and sending HELLO_WORLD
        elif readData == HELLO_WORLD:
            print("Latched incorrectly, releasing latch")
            isHardwareLatched = False

        # Short wait before checking for bluetooth serial buffer
        time.sleep(SLEEP_MS)



if __name__ == "__main__":
    while True:
        main()
        time.sleep(SLEEP_MS)

