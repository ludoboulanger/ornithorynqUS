import bpy
from bpy import context

from math import pi
from math import exp, sqrt, sin, cos, asin, atan

ROTATION_RADIUS = 140
MARBLE_MASS = 0.0052
G = 9810

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

        self.initial_theta = asin(sqrt(x**2 + y**2) / ROTATION_RADIUS)
        self.initial_velocity = 0

        self.angular_position = self.initial_theta

        self.angular_velocity = 0

        self.angular_acceleration = 0
        
    def get_position(self):
        return (self.x, self.y, self.z)
    
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
                self.initial_theta = self.angular_position

            self.angular_position = exp(J*t)*(self.initial_theta*cos(H*t) + self.initial_velocity*sin(H*t))

        else:
            self.accelerate(accel, t)
            
        # Get Cartesian Coordinates    
        linear_displacement = ROTATION_RADIUS*sin(self.angular_position)    
        self.x = linear_displacement*cos(accel_angle)
        # self.y = linear_displacement*sin(accel_angle)

# Objects
marble_object = bpy.context.scene.objects["Marble"]
bpy.context.scene.objects["Marble"].select_set(True)

# Movements
frames = range(TOTAL_FRAMES)

# Animation
marble_object.animation_data_clear()
current_time = 0

marble = Marble(0, 0, 5)
accel_car = 1340
relative_time = 0

for f in frames:
    
    # Calculate next position
    marble.oscillate(relative_time, accel=accel_car)
    
    # Set current frame
    context.scene.frame_set(f)
    
    # Get marble position
    marble_object.location = marble.get_position()
    print("FRAME :: ", f)
    print("MARBLE POSITION :: ", marble.get_position())
    print("MARBLE OBJECT LOCATION :: ", marble_object.location)
    
    # Insert keyframe
    bpy.ops.anim.keyframe_insert(type="LocRotScale")

    # Update Time
    relative_time += TIME
    
#    if f == FRAME_RATE:
#        accel_car = 0
#        relative_time = 0
    
bpy.ops.screen.animation_play()