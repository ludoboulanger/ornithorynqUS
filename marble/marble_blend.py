import bpy
from bpy import context

from math import pi
from math import exp, sqrt, sin, cos, asin, atan

ROTATION_RADIUS = 140
CONTAINER_HEIGHT = 8.5 # 10mm - 1.5mm concavity
MARBLE_MASS = 0.0052
G = 9810

LAMBDA = 0.01
K = sqrt(MARBLE_MASS * G / ROTATION_RADIUS)
H = sqrt(K**2/MARBLE_MASS - LAMBDA**2 / (4*MARBLE_MASS**2))
J = -LAMBDA/(2*MARBLE_MASS)

FRAME_RATE = 30
TOTAL_FRAMES = 120
TIME = 1 / FRAME_RATE

class Container:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

        self.v_x = 0
        self.v_z = 0

        self.a_x = 0
        self.a_z = 0

    def get_cartesien_position(self):
        return (self.x, self.y, self.z)

    """
    direction = ["x", "z"]
    """
    def rectilinear_move(self, a, t, axis="x"):
        if axis == "x":
            self.v_x += a*t
            self.x += self.v_x*t + 0.5*a*t**2
        elif axis == "z":
            self.v_z += a*t
            self.z += self.v_z*t + 0.5*a*t**2


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
        
    def get_cartesien_position(self):
        return (self.x, self.y, self.z)
    
    def update_cartesian_position(self, angle):
        # Calculate linear displacement
        linear_displacement = ROTATION_RADIUS*sin(self.angular_position)
            
        self.x = linear_displacement*cos(angle)
        self.y = linear_displacement*sin(angle)
        
        # self.z = CONTAINER_HEIGHT + ROTATION_RADIUS*(1 - cos(self.angular_position))
        
    
    def accelerate(self, a, t):
        f = 1 / sqrt(ROTATION_RADIUS / sqrt(G**2 + a**2))

        max_theta = atan(a / G)
        print("MAX THETA :: ", max_theta)
        accel = max_theta*sin(f*t)

        max_time = pi/(2*f)
        print("MAX_TIME :: ", max_time)

        theta = accel # if t < max_time else max_theta

        self.angular_position = theta

    def oscillate(self, t, accel=0, accel_angle=0):

        if accel == 0:

            if t == 0:
                self.initial_theta = self.angular_position

            self.angular_position = \
                exp(J*t)*(self.initial_theta*cos(H*t) + \
                self.initial_velocity*sin(H*t))

        else:
            self.accelerate(accel, t)
            
        # Get Cartesian Coordinates    
        self.update_cartesian_position(accel_angle)

# Objects
marble_object = bpy.context.scene.objects["Marble"]
container_object = bpy.context.scene.objects["Container"]

def sim_all():
    # Instantiate Animation Data
    container = Container(0, 0, 5)
    marble = Marble(0, 0, 15)
    
    # Inital params
    accel_car = 800
    relative_time = 0
    
    # Clear previous animation data
    marble_object.animation_data_clear()
    container_object.animation_data_clear()
    
    # Set frames
    frames = range(TOTAL_FRAMES)
    
    for f in frames:
        
        # Calculate next position
        container.rectilinear_move(accel_car, TIME, axis="x")
        marble.oscillate(relative_time, accel=-accel_car, accel_angle=0)
        
        # Set current frame
        context.scene.frame_set(f)
        
        # Get marble position
        marble_object.location = marble.get_cartesien_position()
        container_object.location = container.get_cartesien_position()
        # Insert keyframe
        marble_object.keyframe_insert(data_path="location", frame=f)
        container_object.keyframe_insert(data_path="location", frame=f)

        # Update Time
        relative_time += TIME
        
        if f == FRAME_RATE/2:
            accel_car = 0
            container.v_x = 0
            relative_time = 0


def sim_marble():
    # Instantiate a marble
    marble = Marble(0, 0, 15)
    
    # Initial params
    accel_car = 800
    relative_time = 0
    
    # Clear previous data
    marble_object.animation_data_clear()
    
    # Set frames
    frames = range(TOTAL_FRAMES)
    
    # Clear previous data
    marble_object.animation_data_clear()
    
    for f in frames:
        
        # Calculate next position
        marble.oscillate(relative_time, accel=accel_car, accel_angle=0)
        
        # Set current frame
        context.scene.frame_set(f)
        
        # Get marble position
        marble_object.location = marble.get_cartesien_position()
        
        # Insert keyframe
        marble_object.keyframe_insert(data_path="location", frame=f)

        # Update Time
        relative_time += TIME
        
        if f == FRAME_RATE:
            accel_car = 0
            relative_time = 0
 
            
def sim_container():
    # Instantiate a container
    container = Container(0, 0, 5)
    
    # Initial params
    accel_car = 800
    relative_time = 0
    
    # Set frames
    frames = range(TOTAL_FRAMES)
    
    # Clear Previous data
    container_object.animation_data_clear()
    
    for f in frames:
        # Calculate next position
        container.rectilinear_move(accel_car, TIME, axis="x")
        
        # Set current frame
        context.scene.frame_set(f)
        
        # Get marble position
        container_object.location = container.get_cartesien_position()
        
        # Insert keyframe
        container_object.keyframe_insert(data_path="location", frame=f)
        
        if f == FRAME_RATE:
            accel_car = 0
            container.v_x = 0
        
     
sim_all()
        
bpy.ops.screen.animation_play()