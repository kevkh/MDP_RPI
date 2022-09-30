from picamera import PiCamera
import time


camera = PiCamera()
camera.resolution = (640, 480)
camera.vflip = True
camera.hflip = True



#camera.start_preview()

# colorbalance, blur,  
camera.image_effect = 'colorbalance'

camera.contrast = 25
camera.brightness = 60

camera.start_preview()

#time.sleep(2)

camera.start_recording("./num6/num6_L.h264")
time.sleep(20)
camera.stop_recording
exit()




