import numpy as np
from djitellopy import tello
import cv2
import math
from time import sleep

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()

#cap = cv2.VideoCapture(2)
#hsvVals = [0,162,55,11,255,255] prueba baño
#hsvVals = [0,210,60,16,255,255] prueba pasillo fail
#hsvVals = [0,153,148,24,255,255] #prueba pasillo nueva calibracion
#hsvVals = [0,138,114,24,255,255]
#hsvVals = [0,201,198,89,255,255]
hsvVals = [0,235,222,179,255,255] #PISTA COMPETENCIA
sensors = 3
threshold = 0.03 #0.01 #prueba buena con 0.05
width, height = 360, 240

sensitivity = 3  # if number is high less sensitive
weights = [-35, -25, 0, 25, 35]
fSpeed = 20
curve = 0
flag = 0

getSensors = 0

state = 0
counter = 0

def thresholding(img):

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])
    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])
    mask = cv2.inRange(hsv, lower, upper)

    return mask

def getContours(imgThres, img):

    global getSensors, state, counter

    cx = 0
    cy = 0

    contours, hier = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    circles = []

    if len(contours) != 0:
        biggest = max(contours, key=cv2.contourArea)
        contour = biggest
        #CHECK FOR CIRCLES
        perim = cv2.arcLength(contour,True)
        approx = cv2.approxPolyDP(contour,0.028*perim,True)
        area = cv2.contourArea(contour)

        if ((len(approx) >= 8) & (area > 3000) ): #2800
            if counter == 0:
                circles.append(contour)
                cv2.drawContours(img, contour,  -1, (255,0,0), 2)
                M = cv2.moments(contour)
                ccx = int(M["m10"] / M["m00"])
                ccy = int(M["m01"] / M["m00"])
                radius = int(math.sqrt(area / 3.14159))
                cv2.circle(img, (ccx, ccy), radius, (0, 255, 255) , 2)
                cv2.circle(img, (ccx, ccy), 5, (0, 0, 255), -1)
                print(f'CIRCLE AREA: {area}')
                if state == 2:
                    state = 3 
                elif state == 4:
                    state = 5
                elif state == 5:
                    state = 6
                
                counter = 1
            elif counter == 2:
                counter = 3
            elif counter == 3:
                print(f'AREA: {area}')
                state = 7
        else:
            x, y, w, h = cv2.boundingRect(biggest)
            cx = x + w // 2
            cy = y + h // 2
            cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
            cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)

            if counter == 1:
                counter = 2
            
            if state == 1: #DRON DESPEGADO
                state = 2  #AVANZA
            elif state == 3:
                state = 4

    if len(contours) != 0: #use camera input to command the drone
        getSensors = 0
    elif len(contours) == 0:
        getSensors = 1

    return cx, cy, getSensors, state

def getSensorOutput(imgThres, sensors):

    imgs = np.hsplit(imgThres, sensors)
    totalPixels = (img.shape[1] // sensors) * img.shape[0]
    senOut = []

    for x, im in enumerate(imgs):
        pixelCount = cv2.countNonZero(im)
        if pixelCount > threshold * totalPixels:
            senOut.append(1)
        else:
            senOut.append(0)
        #cv2.imshow(str(x), im) #shows each sensor

    return senOut

def sendCommands(senOut, cx):

    global curve

    ## TRANSLATION

    lr = int((cx - width / 2) / sensitivity)
    lr = int(np.clip(lr, -18, 18)) #original -10 10
    if 3 > lr > -3: lr = 0 #original 5 -5

    #print(f'senOUT: {senOut}')

    ## Rotation

    if   senOut == [1, 0, 0]: curve = weights[0]
    elif senOut == [1, 1, 0]: curve = weights[1]
    elif senOut == [0, 1, 0]: curve = weights[2]
    elif senOut == [0, 1, 1]: curve = weights[3]
    elif senOut == [0, 0, 1]: curve = weights[4]

    elif senOut == [0, 0, 0]: curve = weights[2]
    elif senOut == [1, 1, 1]: curve = weights[2]
    elif senOut == [1, 0, 1]: curve = weights[2]

    me.send_rc_control(lr, fSpeed, 0, curve)

def to():
    global state
    me.takeoff()
    #me.move_down(15)
    me.send_rc_control(0,20,0,0)     #antes 25, 30
    sleep(3.5)
    state = 1

while True:

    #_, img = cap.read()

    img = me.get_frame_read().frame
    img = cv2.resize(img, (width, height))
    #imgcrop = img[70:height, 0:width]
    imgcrop = img
    #img = cv2.flip(img, 0)
    imgThres = thresholding(imgcrop)


    if state == 0:
        to()
    elif (state != 0 and state != 6):
        cx, cy, getSensors, state = getContours(imgThres, imgcrop)  ## For Translation

        if state == 7:
            sleep(0.25)
            me.send_rc_control(-3,25,0,0) #AGREGUÉ IRSE A LA IZQUIERDA
            #sleep(2.5)
            print("RIP")
            break

        if getSensors == 0:
            senOut = getSensorOutput(imgThres, sensors)  ## Rotation
            sendCommands(senOut, cx)
        elif getSensors == 1:
            me.send_rc_control(0,0,0,0)
            me.rotate_counter_clockwise(45)

    cv2.imshow("Output", imgcrop)
    cv2.imshow("Path", imgThres)

    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break


#cap.release()
me.land()
me.streamoff()
cv2.destroyAllWindows()