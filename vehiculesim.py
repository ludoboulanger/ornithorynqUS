# Librairie pour simuler le véhicule du projet S5i
# Simulation dans blender

class vehiculesim:

    coordinates = [0, 0, 0] # Coordonnées du véhicule
    framelength = 0 # Longueur d'un frame, donc le t dans les calculs
    heading = 0 # Cap du véhicule en radians
    vitesse = 0 # Vitesse du véhicule actuelle en m/s
    acceleration = 0 # Accélération du véhicule actuelle, en m/s2

    def __init__(self, framerate, coordinates, heading):
        self.framelength = 1/framerate # On simule à 30 FPS
        self.coordinates = coordinates
        self.heading = heading

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

    # Avancer
    # Simule la fonction d'avancer le véhicule en ligne droite selon son cap
    def avancer(self, vitesse):
        self.vitesse = vitesse

        coord = self.coordinates
        heading = self.heading
        interval = self.framelength





