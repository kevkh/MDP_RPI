import socket
import time
from imutils.video import VideoStream
import imagezmq

sender = imagezmq.ImageSender(connect_to='tcp://192.168.33.15:5555') 
#"192.168.33.1", 5000)
  
rpi_name = socket.gethostname() # send RPi hostname with each image
picam = VideoStream(usePiCamera=True).start()

time.sleep(2.0)  # allow camera sensor to warm up

#while True:  # send images as stream until Ctrl-C
image = picam.read()
print('sending image')
reply = sender.send_image(rpi_name, image)
print(reply)
