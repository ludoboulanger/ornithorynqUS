import time
from datetime import datetime
import bpy
from bpy import data as d
import numpy as np

FRAMERATE = 30 # Framerate
TIME = 1 / FRAMERATE
TOTAL_FRAMES = 250 # nombre de frames à simuler
DISTANCE_WHEELS = 0.14 # 14cm d'empattement

ROTATION_RADIUS = 0.14
CONTAINER_HEIGHT = 0.0085 # 10mm - 1.5mm concavity
MARBLE_MASS = 0.0052
MARBLE_R = 0.005
G = 9.810
DAMP = 1
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
        print("Setting Acceleration :: ", accel)
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

    def get_marble_position(self):
        return self._marble.get_cartesian_position()

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
           self._acceleration = -794.171873034486*np.power(diff_speed, 3)\
                + 281.9660606932039*np.power(diff_speed, 2)\
                - 0.414200251036732*diff_speed\
                - 0.6495715769694956
       elif diff_speed < 0: # Décélération, on assume l'inverse de l'accélération
           diff_speed = np.abs(diff_speed)
           self._acceleration = -1*(-794.171873034486*np.power(diff_speed, 3)\
                + 281.9660606932039*np.power(diff_speed, 2)
                - 0.414200251036732*diff_speed\
                - 0.6495715769694956)
       else:
           self._acceleration = 0

    # Ajuste la vitesse du robot, équivalent à la librairie du robot
    def speed(self, percent):
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
        if circon > 0 and self._is_turning:
            car_acceleration = 10 * self._speed**2 / np.abs(self.angle_to_radius(self._wheel_angle))
            print("Angle :: ", self.angle_to_radius(self._wheel_angle))
            if self._state == 1:
                distanceframe = self._speed * TIME
            elif self._state == 2:
                distanceframe = -1 * self._speed * TIME
            else:
                distanceframe = 0
                
            if self._wheel_angle >= 0:
                self._heading = self._heading - ((distanceframe/circon) * 2 * np.pi)
                acceleration_angle = np.radians(self._heading - 90)
            else:
                self._heading = (self._heading) + ((distanceframe/circon) * 2 * np.pi)
                acceleration_angle = np.radians(self._heading + 90)

        # print("Cap:", self._heading)

        # Déplacement
        if self._state == VEHICLE_STATES['FORWARD']:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading))
            # print("Avancer: ", self._coordinates)
        elif self._state == 2:
            self._coordinates[0] = self._coordinates[0] + (self._speed * TIME * np.cos(self._heading + np.pi))
            self._coordinates[1] = self._coordinates[1] + (self._speed * TIME * np.sin(self._heading + np.pi))
            # print("Reculer: ", self._coordinates)
        elif self._state == 0:
            # car_acceleration = self._speed / TIME
            print("Stop: ", self._coordinates)
        else:
            print("Erreur, état invalide")

        # On met à jour l'ancienne vitesse
        self._prev_speed = self._speed

        # Simule le mouvement de la bille
        self._marble.set_acceleration(car_acceleration, angle=acceleration_angle)
        self._marble.simulate()
        return self._coordinates

def simuler():
    # init conditions
    location = [0,0,0.025]
    vehicle = Vehicle(location, 0)
    
    # Timestamp
    print("Début de la simlation à ", datetime.now())

    # On vient placer le véhicule au début à 0,0,0
    b_vehicle = d.objects["Vehicle"]
    b_marble = d.objects['Marble']
    b_vehicle.animation_data_clear()
    b_marble.animation_data_clear()
    
    bpy.context.scene.frame_set(0)
    b_vehicle.location = location
    b_marble.location = vehicle.get_marble_position()
    b_vehicle.keyframe_insert(data_path="location", frame=0)
    b_marble.keyframe_insert('location', frame=0)

    vehicle.speed(100)
    vehicle.turn_straight()
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
        b_marble.location = vehicle.get_marble_position()

        # On ajout un keyframe
        b_vehicle.keyframe_insert(data_path="location", frame=f)
        b_vehicle.keyframe_insert("rotation_euler", frame=f)
        b_marble.keyframe_insert('location', frame=f)

        if f == 40:
            vehicle.turn(80)
#        if f == 15:
#            vehicle.speed(70)
#        if f == 20:
#            vehicle.speed(30)
#        if f == 25:
#            vehicle.speed(100)
#        if f == 30:
#            vehicle.turn(80)
        if f == 80:
            vehicle.stop()
#        if f == 120:
#            vehicle.speed(100)
        #if f == 200:
        #    vehicule.forward() 


if __name__ == "__main__":
    simuler()