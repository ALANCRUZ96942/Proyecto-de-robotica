from time import sleep
from djitellopy import tello
from time import sleep

import cv2



dron  = tello.Tello()
dron.connect()
print(dron.get_battery())
dron.streamon()


while True: 
    img = dron.get_frame_read().frame
    #img = cv2.resize(img, (360,240))
    cv2.imshow("Imagenes de dron", img)
    cv2.waitKey(1)




