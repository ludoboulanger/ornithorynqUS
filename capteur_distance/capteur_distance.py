import bpy
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


def sim_raw_single(sensor):
    print("\n ----------------------- Single object simulation - Raw distance calculated ----------------------- \n")
    obstacle_distance, name = sensor.get_raw_distance(debug=True)
    print_obstacle_distance(distance=obstacle_distance, name=name)
    print("\n -------------------------------------------------------------------------------------------------- \n")


def sim_corrected_single(sensor):
    print("\n ----------------------- Single object simulation - distance calculated with trendline ----------------------- \n")
    obstacle_distance, name = sensor.get_sim_distance(debug=True)
    print_obstacle_distance(distance=obstacle_distance, name=name)
    print("\n ------------------------------------------------------------------------------------------------------------- \n")
      
        
def sim_corrected_multiple(sensor, start_pos, start_angle, final_angle, angle_incr):
    print("\n ----------------------- Multiple object simulation - distance calculated with trendline ----------------------- \n")
    sensor.vehicule.location = start_pos
    for angle in range(start_angle, final_angle + angle_incr, angle_incr):
        sensor.vehicule.rotation_euler = (0,0, radians(angle))
        obstacle_distance, name = sensor.get_sim_distance()
        print("\nCurrent vehicule angle around z axis : " + str(angle))
        print_obstacle_distance(distance=obstacle_distance, name=name)
    print("\n ------------------------------------------------------------------------------------------------------------- \n")
 
 
def sim_raw_multiple(sensor, start_pos, start_angle, final_angle, angle_incr):
    print("\n ----------------------- Multiple object simulation - distance calculated with trendline ----------------------- \n")
    sensor.vehicule.location = start_pos
    for angle in range(start_angle, final_angle + angle_incr, angle_incr):
        sensor.vehicule.rotation_euler = (0,0, radians(angle))
        obstacle_distance, name = sensor.get_raw_distance(debug=True)
        print("\nCurrent vehicule angle around z axis : " + str(angle))
        print_obstacle_distance(distance=obstacle_distance, name=name)
    print("\n ------------------------------------------------------------------------------------------------------------- \n")
  
         
        
def print_obstacle_distance(distance, name):
    if distance is None or distance <= 0: 
        print("No obstacle found")
    else :
        print(name + " found at distance : " + str(distance) + " mm")


def main():
    # Setup
    VEHICULE = d.objects["Voiture"]
    SENSOR = d.objects["Capteur"]
    sensor = DistanceSensor(vehicule=VEHICULE, sensor=SENSOR)
    
    # Test a single obstacle - raw distance calculated
    sim_raw_single(sensor)
    
    # Test multiple objects - raw distance calculated
    sim_raw_multiple(sensor, start_pos=(0,0,0), start_angle=0, final_angle=360, angle_incr=10)
    
    
    # Test a single obstacle - corrected distance calculated using experimental trendline
    #sim_corrected_single(sensor)
    
    # Test multiple objects - corrected distance calculated using experimental trendline
    #sim_corrected_multiple(sensor, start_pos=(0,0,0), start_angle=0, final_angle=360, angle_incr=10)


if __name__ == "__main__":
    main()

