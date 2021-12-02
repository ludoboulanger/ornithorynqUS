import bpy
import mathutils
import math
from statistics import mean
from bpy import data as d
from mathutils import Vector
from math import radians, degrees, pi
import numpy as np
from enum import Enum
LF_SENSORS = ["Capteur.002", "Capteur.001", "Capteur", "Capteur.003", "Capteur.004"]
SENSOR = d.objects["DistanceSensor"]
LINE = "Plane"
CAR = "Vehicle"
MARBLE = "Marble"
OBSTACLE= "Cube"
FRAME_NUM = 3000
FRAMERATE = 30 # Framerate
TIME = 1 / FRAMERATE
DISTANCE_WHEELS = 0.14 # 14cm d'empattement
DISTANCE_STOP=0.1 #200 mm
TURN_ANGLE = 15
FIND_LINE_ANGLE = 30

ACCELERATIONFACTOR = 1.5
DECELERATIONFACTOR = 2.5
TURN_ACCELERATION_FACTOR = 5

# Constantes pour bille
ROTATION_RADIUS = 0.14
CONTAINER_HEIGHT = 0.0085 # 10mm - 1.5mm concavity
MARBLE_MASS = 0.0052
MARBLE_R = 0.005
G = 9.810
DAMP = 0.5
Z = np.sqrt(G / ROTATION_RADIUS)

VEHICLE_STATES = {
    'STOP' : 0,
    'FORWARD' : 1,
    'BACKWARD' : 2,
}

class Marble:

    def __init__(self, x=0.0, y=0.0, z=0.0, accel=0.0, angle = 0.0):
        self.x = x
        self.y = y
        self.z = z

        self.alpha = np.array([accel*np.cos(angle), accel*np.sin(angle)])
        self.omega = np.array([0,0])
        self.theta = np.arcsin(np.array([x,y]) / ROTATION_RADIUS)

        self.init_theta = self.theta
        self.init_omega = self.omega

        self.rel_time = 0

    def get_cartesian_position(self):
        return self.x, self.y, self.z

    def set_cartesian_position(self):
        linear_displacement = ROTATION_RADIUS * np.sin(self.theta)
        self.x = linear_displacement[0]
        self.y = linear_displacement[1] 
        # self.z = MARBLE_R + CONTAINER_HEIGHT + ROTATION_RADIUS*(1 - cos(self.theta))
        
    def set_acceleration(self, accel, angle=0.0):
        self.alpha = np.array([accel * np.cos(angle), accel * np.sin(angle)])
        self.rel_time = TIME

    def compute_theta(self):
        damping_factor = np.exp(-DAMP * self.rel_time)

        C = -self.alpha / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        pos = A * np.cos(Z * self.rel_time) + \
              B * np.sin(Z * self.rel_time) + C / Z ** 2

        return damping_factor * pos

    def compute_omega(self):
        damping_factor = np.exp(-DAMP * self.rel_time)

        C = -self.alpha / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        pos = A * np.cos(Z * self.rel_time) + B * np.sin(Z * self.rel_time) + C / Z ** 2
        vel = -A * np.sin(Z * self.rel_time) * Z + B * np.cos(Z * self.rel_time) * Z

        return vel * damping_factor + -DAMP * damping_factor * pos

    def simulate(self):
        if self.rel_time == TIME:
            self.init_omega = self.omega
            self.init_theta = self.theta

        self.theta = self.compute_theta()
        self.omega = self.compute_omega()

        self.set_cartesian_position()
        self.rel_time += TIME


class Vehicle:

    _coordinates = [0, 0, 0] # Coordonnées du véhicule
    _heading = 0 # Cap du véhicule en radians
    _speed = 0 # Vitesse du véhicule actuelle en m/s
    _prev_speed = 0 # Vitesse précédente du véhicule en m/s. Sert à calculer l'ACCÉLÉRATION
    _wheel_angle = np.pi/2 # Angle des roues, 90 degrés est le centre
    _acceleration = 0 # Accélération du véhicule actuelle, en m/s2
    _state = VEHICLE_STATES['STOP'] # État, 0 = stop, 1 = avancer, 2 = arrêté
    _is_turning = False

    def __init__(self, coordinates, heading):
        self._coordinates = coordinates
        self._heading = heading
        self._marble = Marble()

    def get_marble_position(self, heading):
        
        rotation_matrix = np.array([
            [np.cos(heading), np.sin(heading), 0],
            [-np.sin(heading), np.cos(heading), 0],
            [0, 0, 1]
        ])

        coords = np.array(self._marble.get_cartesian_position())

        return rotation_matrix @ coords

    # Retourne le pourcentage nécessaire pour obtenir une certaine vitesse en m/s
    # À utiliser pour le vrai véhicule
    def speed_to_percent(self, speed):
        percent = speed/5 # TODO changer la vitesse maximale, ce qui devrait nous donner la bonne valeur
        return percent

    # Converti l'angle des roues en radians en rayon de virage en mètres
    # TODO utiliser les vraies valeurs
    # Pour l'instant on va utiliser un calcul théorique. Cela assume un cas
    # parfait qui n'est pas réaliste. Un meilleur algo est à faire, basé sur:
    # https://patentimages.storage.googleapis.com/c9/d1/1a/2826ee9a515566/WO2005102822A1.pdf
    def angle_to_radius(self, angle):
        try:
            # print("Angle commandé:", angle)
            if angle <= np.pi/2:
                radius = DISTANCE_WHEELS/np.tan(angle)
        except:
            print("Erreur de calcul du rayon")
            return 0
        return radius

    # Retourne l'accélération en fonction du changement de vitesse
    def update_acceleration(self, diff_speed):
       # Sécurité pour la méthode
       if diff_speed > 0.27:
           self._acceleration = 0
           return 0
       elif diff_speed < -0.27:
           self._acceleration = 0
           return 0

       if diff_speed > 0: # Accélération
           self._acceleration = ACCELERATIONFACTOR * (-794.171873034486*np.power(diff_speed, 3)\
                + 281.9660606932039*np.power(diff_speed, 2)\
                - 0.414200251036732*diff_speed\
                - 0.6495715769694956)
       elif diff_speed < 0: # Décélération, on assume l'inverse de l'accélération
           diff_speed = np.abs(diff_speed)
           self._acceleration = -1 * DECELERATIONFACTOR *(-794.171873034486*np.power(diff_speed, 3)\
                + 281.9660606932039*np.power(diff_speed, 2)
                - 0.414200251036732*diff_speed\
                - 0.6495715769694956)
       else:
           self._acceleration = 0

    # Ajuste la vitesse du robot, équivalent à la librairie du robot
    def speed(self, percent):
        self._is_turning = False
        if percent < 0:
            self._speed = 0
            return
        if percent > 100:
            self._speed = 0.27
            return
        speed = 0.002736871508379887 * percent - 0.01346368715083793
        self._speed = speed

    # Mettre les roues droites
    def turn_straight(self):
        self._is_turning = False
        self._wheel_angle = np.radians(90-90)

    # Tourner à un angle, en degrés. 90 est tout droit.
    def turn(self, angle):
        # LineFollower call toujours turn, donc on check si il
        # dit daller tout droit ou non
        if angle == 90:
            self.turn_straight()
            return
        
        self._is_turning = True
        if angle >= 0:
            self._wheel_angle = np.radians(90-angle)

    # Avancer
    def forward(self):
        self._state = VEHICLE_STATES['FORWARD']

    # Reculer
    def backward(self):
        self._state = VEHICLE_STATES['BACKWARD']

    # Arrêter
    def stop(self):
        self._is_turning = False
        self._speed = 0
        self._state = VEHICLE_STATES['STOP']


    # Méthode à rouler à chaque frame qui va automatiquement déplacer le véhicule. Ça sert à simuler le comportement du vrai véhicule
    def update(self):
        # Calcul de l'accélération
        self.update_acceleration(self._speed - self._prev_speed)
        car_acceleration = self._acceleration
        acceleration_angle = self._heading

        # print("Accélération à: ", self._acceleration)

        # Calcul du cap
        circon = np.abs(self.angle_to_radius(self._wheel_angle)) * 2 * np.pi
        # print("Circonférence: ", circon)
        # print("self._angleroues:", self._wheel_angle)
        
        # Virage
        if self._is_turning:
            car_acceleration = TURN_ACCELERATION_FACTOR  * self._speed**2 / np.abs(self.angle_to_radius(self._wheel_angle))
            if self._state == 1:
                distanceframe = self._speed * TIME
            elif self._state == 2:
                distanceframe = -1 * self._speed * TIME
            else:
                distanceframe = 0
                
            if self._wheel_angle >= 0:
                self._heading -= ((distanceframe/circon) * 2 * np.pi)

                if self._heading <= 0:
                    self._heading += 2*np.pi

                acceleration_angle = self._heading - np.pi/2

            else:
                self._heading += ((distanceframe/circon) * 2 * np.pi)

                if self._heading >= 2*np.pi:
                    self._heading -= 2*np.pi

                acceleration_angle = self._heading + np.pi/2

        # print("Cap:", self._heading)

        # Déplacement
        if self._state == VEHICLE_STATES['FORWARD']:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading))
            # print("Avancer: ", self._coordinates)
        elif self._state == VEHICLE_STATES['BACKWARD']:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading + np.pi))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading + np.pi))
            # print("Reculer: ", self._coordinates)
        elif self._state == VEHICLE_STATES['STOP']:
            car_acceleration = -self._prev_speed / TIME
            acceleration_angle = self._heading
        else:
            print("Erreur, état invalide")

        # On met à jour l'ancienne vitesse
        self._prev_speed = self._speed

        # Simule le mouvement de la bille
        if self._state == VEHICLE_STATES['BACKWARD']:
            car_acceleration *= -1
        
        self._marble.set_acceleration(car_acceleration, angle=acceleration_angle)
        self._marble.simulate()
        return self._coordinates

class DistanceSensor:

    def __init__(self, vehicule, sensor, obstacle_prefix=OBSTACLE):
        vehicule_location = vehicule.matrix_world.translation
        self.vehicule = vehicule
        self.location = sensor.matrix_world.translation
        self.vector = self.location - vehicule_location
        self.angle_threshold = ((30 + 40) / 2) / 2
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
            if obj.name.startswith(self.obstacle_prefix):
                obstacle_vector = obj.location - self.location
                osbtacle_sensor_angle = self.vector.angle(obstacle_vector) * 360 / (2 * pi)
                if osbtacle_sensor_angle <= self.angle_threshold:
                    obstacle_distance = (obj.location - self.location).length * 1000
                    if closest_obstacle_distance is None or obstacle_distance < closest_obstacle_distance:
                        closest_obstacle_distance = obstacle_distance
                        closest_obstacle_name = obj.name
                    if debug:
                        in_range.append({
                            "name": obj.name,
                            "location": obj.location,
                            "vector": obstacle_vector,
                            "angle": osbtacle_sensor_angle,
                            "distance": obstacle_distance
                        })
                elif debug:
                    out_of_range.append({
                        "name": obj.name,
                        "location": obj.location,
                        "vector": obstacle_vector,
                        "angle": osbtacle_sensor_angle
                    })
        if debug:
            print("------------------ In range objects ------------------")
            for obj in in_range:
                print(str(obj))

            print("------------------ Out of range objects ------------------")
            for obj in out_of_range:
                print(str(obj))
            print("----------------------------------------------------------")

        return closest_obstacle_distance, closest_obstacle_name

    def get_sim_distance(self, debug=False):
        distance, name = self.get_raw_distance(debug=debug)
        if distance is None or distance <= 0:
            return distance
        return self.apply_trendline(raw_distance=distance), name

    # To do - change trendline values
    def apply_trendline(self, raw_distance):
        return 0.9207 * raw_distance - 34.295


class LineFollower():

    def __init__(self, sensors_names, line_name):
        self.last_angle = 0
        self.sensors = [bpy.data.objects.get(sensor) for sensor in sensors_names]
        self.line = bpy.data.objects.get(line_name)

    def is_sensor_over_line(self, sensor):
        bpy.context.view_layer.update()
        origin = sensor.matrix_world.translation

        ray_direction = mathutils.Vector((0, 0, -1))

        ray_begin_local = self.line.matrix_world.inverted() @ origin

        result, loc, normal, face_idx = self.line.ray_cast(ray_begin_local, ray_direction)

        return result

    def lf_read_digital(self):
        return [int(self.is_sensor_over_line(sensor)) for sensor in self.sensors]
    
    def is_over_line(self):
        for sensor in self.sensors:
            if self.is_sensor_over_line(sensor):
                return True
        return False

    def get_angle_to_turn(self):
        angle = 0
        read = self.lf_read_digital()

        if read == [0, 0, 0, 0, 0]:
            angle = np.sign(self.last_angle)*45
        else:
            angle = (2 - np.mean(np.nonzero(read))) * 45/2
        self.last_angle = angle
        return math.radians(angle)


def print_obstacle_distance(distance, name):
    if distance is None or distance <= 0:
        print("No obstacle found")
    else:
        print(name + " found at distance : " + str(distance) + " mm")


def should_stop(distance):
    distance_stop_mm = DISTANCE_STOP*1000
    if distance is None or distance <= 0 or  distance > distance_stop_mm:
        return False
    else:
        return True



def init_car():
    start_pos = [-0, 0, 0.025]
    start_angle = (0, 0, 0)

    blender_car = bpy.data.objects.get(CAR)
    blender_car.select_set(True)
    blender_car.animation_data_clear()
    blender_car.location = start_pos
    blender_car.rotation_euler = start_angle

    car = Vehicle(start_pos, 0)
    car.speed(80)
    # vehicule.turn(87)
    car.turn_straight()
    car.forward()

    return car, blender_car

def init_marble():
    b_marble = d.objects['Marble']
    b_marble.animation_data_clear()

    return b_marble
        
def animate_frame(frame_num, car, blender_car, blender_marble):
    # print("FRAME :: ", frame_num)
    bpy.context.scene.frame_set(frame_num)

    # On déplace le véhicule
    blender_marble.location = car.get_marble_position(car._heading)
    blender_car.location = car.update()
    blender_car.rotation_euler.z = car._heading

    # On ajout un keyframe
    blender_car.keyframe_insert(data_path="location", frame=frame_num)
    blender_car.keyframe_insert("rotation_euler", frame=frame_num)
    blender_marble.keyframe_insert(data_path="location", frame=frame_num)

class State(Enum):
    OBSTACLE_APPROACHING = 1
    OBSTACLE_WAITING = 2
    OBSTACLE_BACKWARD = 3
    OBSTACLE_TURN = 4
    OBSTACLE_FIND_LINE = 5
    FOLLOW_LINE = 6


def main():
    car, blender_car = init_car()
    blender_marble = init_marble()
    distance_sensor = DistanceSensor(vehicule=blender_car, sensor=SENSOR)
    line_follower = LineFollower(sensors_names=LF_SENSORS, line_name=LINE)
    get_around = False
    state = State.FOLLOW_LINE
    start_waiting_frame = 0
    WAITING_SEC = 5
    WAITING_FRAME_NUM = WAITING_SEC * FRAMERATE

    start_turn_frame = None

    for i in range(1, FRAME_NUM):
        print(f"***********FRAME_NUM: {i}******************")
        obstacle_distance, _ = distance_sensor.get_raw_distance()
        if(state == State.FOLLOW_LINE):
            car.speed(80)
            if should_stop(distance=obstacle_distance):
                state= State.OBSTACLE_WAITING
                start_waiting_frame = i
            else:
                angle = line_follower.get_angle_to_turn()
                car.turn(degrees(angle)+90)
        elif(state == State.OBSTACLE_WAITING):
            car.stop()
            if i - start_waiting_frame > WAITING_FRAME_NUM:
                state = State.OBSTACLE_BACKWARD
        elif(state == State.OBSTACLE_BACKWARD):
            car.backward()
            car.turn_straight()
            car.speed(50)
            if obstacle_distance is None or obstacle_distance >= 300:
                state = State.OBSTACLE_TURN
                start_turn_frame = i
        elif(state == State.OBSTACLE_TURN):
                frame_in_turn = math.sqrt(0.3**2+(DISTANCE_WHEELS/2)**2)/(car._speed / FRAMERATE)        
                car.forward()   
                car.speed(50)   
                car.turn(90+TURN_ANGLE) 
                if i-start_turn_frame>=frame_in_turn:  
                    state = State.OBSTACLE_FIND_LINE    
        elif(state == State.OBSTACLE_FIND_LINE):
                car.turn(90-FIND_LINE_ANGLE)
                if line_follower.is_over_line():
                    state= State.FOLLOW_LINE
            
        animate_frame(frame_num=i, car=car, blender_car=blender_car, blender_marble=blender_marble)


if __name__ == '__main__':
    main()
    print("Done")
