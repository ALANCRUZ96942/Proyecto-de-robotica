
from djitellopy import Tello
import cv2
import time
 
######################################################################
width = 320  # WIDTH OF THE IMAGE
height = 240  # HEIGHT OF THE IMAGE
startCounter =0   #  0 FOR FIGHT 1 FOR TESTING
######################################################################
 
# CONNECT TO TELLO
me = Tello()
me.connect()
me.for_back_velocity = 0
me.left_right_velocity = 0
me.up_down_velocity = 0
me.yaw_velocity = 0

me.speed = 0
 
print(me.get_battery())
 

print(me.get_battery())
 
me.streamoff()
me.streamon()



while True:

    # GET THE IMAGE FROM TELLO
    frame_read = me.get_frame_read()
    myFrame = frame_read.frame
    img = cv2.resize(myFrame, (width, height))
    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    if startCounter == 0:
        me.takeoff()
        startCounter = 1



    me.send_rc_control(0,0,0,30)
    time.sleep(10)


    cv2.imshow('Horizontal Stacking', img)
 
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break
 
# cap.release()
cv2.destroyAllWindows()