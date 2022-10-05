import logging
import struct
import os
class PacketHandler:
    
    handlers = {}

    def __init__(self):      
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def measure_temp(self):
        temp = os.popen("vcgencmd measure_temp").readline()
        return (temp.replace("temp=",""))

    def registerHandler(self,instance):
        unique_id = instance.getPacketHeader()
        if unique_id not in self.handlers:
            self.handlers[unique_id] = instance
        else:
            print("Failed to register handler, please choose another unique_id")

    def unregisterHandler(self,unique_id):
        try:
            del self.handlers[unique_id]
        except KeyError:
            print("Fail to remove, handler not found.")


    def convertToName(self,header):
        if header == 'STM':
                return "RC-Car"
        elif header == 'AND':
                return "ANDROID"
        elif header == 'ALG':
                return "ALGORITHM PC"
        elif header == 'IMG':
                return "PI-CAMERA"
        elif header == 'CPC':
                return "CAMERA-PC"
            
    def handle(self,packet):
        """
        :AND:IMG,1,24

        """
        # TODO - packet = ":AND:1,-1"
        splitData = packet.split(':') # ["", AND, "1,-1"]
        if len(splitData)>1:
            recv_from = splitData[0] # ""
            unique_id = splitData[1] # "AND"
            data = splitData[2] # "1,-1"

            print(f"recv_from={recv_from} | unique_id={unique_id} | data={data}")
                       
            if unique_id in self.handlers:
                if not packet.startswith("P:A:set:startposition"):
                    print(f"[PacketHandler] packet = {packet}")
                    # lo = (self.db["IMG_REC_ID_AND_RESULT"]"["+self.measure_temp().strip()+"][MSG]["+self.convertToName(recv_from)+"->"+self.convertToName(unique_id)+"]:",data)
                self.handlers[unique_id].handle(data+"\n")
        else:
            print("[ERR][PACKETHANDLER]:",packet)
            self.logger.debug("UnknownPacketDestination " + packet)
          
