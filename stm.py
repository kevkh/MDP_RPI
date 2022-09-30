import serial
import time
import threading
global ser

class STMConnection():

    def thread_recv(self):
        global ser
        ser=serial.Serial('/dev/ttyUSB0',115200,timeout=0.5)
        read = ser.readall()
        if len(read) > 0:
            #print(read)
            return(read.decode())

    def thread_send(self,text):
        global ser
        #while True:
        serial.Serial('/dev/serial/by-id/usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0002-if00-port0',115200,timeout=0.5).write(b'd157')
        try:
            ser=serial.Serial('/dev/ttyUSB1',115200,timeout=0.5)
        except:
            ser=serial.Serial('/dev/ttyUSB0',115200,timeout=0.5)
        ser.write(text)
        print(ser.readline())
        time.sleep(0.5)

    def connect_STM(self):
        #global ser
        try:
            ser=serial.Serial('/dev/ttyUSB1',115200,timeout=0.5)
        except:
            ser=serial.Serial('/dev/ttyUSB0',115200,timeout=0.5)

        print("Connected to STM")
        #recv_data = threading.Thread(target=thread_recv)
        #send_data = threading.Thread(target=thread_send)
        return ser
        #send_data.start()

    def listen_and_write(self):
        while True:
            self.thread_recv()
            #self.thread_send(input(),stm)
            
if __name__ == '__main__':
    stmConnection = STMConnection()
   
    stmConnection.thread_send(b'd157')    # w is forward, s is reverse
   
   # stmConnection.thread_send(b'd079')  # Turn 90 deg, d is right, a is left
   # stmConnection.thread_send(b'd157')  # Turn 180 deg, d is right, a is left
   # stmConnection.thread_send(b'a234')  # Turn 270 deg, d is right, a is left
   # stmConnection.thread_send(b'd311')  # Turn 360 deg, d is right, a is left
 
    
