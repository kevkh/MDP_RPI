from picamera import PiCamera
from time import sleep


camera = PiCamera()
camera.resolution = (640, 480)
camera.vflip = True
camera.hflip = True



camera.start_preview()

for i in range(4):
	camera.capture("./num7/num7-%d.jpg"%i);
	sleep(0.25)


camera.stop_preview()
	#exit()
