import bpy
import mathutils
import math
from statistics import mean
from bpy import data as d
from math import pi
from mathutils import Vector
from math import radians

class DistanceSensor:
    
    def __init__(self, vehicule, sensor, obstacle_prefix="Obstacle"):
        vehicule_location = vehicule.matrix_world.translation
        self.vehicule = vehicule
        self.location = sensor.matrix_world.translation
        self.vector = self.location - vehicule_location
        self.angle_threshold = ((30+40)/2)/2
        self.obstacle_prefix = obstacle_prefix
        self.sensor = sensor
        
        
    def get_raw_distance(self, debug=False):
        bpy.context.view_layer.update()
        closest_obstacle_distance = None
        closest_obstacle_name = None
        self.location = self.sensor.matrix_world.translation
        vehicule_location = self.vehicule.matrix_world.translation
        self.vector = self.location - vehicule_location
        
        if debug:
            in_range = []
            out_of_range = []
        
        for obj in d.objects:        
            if obj.name.startswith(self.obstacle_prefix) :
                obstacle_vector = obj.location - self.location
                osbtacle_sensor_angle = self.vector.angle(obstacle_vector)*360/(2*pi)
                if osbtacle_sensor_angle <= self.angle_threshold:
                    obstacle_distance = (obj.location - self.location).length * 1000
                    if closest_obstacle_distance is None or obstacle_distance < closest_obstacle_distance :
                        closest_obstacle_distance = obstacle_distance
                        closest_obstacle_name = obj.name
                    if debug : 
                        in_range.append({
                            "name" : obj.name,
                            "location" : obj.location, 
                            "vector" : obstacle_vector,
                            "angle" : osbtacle_sensor_angle,
                            "distance" : obstacle_distance
                        })                
                elif debug :
                    out_of_range.append({
                            "name" : obj.name,
                            "location" : obj.location, 
                            "vector" : obstacle_vector,
                            "angle" : osbtacle_sensor_angle
                    })
        if debug : 
            print("------------------ In range objects ------------------")
            for obj in in_range :
                print(str(obj))
                
            print("------------------ Out of range objects ------------------")
            for obj in out_of_range :
                print(str(obj))
            print("----------------------------------------------------------")
                
        return closest_obstacle_distance, closest_obstacle_name
    
    
    def get_sim_distance(self, debug=False):
        distance, name = self.get_raw_distance(debug=debug)
        if distance is None or distance <= 0:
            return distance
        return self.apply_trendline(raw_distance=distance), name
    
    #To do - change trendline values
    def apply_trendline(self,raw_distance):
        return 0.9207 * raw_distance - 34.295


############ Setup ############
start_pos = (0,0,0.025)
start_angle = (0,0,math.pi/18)

ob = bpy.data.objects.get("Voiture")
ob.select_set(True)
ob.animation_data_clear()
ob.location = start_pos
ob.rotation_mode= 'XYZ'
ob.rotation_euler = start_angle
frame_num = 0

c1 = bpy.data.objects.get("Capteur")
c2 = bpy.data.objects.get("Capteur.001")
c3 = bpy.data.objects.get("Capteur.003")
c4 = bpy.data.objects.get("Capteur.002")
c5 = bpy.data.objects.get("Capteur.004")
line = bpy.data.objects.get("Plane")

capteurs = [c4, c2, c1, c3, c5]

last_angle = 0.0
SENSOR = d.objects["CapteurDistance"]
sensor = DistanceSensor(vehicule=ob, sensor=SENSOR)

##### Functions #######
def is_captor_over_line(captor, line):
    bpy.context.view_layer.update()
    origin = captor.matrix_world.translation
    print("captor position : " + str(origin))
    
    ray_direction = mathutils.Vector((0,0,-1))
    
    ray_begin_local = line.matrix_world.inverted() @ origin

    result, loc, normal, face_idx = line.ray_cast(ray_begin_local, ray_direction)

    return result

def lf_read_digital():
    return [int(is_captor_over_line(captor, line)) for captor in capteurs] 


def get_angle_to_turn():
    angle = 0
    read = lf_read_digital()
    print(read)
    
    if read == [0,0,0,0,0]:
        return last_angle
    
    angle = (mean([i for i, n in enumerate(read) if n==1])-2)*-2
    print("Angle: ",angle)
    return math.radians(angle)
    
def print_obstacle_distance(distance, name):
    if distance is None or distance <= 0: 
        print("No obstacle found")
    else :
        print(name + " found at distance : " + str(distance) + " mm")
            
def should_stop(distance):
    if distance is None or distance <= 0:
        return False
    elif distance <= 150:
        return True
    return False

##### Animation #######
for i in range(900):
    print("FRAME :: ", i)
    bpy.context.scene.frame_set(frame_num)
    
    # Distance sensor
    print("\n ------------------------------- Calculating distance with obstacles ------------------------------- \n")
    obstacle_distance, name = sensor.get_raw_distance(debug=True)
    print_obstacle_distance(distance=obstacle_distance, name=name)
    if should_stop(distance=obstacle_distance):
        print("\n -------------------------------------------------------------------------------------------------- \n")
        print("stopping at distance : " + str(obstacle_distance) + "mm from obstacle")
        print("\n -------------------------------------------------------------------------------------------------- \n")
        break
    print("\n -------------------------------------------------------------------------------------------------- \n")
    
    # Line Follower
    angle = get_angle_to_turn()
    last_angle = angle
    print("Angle rad:", angle)
    ob.rotation_euler.z += angle
    print("Angle ob:", ob.rotation_euler.z)

    vec = mathutils.Vector((0.001,0,0))
    inv = ob.matrix_world.copy()
    inv.invert()
    vec_rot = vec @ inv

    ob.location += vec_rot
    
    bpy.ops.anim.keyframe_insert(type='LocRotScale') 
    frame_num+=1
    

print("Done")