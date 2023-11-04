from time import sleep
from djitellopy import Tello
import math
import numpy as np

#creating the drone object
tello = Tello()

tello.connect()
print(tello.get_battery())

tello.takeoff()
#creating the traslation and rotation matrix 

#first movement matrix:

#rotate 45° and move to 10, 5 coordinate
psi = math.radians(45)
x = 10
y = 5
z = 0
matrix_movement1 = [[math.cos(psi), -math.sin(psi),0, x], 
          [math.sin(psi), math.cos(psi),0, y], 
           [0, 0,1, z],
           [0, 0,0, 1],
           ]


#rotate 45° and move to 10, 5 coordinate
psi = math.radians(45)
x = 10
y = 5
z = 0
matrix_movement1 = [[math.cos(psi), -math.sin(psi),0, x], 
          [math.sin(psi), math.cos(psi),0, y], 
           [0, 0,1, z],
           [0, 0,0, 1],
           ]

#rotate 45° and move to 12 on y
psi2 = math.radians(45)
x2 = 0
y2 = 12
z2 = 0
matrix_movement2 = [[math.cos(psi2), -math.sin(psi2),0, x2], 
          [math.sin(psi2), math.cos(psi2),0, y2], 
           [0, 0,1, z2],
           [0, 0,0, 1],
           ]           


final_matrix = 	np.dot(matrix_movement1, matrix_movement2)

#we pass the trajectory to the drone

tello.rotate_clockwise(psi)
tello.move_forward(final_matrix[0][4])
tello.move_left(final_matrix[1][4])


#land the drone
tello.land()