import pygame
import math


RADSTAND = 55
MAX_ACCELERATION = 10
MAX_STEERING_ANGLE = math.radians(30)
MAX_STEERING_OVER_TIME = math.radians(50)
MASS = 1200


class Car :
    def __init__(self):
        self.position = pygame.Vector2(400, 300)
        self.velocity = 0
        self.yaw = 0
        self.steering_angle = 0 # Delta Winkel


    def update(self, dt, steering_input, throttle_input):

        temp_steering_angle  = steering_input * MAX_STEERING_OVER_TIME
        self.steering_angle = self.steering_angle + temp_steering_angle * dt
        self.steering_angle = max(-MAX_STEERING_ANGLE, min(self.steering_angle, MAX_STEERING_ANGLE))

        acceleration = throttle_input * MAX_ACCELERATION
        self.velocity = self.velocity + acceleration * dt

        temp_yaw = self.velocity / RADSTAND * math.tan(self.steering_angle)
        self.yaw = self.yaw + temp_yaw * dt

        self.position.x += self.velocity * math.cos(self.yaw) * dt
        self.position.y += self.velocity * math.sin(self.yaw) * dt

        print(f"Position: [ x: {self.position.x}, y: {self.position.y}] \n Velocity: [ v: {self.velocity} ] \n Steering Angle: [ steering_angle: {self.steering_angle} ]")




