
import numpy as np
 
from djitellopy import tello
 
import cv2

 
startCounter =0

me = tello.Tello()
 
me.connect()
 
print(me.get_battery())
 
me.streamon()
 
#
 
#cap = cv2.VideoCapture(1)




#hsvVals = [11,164,211,30,255,255]

#hsvVals = [20,87,130,50,255,255]

hsvVals = [0,235,222,179,255,255] #PISTA COMPETENCIA

sensors = 3
 
threshold = 0.2
 
width, height = 480, 360
 
senstivity = 1  # if number is high less sensitive
 
weights = [-45, -15, 0, 15, 25]
 
fSpeed = 18
 
curve = 0
 
def thresholding(img):
 
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
 
    lower = np.array([hsvVals[0], hsvVals[1], hsvVals[2]])
 
    upper = np.array([hsvVals[3], hsvVals[4], hsvVals[5]])
 
    mask = cv2.inRange(hsv, lower, upper)
 
    return mask
 
def getContours(imgThres, img):
 
    cx = 0
 
    contours, hieracrhy = cv2.findContours(imgThres, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
 
    if len(contours) != 0:
 
        biggest = max(contours, key=cv2.contourArea)
 
        x, y, w, h = cv2.boundingRect(biggest)
 
        cx = x + w // 2
 
        cy = y + h // 2
 
        cv2.drawContours(img, biggest, -1, (255, 0, 255), 7)
 
        cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)



    for cnt in contours:
        area = cv2.contourArea(cnt)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
       #x = approx.ravel()[0]
        #y = approx.ravel()[1]

        """  if(area > 400 ):
            
        #cv2.drawContours(img, [approx], 0, (0, 0, 0), 5)
            if 10 < len(approx) < 20:
                #.putText(img, "Circle", (x, y), 1, (0, 0, 0))
                me.land()"""

        """peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
        x , y , w, h = cv2.boundingRect(approx)   
          area = cv2.contourArea(cnt)
        (x,y),radius = cv2.minEnclosingCircle(cnt)
        center = (int(x),int(y))
        radius = int(radius)
        cv2.circle(img,center,radius,(0,255,0),2)
        if(radius > 3000 ):
            me.land()
        """
    

    return cx
 
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
 
        #cv2.imshow(str(x), im)
 
    #print(totalPixels)
 
    return senOut
 
def sendCommands(senOut, cx):
 
    global curve

    ## TRANSLATION

    lr = (cx - width // 2) // senstivity

    lr = int(np.clip(lr, -20, 20))

    if 3 > lr > -3: lr = 0

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

        
 
while True:
 
    #_, img = cap.read()
 
    img = me.get_frame_read().frame
 
    img = cv2.resize(img, (width, height))
 
    img = cv2.flip(img, 0)
 
    imgThres = thresholding(img)
 
    cx = getContours(imgThres, img)  ## For Translation
 
    senOut = getSensorOutput(imgThres, sensors)  ## Rotation
 
    sendCommands(senOut, cx)
 
    cv2.imshow("Output", img)
 
    cv2.imshow("Path", imgThres)
 
    if startCounter == 0:
        me.takeoff()
        #me.move_down(20)
        #while(me.get_height() < 50):
            #   me.send_rc_control(0,0,30,0)
        startCounter = 1



    if cv2.waitKey(1) & 0xFF == ord('q'):

        me.land()
        break
 
# cap.release()
cv2.destroyAllWindows()