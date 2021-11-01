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
        self.v_y = 0
        
        self.marble = Marble(self.x, self.y, 15)

    def get_position(self):
        return (self.x, self.y, self.z)
    
    def get_marble_position(self):
        return self.marble.get_cartesien_position()
        
    """
    direction = ["x", "z"]
    """
    def rectilinear_move(self, a, t, angle=0, stop=False):
        
        if not stop:    
            a_x = a*cos(angle)
            a_y = a*sin(angle)
            
            self.v_x += a_x*TIME
            self.x += self.v_x*TIME + 0.5*a_x*TIME**2
            
            self.v_y += a_y*t
            self.y += self.v_y*TIME + 0.5*a_y*TIME**2
            
        else:
            self.v_x = 0
            self.v_y = 0
        
        # Make marble oscillate inside the container
        self.marble.oscillate(t, accel=-a, accel_angle=angle) 


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
        accel = max_theta*sin(f*t)

        theta = accel

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
        
        
class Simulation:
    
    def __init__(self):
        
        # Objects
        self.marble_object = marble_object = bpy.context.scene.objects["Marble"]
        self.container_object = bpy.context.scene.objects["Container"]
        
        # Animation data
        self.container = Container(0, 0, 5)
        
        self.accel_car = 800
        self.time = 0
        self.last_timestamp = 0
        self.frames = range(TOTAL_FRAMES)
        
    def sim_all(self):
        self.marble_object.animation_data_clear()
        self.container_object.animation_data_clear()
        c_stop = False
        
        for f in self.frames:
            
            if f == 6:
                self.last_timestamp = self.time
                self.accel_car = 0
            elif f == 30:
                c_stop = True
                self.accel_car = -800
                
            # Calculate next position
            current_time = self.time - self.last_timestamp
            self.container.rectilinear_move(self.accel_car, current_time, angle=0, stop=c_stop)
            
            # Set current frame
            context.scene.frame_set(f)
            
            # Get marble position
            self.marble_object.location = self.container.get_marble_position()
            self.container_object.location = self.container.get_position()
            
            # Insert keyframe
            self.marble_object.keyframe_insert(data_path="location", frame=f)
            self.container_object.keyframe_insert(data_path="location", frame=f)

            # Update Time
            self.time += TIME
                
        bpy.ops.screen.animation_play()

    def sim_marble(self):

        # Clear previous data
        self.marble_object.animation_data_clear()
        
        for f in self.frames:
            
            # Calculate next position
            self.marble.oscillate(relative_time, accel=accel_car, accel_angle=0)
            
            # Set current frame
            context.scene.frame_set(f)
            
            # Get marble position
            self.marble_object.location = self.marble.get_cartesien_position()
            
            # Insert keyframe
            self.marble_object.keyframe_insert(data_path="location", frame=f)

            # Update Time
            self.relative_time += TIME
            
            if f == FRAME_RATE:
                self.accel_car = 0
                self.relative_time = 0
 
            
    def sim_container(self):
        self.container_object.animation_data_clear()
        
        for f in frames:
            # Calculate next position
            self.container.rectilinear_move(accel_car, TIME, axis="x")
            
            # Set current frame
            context.scene.frame_set(f)
            
            # Get marble position
            self.container_object.location = self.container.get_cartesien_position()
            
            # Insert keyframe
            self.container_object.keyframe_insert(data_path="location", frame=f)
            
            if f == FRAME_RATE:
                self.accel_car = 0
                self.container.v_x = 0
        

if __name__ == "__main__":
    sim = Simulation()
    
    sim.sim_all()