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

def simuler():
    # init conditions
    location = [0,0,0.025]
    # Timestamp
    print("Début de la simlation à ", datetime.now())

    # On vient placer le véhicule au début à 0,0,0
    b_vehicle = d.objects["Vehicle"]
    bpy.context.scene.frame_set(0)
    b_vehicle.location = location
    b_vehicle.keyframe_insert(data_path="location", frame=0)
    b_vehicle.animation_data_clear()

    vehicle = Vehicle(location, 0)
    vehicle.speed(100)
    vehicle.turn(90)
    #vehicule.turn(87)
    vehicle.forward()


    frames = range(1, TOTAL_FRAMES)
    for f in frames:
        print("Image :", f)
        # On vient lire le frame actuel
        bpy.context.scene.frame_set(f)

        # On déplace le véhicule
        b_vehicle.location = vehicle.update()
        b_vehicle.rotation_euler.z = vehicle._heading

        # On ajout un keyframe
        b_vehicle.keyframe_insert(data_path="location", frame=f)
        b_vehicle.keyframe_insert("rotation_euler", frame=f)

        if f == 10:
            vehicle.speed(80)
        if f == 15:
            vehicle.speed(70)
        if f == 20:
            vehicle.speed(30)
        if f == 25:
            vehicle.speed(100)
        if f == 50:
            vehicle.turn(80)
        if f == 100:
            vehicle.backward()
        #if f == 120:
        #    vehicule.speed(5)
        #if f == 200:
        #    vehicule.forward() 


if __name__ == "__main__":
    simuler()