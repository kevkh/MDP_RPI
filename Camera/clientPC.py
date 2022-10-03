import io
import socket
import struct
from PIL import Image
import time

# IMG Client Server
cs = socket.socket()
cs.connect(('192.168.33.1', 5001))  #connect to RPI
print('Connected to RPi!')
connection = cs.makefile('rb')


try:
    img = None
    while True:
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            continue
        print("write scan" + "\n")
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        image_stream.seek(0)
            
        image = Image.open(image_stream)
        image.save('../fromrpi.jpg') #store in img in rpi folder  #Captured from RPI CAM
        print('Image resolution is %d x %d' % image.size)
        image.verify()
        print('Verified!')
       
        # Your detect.py functions goes here, within the comments

        #cs.sendall(':AND:Picture'.encode()) # Send to Android
        cs.sendall('Picture'.encode()) # Tis img data is to be sent to IMG Processing(Ans)
        # I tink its to send img data over to Android (as a Reply)
finally:
    connection.close()
    cs.close()