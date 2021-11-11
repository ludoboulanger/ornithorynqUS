import time
from datetime import datetime
import bpy
from bpy import data as d
import numpy as np

FRAMERATE = 30 # Framerate
TOTAL_FRAMES = 250 # nombre de frames à simuler
EMPATTEMENT = 0.14 # 14cm d'empattement


class vehiculesim:

    _coordinates = [0, 0, 0] # Coordonnées du véhicule
    _framelength = 0 # Longueur d'un frame, donc le t dans les calculs
    _heading = 0 # Cap du véhicule en radians
    _vitesse = 0 # Vitesse du véhicule actuelle en m/s
    _angleroues = np.pi/2 # Angle des roues, 90 degrés est le centre
    _acceleration = 0 # Accélération du véhicule actuelle, en m/s2
    _state = 0 # État, 0 = stop, 1 = avancer, 2 = arrêté

    def __init__(self, framerate, coordinates, heading):
        self._framelength = 1 / framerate # On simule à 30 FPS
        self._coordinatest = coordinates
        self._heading = heading

    # Retourne le pourcentage nécessaire pour obtenir une certaine vitesse en m/s
    # À utiliser pour le vrai véhicule
    def vitesseapourc(self, vitesse):
        pourcentage = vitesse/5 # TODO changer la vitesse maximale, ce qui devrait nous donner la bonne valeur
        return pourcentage

    # Converti l'angle des roues en radians en rayon de virage en mètres
    # TODO utiliser les vraies valeurs
    # Pour l'instant on va utiliser un calcul théorique. Cela assume un cas
    # parfait qui n'est pas réaliste. Un meilleur algo est à faire, basé sur:
    # https://patentimages.storage.googleapis.com/c9/d1/1a/2826ee9a515566/WO2005102822A1.pdf
    def anglearayon(self, angle):
        try:
            print("Angle commandé:", angle)
            if angle <= np.pi/2:
                rayon = EMPATTEMENT/np.tan(angle)
        except:
            print("Erreur de calcul du rayon")
            return 0
        return rayon

    def speed(self, vitesse):
        self._vitesse = vitesse

    # Mettre les roues droites
    def turn_straight(self):
        self._angleroues = np.radians(90-90)

    # Tourner à un angle, en degrés. 90 est tout droit.
    def turn(self, angle):
        if angle >= 0:
            self._angleroues = np.radians(90-angle)

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
        circon = np.abs(self.anglearayon(self._angleroues)) * 2 * np.pi
        print("Circonférence: ", circon)
        print("self._angleroues:", self._angleroues)
        if circon > 0:
            if self._state == 1:
                distanceframe = self._vitesse * self._framelength
            elif self._state == 2:
                distanceframe = -1 * self._vitesse * self._framelength
            if self._angleroues >= 0:
                self._heading = self._heading - ((distanceframe/circon) * 2 * np.pi)
            else:
                self._heading = (self._heading) + ((distanceframe/circon) * 2 * np.pi)


        print("Cap:", self._heading)

        # Déplacement
        if self._state == 1:
            self._coordinates[0] = self._coordinates[0] + (self._vitesse * self._framelength * np.cos(self._heading))
            self._coordinates[1] = self._coordinates[1] + (self._vitesse * self._framelength * np.sin(self._heading))
            print("Avancer: ", self._coordinates)
        elif self._state == 2:
            self._coordinates[0] = self._coordinates[0] + (self._vitesse * self._framelength * np.cos(self._heading + np.pi))
            self._coordinates[1] = self._coordinates[1] + (self._vitesse * self._framelength * np.sin(self._heading + np.pi))
            print("Reculer: ", self._coordinates)
        elif self._state == 0:
            print("Stop: ", self._coordinates)
        else:
            print("Erreur, état invalide")

        return self._coordinates

def simuler():
    # Timestamp
    print("Début de la simlation à ", datetime.now())

    # On vient placer le véhicule au début à 0,0,0
    bvehicule = d.objects["Cube"]
    bpy.context.scene.frame_set(0)
    bvehicule.location = [0,0,0]
    bvehicule.keyframe_insert(data_path="location", frame=0)
    bvehicule.animation_data_clear()

    vehicule = vehiculesim(FRAMERATE, [0, 0, 0], 0)
    vehicule.speed(3)
    vehicule.turn(90)
    #vehicule.turn(87)
    vehicule.forward()


    frames = range(1, TOTAL_FRAMES)
    for f in frames:
        print("Image :", f)
        # On vient lire le frame actuel
        bpy.context.scene.frame_set(f)

        # On déplace le véhicule
        bvehicule.location = vehicule.update()

        # On ajout un keyframe
        bvehicule.keyframe_insert(data_path="location", frame=f)

        if f == 50:
            vehicule.turn(94)
        #if f == 100:
        #    vehicule.backward()
        #if f == 120:
        #    vehicule.speed(5)
        #if f == 200:
        #    vehicule.forward() 


if __name__ == "__main__":
    simuler()
