import time
from datetime import datetime
import bpy
from bpy import data as d
import numpy as np

FRAMERATE = 30 # Framerate
TIME = 1 / FRAMERATE
TOTAL_FRAMES = 250 # nombre de frames à simuler
DISTANCE_WHEELS = 0.14 # 14cm d'empattement


class Vehicle:

    _coordinates = [0, 0, 0] # Coordonnées du véhicule
    _heading = 0 # Cap du véhicule en radians
    _speed = 0 # Vitesse du véhicule actuelle en m/s
    _wheel_angle = np.pi/2 # Angle des roues, 90 degrés est le centre
    _acceleration = 0 # Accélération du véhicule actuelle, en m/s2
    _state = 0 # État, 0 = stop, 1 = avancer, 2 = arrêté

    def __init__(self, coordinates, heading):
        self._coordinates = coordinates
        self._heading = heading

    # Retourne le pourcentage nécessaire pour obtenir une certaine vitesse en m/s
    # À utiliser pour le vrai véhicule
    def speed_to_percent(self, vitesse):
        percent = vitesse/5 # TODO changer la vitesse maximale, ce qui devrait nous donner la bonne valeur
        return percent

    # Converti l'angle des roues en radians en rayon de virage en mètres
    # TODO utiliser les vraies valeurs
    # Pour l'instant on va utiliser un calcul théorique. Cela assume un cas
    # parfait qui n'est pas réaliste. Un meilleur algo est à faire, basé sur:
    # https://patentimages.storage.googleapis.com/c9/d1/1a/2826ee9a515566/WO2005102822A1.pdf
    def angle_to_radius(self, angle):
        try:
            if angle <= np.pi/2:
                radius = DISTANCE_WHEELS/np.tan(angle)
        except:
            return 0
        return radius

    def speed(self, speed):
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
        # Calcul du cap
        circon = np.abs(self.angle_to_radius(self._wheel_angle)) * 2 * np.pi

        if circon > 0:
            if self._state == 1:
                distance_frame = self._speed * TIME
            elif self._state == 2:
                distance_frame = -1 * self._speed * TIME
            if self._wheel_angle >= 0:
                self._heading = self._heading - ((distance_frame/circon) * 2 * np.pi)
            else:
                self._heading = (self._heading) + ((distance_frame/circon) * 2 * np.pi)

        # Déplacement
        if self._state == 1:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading))
        elif self._state == 2:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading + np.pi))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading + np.pi))
        elif self._state == 0:
            print("Stop: ", self._coordinates)
        else:
            print("Erreur, état invalide")

        return self._coordinates

def simulate():
    # init conditions:
    init_position = [0, 0, 0.025]
    # Timestamp
    print("Début de la simlation à ", datetime.now())
    # On vient placer le véhicule au début à 0,0,0
    b_vehicle = d.objects["Vehicle"]
    bpy.context.scene.frame_set(0)
    b_vehicle.location = init_position
    b_vehicle.keyframe_insert(data_path="location", frame=0)
    b_vehicle.animation_data_clear()

    vehicle = Vehicle(init_position, 0)
    vehicle.speed(3)
    vehicle.turn(90)
    #vehicule.turn(87)
    vehicle.forward()


    frames = range(1, TOTAL_FRAMES)
    for f in frames:
        # On vient lire le frame actuel
        bpy.context.scene.frame_set(f)

        # On déplace le véhicule
        b_vehicle.location = vehicle.update()
        b_vehicle.rotation_euler.z = vehicle._heading

        # On ajout un keyframe
        b_vehicle.keyframe_insert(data_path="location", frame=f)
        b_vehicle.keyframe_insert("rotation_euler", frame=f)

        if f == 20:
            vehicle.turn(80)
#        if f == 50:
#            vehicle.backward()
        #if f == 120:
        #    vehicule.speed(5)
        #if f == 200:
        #    vehicule.forward() 


if __name__ == "__main__":
    simulate()
