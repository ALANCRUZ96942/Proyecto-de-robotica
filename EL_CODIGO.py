from djitellopy import tello
import numpy as np
from pandas import read_csv
from time import time
import cv2

# Variables de control
distLejana = 280 # 160 a 900 con saltos de 20
centroY = 95
alturaExtra = 100
distanciaExtra = 100
radioSeguro = 0.25 # Area segura de 50%
tiempoEspera = 1.5

# Leer base de datos de la relación distancia por anchura
df = read_csv("relacionAnchuraDistancia.csv")

posDistLejana = None

contador = 0
for distancia in df["Distancia"]:
    if distancia == distLejana:
        posDistLejana = contador
        break
    else:
        contador += 1

anchoReal, altoReal = 120, 120
ancho_imagen, alto_imagen = 480, 360
centroX = ancho_imagen // 2
centro = [centroX, centroY]

# [hue_min, saturation_min, val_min, hue_max, saturation_max, val_max]
HSV_vals = [0,70,15,17,255,255] # [0,183,149,179,255,255]

# DRONE
elDrone = tello.Tello()
elDrone.connect()   # Conexión
elDrone.streamon()  # Transmisión de video
elDrone.takeoff()   # Despegue
elDrone.move_up(int(alturaExtra))

def temporizador(segundos):
    inicio = time()
    tiempo = 0
    while tiempo < segundos:
        actual = time()
        tiempo = actual - inicio

def umbralizacion(imagen):
    # Se crea una imagen tipo HSV a partir de la imagen
    imagen_HSV = cv2.cvtColor(imagen, cv2.COLOR_BGR2HSV)
    # Se crea un array con los valores mínimos de detección del HSV
    minimos = np.array(HSV_vals[:3])
    # Se crea un array con los valores máximos de detección del HSV
    maximos = np.array(HSV_vals[3:])
    # Segenera una mascara con la deteccion del color
    mascara = cv2.inRange(imagen_HSV, minimos, maximos)
    return mascara

def obtenerInfoPuerta(img_Mask, imagenOriginal, dibujar = False):
    width, height, cx, cy = None, None, None, None
    # Se obtienen los contornos
    contornos, jerarquia = cv2.findContours(img_Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # Si se encuentra algún contorno
    if len(contornos) != 0:
        # Se obtiene el contorno más grande
        mayor = max(contornos, key=cv2.contourArea)
        # (x, y) coordenadas de la esquina superior izquierda
        piX, piY, width, height = cv2.boundingRect(mayor)
        # Se obtienen los valores centrales de la puerta
        cx = piX + width // 2
        cy = piY + height // 2
        # Se dibuja el contorno de la puerta
        if dibujar == True:
            # Dibujar contorno y su centro
            cv2.drawContours(imagenOriginal, mayor, -1, (255, 0, 255), 7)
            cv2.circle(imagenOriginal, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
            cv2.circle(imagenOriginal, centro, 5, (0, 0, 255), cv2.FILLED)
    else:
        print("No se detectó puerta")
    return width, height, cx, cy

def obtenImagen():
    # Obtiene captura de imagen
    captura = elDrone.get_frame_read().frame
    #captura = cv2.imread('Puertas.jpg')
    # Cambia el tamaño de la imagen
    captura = cv2.resize(captura, (ancho_imagen, alto_imagen))
    # print("Las dimensiones son: ", captura.shape)
    return captura

puertasT = 4
puertasA = 0

while True:
    # Espera para estabilizarse
    temporizador(tiempoEspera)
    # Obtiene la imagen y detecta la puerta
    captura = obtenImagen()
    mascara = umbralizacion(captura)
    ancho, alto, cX, cY = obtenerInfoPuerta(mascara, captura, dibujar=True)
    # Si en altura está dentro del área segura
    if (centroY >= (cY - (alto * radioSeguro))) and (centroY <= (cY + (alto * radioSeguro))):
        # Si en el eje X está dentro del área segura
        if (centroX >= (cX - (ancho * radioSeguro))) and (centroX <= (cX + (ancho * radioSeguro))):
            # Si está muy lejos (9 metros) avanza el máximo de metros posibles
            if (ancho < df["Anchura"].iloc[-1]):
                elDrone.move_forward(500)
            elif (ancho <= df["Anchura"][posDistLejana]): # Si está a una distancia delimitada por nosotros o más lejos
                faltanteA = 100
                contador = 0
                for anchura in df["Anchura"]:
                    if ancho >= anchura:
                        faltanteA = df["Distancia"][contador] - (distLejana - 40)
                        if faltanteA > 500:
                            faltanteA = 500
                        break
                    contador += 1
                # Se mueve para llegar a distLejana - 40
                elDrone.move_forward(int(abs(faltanteA)))
            else:
                faltanteA = 100
                contador = 0
                for anchura in df["Anchura"]:
                    if ancho >= anchura:
                        faltanteA = df["Distancia"][contador] + distanciaExtra
                        if faltanteA > 500:
                            faltanteA = 500
                        break
                    contador += 1
                # Se mueve para atravesar la puerta
                elDrone.move_forward(int(abs(faltanteA)))
                # Se ha atravezado una puerta :D
                puertasA += 1
                # Si ya se han atravesado todas las puertas
                if puertasA >= puertasT:
                    # Aterriza y se acaba el ciclo
                    elDrone.land()
                    elDrone.streamoff
                    break
                else:
                    # Espera para estabilizarse
                    temporizador(tiempoEspera)
                    # Gira hacia la derecha
                    elDrone.rotate_clockwise(90)
        else:
            # Calcular distancia faltante en X en píxeles
            faltanteXP = cX - centroX
            # Calcular distancia faltante en X en cm
            faltanteXR = int((faltanteXP / ancho) * anchoReal)
            if faltanteXP < 0:
                elDrone.move_left(int(abs(faltanteXR)))
            else:
                elDrone.move_right(int(abs(faltanteXR)))
    else:
        # Calcular distancia faltante en Y en píxeles
        faltanteYP = cY - centroY
        # Calcular distancia faltante en Y en cm
        faltanteYR = int((faltanteYP / alto) * altoReal)
        if faltanteYP < 0:
            elDrone.move_up(int(abs(faltanteYR)))
        else:
            elDrone.move_down(int(abs(faltanteYR)))
    cv2.imshow("Puerta", captura)
    cv2.waitKey(1)