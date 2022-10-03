import socket 
import time
#from thread import *
import threading
import multiprocessing
import logging
import queue as Queue
import re

class AlgoServer(multiprocessing.Process):
    print_lock = threading.Lock()
    handle_q = multiprocessing.Manager().Queue()

    def __init__(self,host,port,job_q,header, db):
        multiprocessing.Process.__init__(self)
        self.port = port
        self.header=header
        self.logger = logging.getLogger(self.__class__.__name__)
        self.host = host
        self.job_q = job_q
        self.c = None 
        self.daemon=True
        self.db = db 
        self.start()
        self.cmdArray = None
        

    def run(self):
        t2 = threading.Thread(target=self.handleProcessor, args=(0.00001,))
        t2.start()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(5)

        self.cmdArray = []
        while True: 
            print("[LOG][ALGOPC]","Listening for connection")
            # Create connection with client 
            self.c, addr = s.accept() 
            
            #self.c.send(b"7,8,N") #Commands from ANDROID obstacle list
                      
            # Lock acquired by client 
            self.print_lock.acquire() 
            print("[LOG][ALGOPC]","Connection from:" + str(addr[0]) +":"+ str(addr[1])) 
            #self.job_q.put(self.header+":ALG:PC Connected") 
 
            t1 = threading.Thread(target=self.thread_receive,args=(self.c,self.job_q,))
            
            t1.start()
            t1.join()
                   
        s.close()
        t2.join() 

    def getPacketHeader(self):
        return self.header


    def handleProcessor(self,delay):
        while True:
            if(self.handle_q.qsize()!=0):
                packet = self.handle_q.get().strip()  # Android's obs list
                self.handle_q.task_done()
   
                print(f"packet: {packet}") # TODO  -SEE WHAT IS THIS
                
                if packet == '$' or packet.endswith(("N", "S", "E", "W")):
                    print("Sending Acknowledgement OR Obstacle List to ALG: " + packet) # packet is $ or robot movement
                    self.send_socket(packet)
                    
                #print("ACK Packet",self.send_socket(packet))
            time.sleep(delay)

    def handle(self,packet):
        print(f"[AlgoServer] handle() - putting packet = '{packet}'")
        self.handle_q.put(packet)

    def send_socket(self,message):
        try:
            if(self.c == None):
                print("[ERR][ALGOPC]","Trying to send but no clients connected")
                # self.job_q.put(self.header+":ALG:PC not connected")
            else: 
                self.c.send(message.encode('utf-8'))
        except socket.error as e:
                print(socket.error)
                self.logger.debug(e)
       
# Thread Function
    def thread_receive(self,c,job_q): 
        while True: 
            try:
                data = c.recv(1024)
                data = data.decode('utf-8').strip()
                print(f"[AlgoServer] received data = '{data}'")

                if not data: 
                    print('ALGO PC Said: Bye')
                    self.print_lock.release()    # lock released on exit 
                    break
                if len(data)>0:                   
                    
                        print("[RECV New List from ALG]: " + data)  

                        if (data == 'x'):      # Command to snap a pic, send to IMG Server
                            print("IMG Data" + data)
                            job_q.put(self.header + ":IMG:" + data) 

                            time.sleep(7)

            
                            print(f"Print IR_IMG_RESULT: = {self.db['IR_IMG_RESULT']}")

                            # A5 CHANGES
                            if (self.db["IR_IMG_RESULT"] != ":AND:0" and self.db["IR_IMG_RESULT"] != ":AND:-1"): #VALID IMAGE
                                job_q.put(self.header+ ":ALG:" + 'StopMovement') #Tell ALG to stop sending data and hang the system or send x again?
                                time.sleep(10000000)



                        elif data.startswith('xIMG'):

                            # "xIMG,0" - if there is no obstacle left
                            if len(data) == 6:
                                x, image_id = data[0], data[1:]

                            # "xIMG,0j/k/m/n/w010/s010" - if there is any obstacle left
                            else:
                                x, image_id, movement = data[0], data[1:6], data[6:]
                                job_q.put(f":STM:{movement}")

                            job_q.put(self.header + ":IMG:" + x) 
                            # job_q.put("STM:ALG:$\n") # TODO 


                            print("Before sleep")
                            # wait for camera server to receive the image result
                            time.sleep(3)
                            print("After sleep")
                            
                            print("See self db data:" ,self.db) # Check 

                            self.db["ALGO_IMG_ID"] = image_id
                            print(f"Print IR_IMG_RESULT: = {self.db['IR_IMG_RESULT']}")

                            # A5 CHANGES
                            if (self.db["IR_IMG_RESULT"] != ":AND:0" and self.db["IR_IMG_RESULT"] != ":AND:-1"): #VALID IMAGE
                                job_q.put(self.header+ ":ALG:" + 'StopMovement') #Tell ALG to stop sending data and hang the system or send x again?
                                time.sleep(10000000)

                            # TODO
                            """
                            IMG,1
                            24
                            """
                            img_rec_id_and_result = self.db["ALGO_IMG_ID"] + self.db["IR_IMG_RESULT"] # :AND:IMG,1:AND:24
                            img_rec_id_and_result = img_rec_id_and_result.split(':') # ["AND", "IMG,1", "AND" "24"]
                            img_rec_id_and_result = [part for part in img_rec_id_and_result if part != "AND"] # ["IMG,1", "24"]
                            img_rec_id_and_result = ','.join(img_rec_id_and_result) # IMG,1,24
                            img_rec_id_and_result = img_rec_id_and_result[4:] # 1,24

                            self.db["IMG_REC_ID_AND_RESULT"] = img_rec_id_and_result # 1,24
                            print(f"self.db['ALGO_IMG_ID'] = {self.db['ALGO_IMG_ID']}")
                            print(f"self.db['IMG_REC_ID_AND_RESULT'] = {self.db['IMG_REC_ID_AND_RESULT']}")

                            self.db['concatResult'] = "IMG," + self.db["IMG_REC_ID_AND_RESULT"] # IMG,1,24
                            print(f"Concat ImgResult = {self.db['concatResult']} ")  # Result: "IMG,Int,Int"                            
                            self.job_q.put(f":AND: { self.db['concatResult'] } ") # Send Merged data "IMG,1,24" to AND for live_location
                            
                            #self.job_q.put(f":AND:{self.db['IMG_REC_ID_AND_RESULT']}") #Send merged data to ANDROID for Live location      
                            #self.job_q.put(f":ALG:{self.db['IMG_REC_ID_AND_RESULT']}") #send to Algo
                            # self.job_q.put("STM:ALG:$\n") # TODO 

                            #A5 Logic:
                            # if(self.db["IR_IMG_RESULT"] != 0 or self.db["IR_IMG_RESULT"] != -1): #if not bullseyes or Invalid pic
                            #     self.db['concatResult'] = "IMG," + self.db["IMG_REC_ID_AND_RESULT"] # IMG,1,24
                            #     print(f"Concat ImgResult = {self.db['concatResult']} ")  #Shud show "IMG,1,24"
                                
                            #     self.job_q.put(f":AND: { self.db['concatResult']}") # Send CONCAT data "IMG,1,24" to AND for live_location
                            #     #self.job_`q.put(f":ALG: {self.db['IMG_REC_ID_AND_RESULT']}") # Send to algo e.g. (1,24)
                            
                            # else:
                            #     # Stop MOVEMENT
                            #     print("Stop Car Movement:", job_q.put(self.header + ":STM:" + "\n\n\n\n")) #Just send stop string to stop the robot from moving
                            
                        elif matches := re.findall(r"([w|s|a|d|j|k|n|m]\d{3})", data): 
                            data = matches[0]
                            print("NEW movement data",data)
                            print("Movements Data: " + data)
                            job_q.put(self.header + ":STM:" + data) #send movements data to STM

                        elif data.startswith("ROBOT"): # send android robot data

                            if matches := re.findall(r"([w|s|a|d|j|k|n|m]\d{3})$", data):
                                data = matches[0]
                                live_location, movement = data[:-4], data[-4:]
                                print("AND's Robot Data" + live_location)
                                job_q.put(self.header + ":AND:" + live_location) #send to AND live ROBOT data
                                job_q.put(self.header + ":STM:" + movement) #send to STM movement data
                            else:
                                print("AND's Robot Data" + data)
                                job_q.put(self.header + ":AND:" + data) #send to AND live ROBOT data

                        
            except socket.error as e:
                print(socket.error)
                self.logger.debug(e)
                self.print_lock.release() 
                break
            time.sleep(0.0001)
            
            
        # Close Connection
        c.close() 
      
        


