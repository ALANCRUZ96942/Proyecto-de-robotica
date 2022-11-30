from time import sleep
from djitellopy import Tello


tello = Tello()

tello.connect()
print(tello.get_battery())

tello.takeoff()
tello.send_rc_control(0,0,30,0)
sleep(3)
tello.send_rc_control(10,0,0,0)
sleep(3)
tello.send_rc_control(0,0,0,10)
sleep(3)
tello.land()