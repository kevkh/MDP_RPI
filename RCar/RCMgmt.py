import serial
import threading
from sys import stderr
import logging
import multiprocessing
import time
import queue as Queue
from collections import Counter
import json


class RCMgmt(multiprocessing.Process):
    print_lock = threading.Lock()
    serial_port = serial.Serial()
    m = multiprocessing.Manager()
    handle_q = m.Queue()
    connected=False
    count = 0

    def __init__(self,port,baud,timeout,job_q,header):
        multiprocessing.Process.__init__(self)
        self.job_q = job_q
        self.logger = logging.getLogger(self.__class__.__name__)
        self.header=header
        self.serial_port.baudrate = baud
        self.serial_port.port = port
        self.serial_port.timeout = timeout
        self.daemon=True
        self.start()


    def connect(self):
        #If it is currently open, close the current connection and re-open
        if self.serial_port.isOpen():
            self.serial_port.close()
        try:
            self.serial_port.open()
            self.connected=True
            print("[LOG][STM]","RC-Car Connection opened")
            return True
        except serial.SerialException as e:
            print("[ERR][STM]","Unable to open serial port")
#            self.logger.debug(e)
            return False

    def getPacketHeader(self):
        return self.header

    def run(self):
        if(self.connect()==True):
            t1 = threading.Thread(target=self.read, args=(self.job_q,))
            t2 = threading.Thread(target=self.handleProcessor, args=())
            t1.start()
            t2.start()

            t1.join()
            t2.join()

    def handleProcessor(self):
        while True:
            if(self.handle_q.qsize()!=0):
                packet = self.handle_q.get().strip()
                self.handle_q.task_done()
                print("RC-Car is handling : "+packet+"   \n")
                self.write(packet)

            time.sleep(0.000001)

    def handle(self,packet):
        self.handle_q.put(packet)

    
    # From RPI TO STM
    def write(self,message):
        if self.serial_port.isOpen():
            message = message.strip()
            self.serial_port.write(message.encode('utf-8')) 
            print("[SEND][STM]:",message)   # The message here is taken from ALG
            
            #print(self.serial_port.write(message.encode('utf-8')) )
        else:
            print("[ERR][STM]:","Serial port not open")

    # From STM TO RPI
    def read(self,job_q):
        in_buffer = ""

        while True:
            try:
                data = self.serial_port.readline().strip() #non-blocking

                if len(data) == 0:
                    continue
                print('raw data from STM:', data.decode('utf-8'))
                data = data.decode('utf-8')
                
                #Week 8,
                print("RC Mgmt STM to RPI", data)   #Sending '$' to ALG for ACK
                job_q.put(self.header+ ":ALG:" + data  + "\n")  # IS it ACK? Gotta check
                
                #Week 9

            except serial.SerialException as e:
                print >> stderr,(self.__class__.__name__,e)
                self.logger.debug(e)
                while self.connected==False:
                     self.connect()
                     print("Reconnecting STM in 3 seconds...")
                     time.sleep(3)
                break

            time.sleep(0.000001)

#job_q = Queue()
#RC-Car = RC-CarManager("COM3",115200,0,job_q)

# Fast car flow:
# 1. AND send a 'start' string to ALG to trigger obstacle list
# 2. ALG will send movement one by one to STM via RPI
# 3. Once IR sensor detects obstacle, STM will send the IR values over to ALG to stop the send a "STOP" command (x) to stop the car and take a picture
# 4. Image will be captured, the IMG_RESULT will be processed, then send the IMG Result to ALG to continue the left/right movement
# 5. Step 2 to 4 will be repeated until the car reaches the end of the carpark
# 6. End of run


