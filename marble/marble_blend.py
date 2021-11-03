import bpy
from bpy import context

from math import pi
from math import exp, sqrt, sin, cos, asin, atan

ROTATION_RADIUS = 140
CONTAINER_HEIGHT = 8.5 # 10mm - 1.5mm concavity
MARBLE_MASS = 0.0052
MARBLE_R = 7.5
G = 9810
DAMP = 1
Z = sqrt(G / ROTATION_RADIUS)

FRAME_RATE = 30
TOTAL_FRAMES = 120
TIME = 1 / FRAME_RATE

class Container:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
        
        self.v_x = 0
        self.v_y = 0
        
        self.a_x = 0
        self.a_y = 0
        
        self.marble = Marble(x=self.x, y=self.y, z=15)

    def get_position(self):
        return (self.x, self.y, self.z)
    
    def get_marble_position(self):
        return self.marble.get_cartesian_position()
    
    def set_acceleration(self, accel, angle=0):
        
        self.a_x = accel*cos(angle)
        self.a_y = accel*sin(angle)
        
        self.marble.set_acceleration(accel, angle)
    
    def compute_rect_position(self):
        x = self.v_x*TIME + 0.5*self.a_x*TIME**2
        y = self.v_y*TIME + 0.5*self.a_y*TIME**2
        
        return x, y
    
    def compute_rect_velocity(self):
        x = self.a_x*TIME
        y = self.a_y*TIME
        
        return x, y
        
    def rectilinear_move(self, stopping=False):
        
        # Compute new velocities
        v_x, v_y = self.compute_rect_velocity()
        
        if stopping:
            # Need to check if there was a sign change in velocities
            # If so, make velocities 0
            if self.v_x >= 0 and v_x <= 0 or self.v_x <= 0 and v_x >= 0:
                v_x = 0
                self.v_x = 0
                self.a_x = 0
            if self.v_y >= 0 and v_y <= 0 or self.v_y <= 0 and v_y >= 0:
                v_y = 0
                self.v_y = 0
                self.a_y = 0
        
        # Compute new positions        
        x, y = self.compute_rect_position()
        
        self.v_x += v_x
        self.x += x
        
        self.v_y += v_y
        self.y += y
        
        # Make marble oscillate inside the container
        self.marble.simulate() 


class Marble:

    def __init__(self, x=0.0, y=0.0, z=0.0, accel=0.0):
        self.x = x
        self.y = y
        self.z = z

        self.alpha = accel
        self.alpha_angle = 0
        self.omega = 0
        self.theta = asin(sqrt(x ** 2 + y ** 2) / ROTATION_RADIUS)

        self.init_theta = self.theta
        self.init_omega = self.omega

        self.rel_time = 0

    def get_cartesian_position(self):
        return self.x, self.y, self.z

    def set_cartesian_position(self):
        linear_displacement = ROTATION_RADIUS * sin(self.theta)
        self.x = linear_displacement * cos(self.alpha_angle)
        self.y = linear_displacement * sin(self.alpha_angle)
        # self.z = MARBLE_R + CONTAINER_HEIGHT + ROTATION_RADIUS*(1 - cos(self.theta))
        
    def set_acceleration(self, accel, angle=0.0):
        self.alpha = accel
        self.alpha_angle = angle
        self.rel_time = TIME

    def compute_theta(self):
        damping_factor = exp(-DAMP * self.rel_time)

        C = -self.alpha / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        pos = A * cos(Z * self.rel_time) + \
              B * sin(Z * self.rel_time) + C / Z ** 2

        return damping_factor * pos

    def compute_omega(self):
        damping_factor = exp(-DAMP * self.rel_time)

        C = -self.alpha / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        pos = A * cos(Z * self.rel_time) + B * sin(Z * self.rel_time) + C / Z ** 2
        vel = -A * sin(Z * self.rel_time) * Z + B * cos(Z * self.rel_time) * Z

        return vel * damping_factor + -DAMP * damping_factor * pos

    def simulate(self):
        if self.rel_time == TIME:
            self.init_omega = self.omega
            self.init_theta = self.theta

        self.theta = self.compute_theta()
        self.omega = self.compute_omega()

        self.set_cartesian_position()
        self.rel_time += TIME
        
   
###############################################################################################     

#                                             SIMULATIONS                                     #

###############################################################################################

def sim_marble():
   
    marble_object = bpy.context.scene.objects["Marble"]
    container_object = bpy.context.scene.objects["Container"]
    
    container_object.animation_data_clear()
    marble_object.animation_data_clear()
    
    marble = Marble(x=0, y=0, z=15, accel=1000)
   
    frames = range(TOTAL_FRAMES)
   
    for f in frames:
        print("FRAME :: ", f)
        # Calculate next position
        marble.simulate()
       
        # Set current frame
        context.scene.frame_set(f)
       
        # Get marble position
        marble_object.location = marble.get_cartesian_position()

        print("POSITION :: ", marble_object.location)
       
        # Insert keyframe
        marble_object.keyframe_insert(data_path="location", frame=f)
       
        if f == 12:
            marble.set_acceleration(0)

        if f == 80:
            marble.set_acceleration(-1000)

        if f == 92:
            marble.set_acceleration(0)
            
def sim_all():
    marble_object = bpy.context.scene.objects["Marble"]
    container_object = bpy.context.scene.objects["Container"]
    
    marble_object.animation_data_clear()
    container_object.animation_data_clear()
    
    car_accel = 1000
    accel_angle = pi/2
    car_stopping = False
    
    container = Container(z=5)
    
    container.set_acceleration(car_accel, angle=accel_angle)
    
    frames = range(TOTAL_FRAMES)
    
    for f in frames:
        print("FRAME :: ", f)
        # Calculate next position
        container.rectilinear_move(stopping=car_stopping)
        
        # Set current frame
        context.scene.frame_set(f)
       
        # Get marble position
        marble_object.location = container.get_marble_position()
        
        # Get container position
        container_object.location = container.get_position()
       
        # Insert keyframe
        marble_object.keyframe_insert(data_path="location", frame=f)
        container_object.keyframe_insert(data_path="location", frame=f)
       
        if f == 10:
            container.set_acceleration(car_accel, angle=accel_angle)

        if f == 30:
            car_stopping=True
            container.set_acceleration(-car_accel, angle=accel_angle)

        if f == 40:
            container.set_acceleration(0, angle=accel_angle)
            car_stopping = False
            
#        if f == 50:
#            container.set_acceleration(car_accel, angle=(pi/2))
#            
#        if f == 70:
#            car_stopping=True
#            container.set_acceleration(-car_accel, angle=(pi/2))
#            
#        if f == 80:
#            container.set_acceleration(0, angle=(pi/2))

if __name__ == "__main__":
    sim_all()