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

    def update_cartesian_position(self):
        linear_displacement = ROTATION_RADIUS * sin(self.theta)
        self.x = linear_displacement * cos(self.alpha_angle)
        self.y = linear_displacement * sin(self.alpha_angle)
        # self.z = MARBLE_R + CONTAINER_HEIGHT + ROTATION_RADIUS*(1 - cos(self.theta))

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

        self.update_cartesian_position()
        self.rel_time += TIME

    def set_accel(self, accel, angle=0.0):
        self.alpha = accel
        self.alpha_angle = angle
        self.rel_time = TIME
        
        
def sim_marble():
   
    marble_object = bpy.context.scene.objects["Marble"]
    marble_object.animation_data_clear()
    marble = Marble(x=0, y=0, z=15, accel=1300)
   
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
            marble.set_accel(0)

        if f == 80:
            marble.set_accel(-1300)

        if f == 92:
            marble.set_accel(0)

if __name__ == "__main__":
    sim_marble()