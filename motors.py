import RPi.GPIO as gpio
import time
import pygame
from pygame.locals import *
import subprocess

screen = 0
font = 0

left_front = 17
left_back = 22
right_front = 23
right_back = 24
speaker = 4
speaker_pwm = 0

ena = 15
enb = 18
ena_pwm = 0
enb_pwm = 0
power_percent = 50

moveSpeak = True

def init():
    global ena_pwm
    global enb_pwm
    global speaker_pwm
    global screen
    global font
   
    pygame.init()
    screen = pygame.display.set_mode([300, 300])

    pygame.font.init()
    font = pygame.font.SysFont("Calibri", 30)

    gpio.setmode(gpio.BCM)
    gpio.setup(left_front, gpio.OUT)
    gpio.setup(left_back, gpio.OUT)
    gpio.setup(right_front, gpio.OUT)
    gpio.setup(right_back, gpio.OUT)
    gpio.setup(speaker, gpio.OUT)
    gpio.setup(ena, gpio.OUT)
    gpio.setup(enb, gpio.OUT)
    
    ena_pwm = gpio.PWM(ena, 100)
    enb_pwm = gpio.PWM(enb, 100)
    speaker_pwm = gpio.PWM(speaker, 100)

    ena_pwm.start(0)
    enb_pwm.start(0)
    speaker_pwm.start(0)

    stopAll()

def move(left, right):

    global power_percent

    if left > 0:
        gpio.output(left_back, gpio.LOW)
        gpio.output(left_front, gpio.HIGH)
    else:
        gpio.output(left_back, gpio.HIGH)
        gpio.output(left_front, gpio.LOW)

    if right > 0:
        gpio.output(right_front, gpio.HIGH)
        gpio.output(right_back, gpio.LOW)
    else:
        gpio.output(right_front, gpio.LOW)
        gpio.output(right_back, gpio.HIGH)

    ena_pwm.ChangeDutyCycle(abs(left)*power_percent)
    enb_pwm.ChangeDutyCycle(abs(right)*power_percent)

def stopAll():

    global ena_pwm
    global enb_pwm

    ena_pwm.ChangeDutyCycle(0)
    enb_pwm.ChangeDutyCycle(0)

    gpio.output(left_front, gpio.LOW)
    gpio.output(left_back, gpio.LOW)
    gpio.output(right_front, gpio.LOW)
    gpio.output(right_back, gpio.LOW)

def loop():
    global screen
    global power_percent
    global font
    global speaker_pwm
    global moveSpeak

    clock = pygame.time.Clock()

    try:
        while True:
            clock.tick(60)
            keyStatus = pygame.key.get_pressed()
           
            leftPower = 0
            rightPower = 0
            horn = False

            if keyStatus[K_UP]:
                
                leftPower = 1
                rightPower = 1
                
                if (keyStatus[K_RIGHT]):
                    rightPower = 0.4
                if (keyStatus[K_LEFT]):
                    leftPower = 0.4

            elif keyStatus[K_DOWN]:
                
                leftPower = -1
                rightPower = -1

                if (keyStatus[K_RIGHT]):
                    rightPower = -0.4
                if (keyStatus[K_LEFT]):
                    leftPower = -0.4
            
            elif keyStatus[K_LEFT]:
                leftPower = -1
                rightPower = 1

            elif keyStatus[K_RIGHT]:
                leftPower = 1
                rightPower = -1

            elif keyStatus[K_h]:
                horn = True

            move(leftPower, rightPower)

            if moveSpeak:
                speaker_pwm.ChangeDutyCycle(100)   
                moveSpeak = False
            else:
                speaker_pwm.ChangeDutyCycle(0)
                moveSpeak = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == K_s:
                        stopAll()
                    elif event.key == K_q:
                        pygame.quit()
                    elif event.key == K_KP_PLUS:
                        power_percent += 5
                        if (power_percent > 100):
                            power_percent = 100
                    elif event.key == K_KP_MINUS:
                        power_percent -= 5
                        if (power_percent < 0):
                            power_percent = 0
                    elif event.key == K_w: 
                        wifi_status = subprocess.getoutput("iwconfig wlan0 | grep -i --color signal")
                        print(wifi_status)
            screen.fill((0, 0, 0))
            powerText = font.render("Power: " + str(power_percent) + "%", False, (255, 255, 255))
            screen.blit(powerText, (10, 10))
            pygame.display.flip()

    finally:
        ena_pwm.stop()
        enb_pwm.stop()
        pygame.quit()
        gpio.cleanup()

init()
loop()
