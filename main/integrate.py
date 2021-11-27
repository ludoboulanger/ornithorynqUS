import bpy
import mathutils
import math
from statistics import mean
from bpy import data as d
from mathutils import Vector
from math import radians, degrees, pi
import numpy as np

LF_SENSORS = ["Capteur.002", "Capteur.001", "Capteur", "Capteur.003", "Capteur.004"]
SENSOR = d.objects["DistanceSensor"]
LINE = "Plane"
CAR = "Vehicle"
FRAME_NUM = 900
FRAMERATE = 30 # Framerate
TIME = 1 / FRAMERATE
DISTANCE_WHEELS = 0.14 # 14cm d'empattement


class Vehicle:

    _coordinates = [0, 0, 0] # Coordonnées du véhicule
    _heading = 0 # Cap du véhicule en radians
    _speed = 0 # Vitesse du véhicule actuelle en m/s
    _prev_speed = 0 # Vitesse précédente du véhicule en m/s. Sert à calculer l'ACCÉLÉRATION
    _wheel_angle = np.pi/2 # Angle des roues, 90 degrés est le centre
    _acceleration = 0 # Accélération du véhicule actuelle, en m/s2
    _state = 0 # État, 0 = stop, 1 = avancer, 2 = arrêté

    def __init__(self, coordinates, heading):
        self._coordinates = coordinates
        self._heading = heading

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
            print("Angle commandé:", angle)
            if angle <= np.pi/2:
                radius = DISTANCE_WHEELS/np.tan(angle)
        except:
            print("Erreur de calcul du rayon")
            return 0
        return radius

    # Retourne l'accélération en fonction du changement de vitesse
    def acceleration(self, diff_speed):
        # Sécurité pour la méthode
        if diff_speed > 0.27:
            self._acceleration = 0
            return 0
        elif diff_speed < -0.27:
            self._acceleration = 0
            return 0

        if diff_speed > 0: # Accélération
            self._acceleration = -794.171873034486*np.power(diff_speed, 3)+281.9660606932039*np.power(diff_speed, 2)-0.414200251036732*diff_speed-0.6495715769694956
        elif diff_speed < 0: # Décélération, on assume l'inverse de l'accélération
            diff_speed = np.abs(diff_speed)
            self._acceleration = -1*(-794.171873034486*np.power(diff_speed, 3)+281.9660606932039*np.power(diff_speed, 2)-0.414200251036732*diff_speed-0.6495715769694956)
        else:
            self._acceleration = 0
        return self._acceleration

    # Ajuste la vitesse du robot, équivalent à la librairie du robot
    def speed(self, percent):
        if percent < 0:
            self._speed = 0
            return
        if percent > 100:
            self._speed = 0.27
            return
        speed = 0.002736871508379887*percent-0.01346368715083793
        self._speed = speed

    # Mettre les roues droites
    def turn_straight(self):
        self._wheel_angle = np.radians(90-90)

    # Tourner à un angle, en degrés. 90 est tout droit.
    def turn(self, angle):
        if angle >= 0:
            self._wheel_angle = np.radians(90-angle)

    # Avancer
    def forward(self):
        self._state = 1

    # Reculer
    def backward(self):
        self._state = 2

    # Arrêter
    def stop(self):
        self._state = 0


    # Méthode à rouler à chaque frame qui va automatiquement déplacer le véhicule. Ça sert à simuler le comportement du vrai véhicule
    def update(self):
        # Calcul de l'accélération
        self._acceleration = self.acceleration(self._speed - self._prev_speed)
        print("Accélération à: ", self._acceleration)

        # Calcul du cap
        circon = np.abs(self.angle_to_radius(self._wheel_angle)) * 2 * np.pi
        print("Circonférence: ", circon)
        print("self._angleroues:", self._wheel_angle)
        if circon > 0:
            if self._state == 1:
                distanceframe = self._speed * TIME
            elif self._state == 2:
                distanceframe = -1 * self._speed * TIME
            if self._wheel_angle >= 0:
                self._heading = self._heading - ((distanceframe/circon) * 2 * np.pi)
            else:
                self._heading = (self._heading) + ((distanceframe/circon) * 2 * np.pi)

        print("Cap:", self._heading)

        # Déplacement
        if self._state == 1:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading))
            print("Avancer: ", self._coordinates)
        elif self._state == 2:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading + np.pi))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading + np.pi))
            print("Reculer: ", self._coordinates)
        elif self._state == 0:
            print("Stop: ", self._coordinates)
        else:
            print("Erreur, état invalide")

        # On met à jour l'ancienne vitesse
        self._vitesseprec = self._speed
        return self._coordinates

class DistanceSensor:

    def __init__(self, vehicule, sensor, obstacle_prefix="Obstacle"):
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
        print("Sensor position : " + str(origin))

        ray_direction = mathutils.Vector((0, 0, -1))

        ray_begin_local = self.line.matrix_world.inverted() @ origin

        result, loc, normal, face_idx = self.line.ray_cast(ray_begin_local, ray_direction)

        return result

    def lf_read_digital(self):
        return [int(self.is_sensor_over_line(sensor)) for sensor in self.sensors]

    def get_angle_to_turn(self):
        angle = 0
        read = self.lf_read_digital()
        print(read)

        if read == [0, 0, 0, 0, 0]:
            angle = self.last_angle
        else:
            angle = (2 - np.mean(np.nonzero(read))) * 90/3
        self.last_angle = angle
        print("Angle: ", angle)
        return math.radians(angle)


def print_obstacle_distance(distance, name):
    if distance is None or distance <= 0:
        print("No obstacle found")
    else:
        print(name + " found at distance : " + str(distance) + " mm")


def should_stop(distance):
    if distance is None or distance <= 0:
        return False
    elif distance <= 150:
        return True
    return False


def init_car():
    start_pos = [0, -0.005, 0.025]
    start_angle = (0, 0, math.pi / 18)

    blender_car = bpy.data.objects.get(CAR)
    blender_car.select_set(True)
    blender_car.animation_data_clear()
    blender_car.location = start_pos
    blender_car.rotation_euler = start_angle

    car = Vehicle(start_pos, 0)
    car.speed(10)
    # vehicule.turn(87)
    car.turn_straight()
    car.forward()

    return car, blender_car


def animate_frame(frame_num, car, blender_car):
    print("FRAME :: ", frame_num)
    bpy.context.scene.frame_set(frame_num)

    # On déplace le véhicule
    blender_car.location = car.update()
    blender_car.rotation_euler.z = car._heading

    # On ajout un keyframe
    blender_car.keyframe_insert(data_path="location", frame=frame_num)
    blender_car.keyframe_insert("rotation_euler", frame=frame_num)


def main():
    car, blender_car = init_car()
    distance_sensor = DistanceSensor(vehicule=blender_car, sensor=SENSOR)
    line_follower = LineFollower(sensors_names=LF_SENSORS, line_name=LINE)

    for i in range(FRAME_NUM):
        obstacle_distance, name = distance_sensor.get_raw_distance(debug=True)
        if should_stop(distance=obstacle_distance):
            break
        else:
            angle = line_follower.get_angle_to_turn()
            car.turn(degrees(angle)+90)
            animate_frame(frame_num=i, car=car, blender_car=blender_car)


if __name__ == '__main__':
    main()
    print("Done")
