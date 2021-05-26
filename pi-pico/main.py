from machine import Pin, Timer

def check_sensor(timer):
    global sensor
    if sensor.value() == 1:
        gp1.value(1)
        gp25.value(1)
        print("Motion detected")
    else:
        gp1.value(0)
        gp25.value(0)
        print("Waiting for motion")

gp4 = Pin(4,Pin.OUT)
gp4.value(1)
gp1 = Pin(1,Pin.OUT)
gp25 = Pin(25,Pin.OUT)
sensor = Pin(16,Pin.IN)
tim = Timer()
tim.init(freq=1.5, mode=Timer.PERIODIC, callback=check_sensor)
