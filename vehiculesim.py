# Librairie pour simuler le véhicule du projet S5i
# Simulation dans blender

import math
import _thread

class vehiculesim:

    _coordinates = [0, 0, 0] # Coordonnées du véhicule
    _framelength = 0 # Longueur d'un frame, donc le t dans les calculs
    _heading = 0 # Cap du véhicule en radians
    _vitesse = 0 # Vitesse du véhicule actuelle en m/s
    _acceleration = 0 # Accélération du véhicule actuelle, en m/s2
    _state = 0 # État, 0 = stop, 1 = avancer, 2 = arrêté

    def __init__(self, framerate, coordinates, heading):
        self._framelength = 1 / framerate # On simule à 30 FPS
        self._coordinates = coordinates
        self._heading = heading

    # Retourne le pourcentage nécessaire pour obtenir une certaine vitesse en m/s
    # À utiliser pour le vrai véhicule
    def vitesseapourc(self, vitesse):
        pourcentage = vitesse/5 # TODO changer la vitesse maximale, ce qui devrait nous donner la bonne valeur
        return pourcentage

    # Converti l'angle des roues en rayon de virage en mètres
    # TODO utiliser les vraies valeurs
    def anglearayon(self, angle):
        rayon = 0.2 # mètres
        return rayon

    def speed(self, vitesse):
        self._vitesse = vitesse

    def heading(self, heading):
        self._heading = math.radians(heading)

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
