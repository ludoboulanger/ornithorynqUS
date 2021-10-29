from math import pi
from math import exp, sqrt, sin, cos, asin, atan
from matplotlib import pyplot as plt

ROTATION_RADIUS = 0.140
MARBLE_MASS = 0.0052
G = 9.810

LAMBDA = 0.01
K = sqrt(MARBLE_MASS * G / ROTATION_RADIUS)
H = sqrt(K**2/MARBLE_MASS - LAMBDA**2 / (4*MARBLE_MASS**2))
J = -LAMBDA/(2*MARBLE_MASS)

FRAME_RATE = 30
TOTAL_FRAMES = 300
TIME = 1 / FRAME_RATE


class Marble:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.initial_theta = asin(sqrt(x**2 + z**2) / ROTATION_RADIUS)
        self.initial_velocity = 0

        self.angular_position = self.initial_theta

        self.angular_velocity = 0

        self.angular_acceleration = 0
    
    def accelerate(self, a, t):
        f = 1 / sqrt(ROTATION_RADIUS / sqrt(G**2 / a**2))

        max_theta = atan(a / G)
        
        accel = max_theta*sin(f*t)

        max_time = pi/(2*f)

        theta = accel if t < max_time else max_theta

        self.angular_position = theta

    def oscillate(self, t, accel=0, accel_angle=0):

        if accel == 0:

            if t == 0:
                self.initial_theta =  self.angular_position

            self.angular_position = exp(J*t)*(self.initial_theta*cos(H*t) + self.initial_velocity*sin(H*t))

        else:
            self.accelerate(accel, t)

        # Get Cartesian Coordinates    
        linear_displacement = ROTATION_RADIUS*sin(self.angular_position)    
        self.x = linear_displacement*cos(accel_angle)
        self.z = linear_displacement*sin(accel_angle)


if __name__ == "__main__":

    marble = Marble(0, 0, 0)
    accel_car = 1.3
    thetas = []
    relative_time = 0

    for i in range(TOTAL_FRAMES):

        marble.oscillate(relative_time, accel=accel_car)

        relative_time += TIME

        if i == FRAME_RATE:
            relative_time = 0
            accel_car = 0

        thetas.append(marble.angular_position)


    plt.figure()
    plt.plot(thetas)
    plt.title("Angular Position")
    plt.show()