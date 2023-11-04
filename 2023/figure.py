import cv2
import numpy as np
import djitellopy as tello


width = 640
height = 480

cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)


centro=20
global imgContour

def empty(a):
    pass

cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,240)
cv2.createTrackbar("HUE Min","HSV",23,179,empty)
cv2.createTrackbar("HUE Max","HSV",60,179,empty)
cv2.createTrackbar("SAT Min","HSV",108,255,empty)
cv2.createTrackbar("SAT Max","HSV",190,255,empty)
cv2.createTrackbar("VALUE Min","HSV",31,255,empty)
cv2.createTrackbar("VALUE Max","HSV",174,255,empty)

cv2.namedWindow("Parameters")
cv2.resizeWindow("Parameters",640,240)
cv2.createTrackbar("Threshold1","Parameters",80,255,empty)
cv2.createTrackbar("Threshold2","Parameters",171,255,empty)
cv2.createTrackbar("Area 1","Parameters",250,30000,empty)
cv2.createTrackbar("Area 2","Parameters",250,30000,empty)


frameWidth = width
frameHeight = height

def stackImages(scale,imgArray):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                else:
                    imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
        ver = np.vstack(hor)
    else:
        for x in range(0, rows):
            if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            else:
                imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        ver = hor
    return ver


n = 0
init = 0
areas = np.zeros((10,))

def getContours(img,imgContour):
    global dir
    contours, hierarchy = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    gate =  0
    maxima = 0
    global n, init, areas

    for cnt in contours:

        area = cv2.contourArea(cnt)
        areaMin = cv2.getTrackbarPos("Area 1", "Parameters")

        #cv2.drawContours(imgContour, cnt, -1, (255, 0, 255),3)
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)


            
        if len(approx) == 3:
                    # Dibujar un contorno amarillo alrededor del triángulo
            cv2.drawContours(imgContour, cnt, -1, (0, 255, 255), 2)

            # Mostrar el tipo de figura en el frame
            cv2.putText(imgContour, "Triangulo", tuple(approx[0][0]),cv2.FONT_HERSHEY_COMPLEX, .5,
                            (255, 0, 0),2)
        if len(approx) == 6:
                    # Dibujar un contorno amarillo alrededor del triángulo
            cv2.drawContours(imgContour, cnt, -1, (0, 255, 255), 2)

            # Mostrar el tipo de figura en el frame
            cv2.putText(imgContour, "Hexagono", tuple(approx[0][0]),cv2.FONT_HERSHEY_COMPLEX, .5,
                            (255, 0, 0),2)
            
        if area >= areaMin:
                    
            # Si el contorno tiene 4 vértices, es un romboide
            if len(approx) == 4:
                # Dibujar un contorno amarillo alrededor del romboide
                cv2.drawContours(imgContour, cnt, -1, (0, 255, 255), 2)

                cv2.putText(imgContour, "Hexagono", tuple(approx[0][0]),cv2.FONT_HERSHEY_COMPLEX, .5,
                    (255, 0, 0),2)   
                
                
        n = 0
        areas[n] = area
        gate = gate+1
   

def display(img):
    cv2.line(img,(int(frameWidth/2)-centro,0),(int(frameWidth/2)-centro,frameHeight),(255,255,0),3)
    cv2.line(img,(int(frameWidth/2)+centro,0),(int(frameWidth/2)+centro,frameHeight),(255,255,0),3)

    cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),5,(0,0,255),5)
    cv2.line(img, (0,int(frameHeight / 2) - centro), (frameWidth,int(frameHeight / 2) - centro), (255, 255, 0), 3)
    cv2.line(img, (0, int(frameHeight / 2) + centro), (frameWidth, int(frameHeight / 2) + centro), (255, 255, 0), 3)



while True:

   
    _, img = cap.read()
    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    imgContour = img.copy()
    imgHsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    h_min = cv2.getTrackbarPos("HUE Min","HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")
    #print(h_min)

    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])
    mask = cv2.inRange(imgHsv,lower,upper)
    result = cv2.bitwise_and(img,img, mask = mask)
    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

    imgBlur = cv2.GaussianBlur(result, (7, 7), 1)
    imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)

    threshold1 = cv2.getTrackbarPos("Threshold1", "Parameters")
    threshold2 = cv2.getTrackbarPos("Threshold2", "Parameters")
    imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
    kernel = np.ones((4, 4))
    imgDil = cv2.dilate(imgCanny, kernel, iterations=1)
    getContours(imgDil, imgContour)
    #display(imgContour)

    stack = stackImages(0.7,([img,result],[imgDil,imgContour]))

    cv2.imshow('Horizontal Stacking', stack)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()


