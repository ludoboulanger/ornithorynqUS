import time
import bpy
from bpy import data as d
import math

coord = [0, 0, 0]
a = "AAAAAAAAAAAAAAAa"

class vehiculesim:

    _coordinates = [0, 0, 0] # Coordonnées du véhicule
    _framelength = 0 # Longueur d'un frame, donc le t dans les calculs
    _heading = 0 # Cap du véhicule en radians
    _vitesse = 0 # Vitesse du véhicule actuelle en m/s
    _angleroues = math.pi/2 # Angle des roues, 90 degrés est le centre
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
    def anglearayon(self, angle):
        rayon = 0.2 # mètres
        return rayon

    def speed(self, vitesse):
        self._vitesse = vitesse

    # Mettre les roues droites
    def turn_straight(self):
        self._angleroues = math.radians(90-90)

    # Tourner à un angle, en degrés. 90 est tout droit.
    def turn(self, angle):
        self._angleroues = math.radians(90-angle)

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
        circon = self.anglearayon(self._angleroues) * 2 * math.pi
        if self._state == 1:
            distanceframe = self._vitesse * self._framelength
            self._heading = self._heading + ((distanceframe/circon) * 2 * math.pi)
        elif self._state == 2:
            distanceframe = -1 * self._vitesse * self._framelength
            self._heading = self._heading - ((distanceframe/circon) * 2 * math.pi)

        # Déplacement
        if self._state == 1:
            self._coordinates[0] = self._coordinates[0] + (self._vitesse * self._framelength * math.cos(self._heading))
            self._coordinates[1] = self._coordinates[1] + (self._vitesse * self._framelength * math.sin(self._heading))
            print("Avancer: ", self._coordinates)
        elif self._state == 2:
            self._coordinates[0] = self._coordinates[0] + (self._vitesse * self._framelength * math.cos(self._heading + math.pi))
            self._coordinates[1] = self._coordinates[1] + (self._vitesse * self._framelength * math.sin(self._heading + math.pi))
            print("Reculer: ", self._coordinates)
        elif self._state == 0:
            print("Stop: ", self._coordinates)
        else:
            print("Erreur, état invalide")

        coord = self._coordinates

        return self._coordinates
    
def framehandler(scene):
    #d.objects["Cube"].location = vehicule.update()
    print(a)


if __name__ == "__main__":
    print("Simulation démarre")
    vehicule = vehiculesim(30, [0, 0, 0], 0)
    bpy.app.handlers.frame_change_post.append(framehandler)
    bvehicule = d.objects["Cube"]
    vehicule.speed(0.18)
    vehicule.turn_straight()
    vehicule.forward()
    time.sleep(5)
    vehicule.stop()
