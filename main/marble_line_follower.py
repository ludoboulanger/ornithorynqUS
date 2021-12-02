import bpy
import mathutils
from statistics import mean
from bpy import data as d
from mathutils import Vector
import numpy as np
import datetime

LF_SENSORS = ["Capteur.002", "Capteur.001", "Capteur", "Capteur.003", "Capteur.004"]
SENSOR = d.objects["DistanceSensor"]
LINE = "Plane"
CAR = "Vehicle"
MARBLE = "Marble"
OBSTACLE= "Cube"
FRAME_NUM = 1000
FRAMERATE = 30 # Framerate
TIME = 1 / FRAMERATE
DISTANCE_WHEELS = 0.14 # 14cm d'empattement
DISTANCE_STOP=0.2 #200 mm
TURN_ANGLE = 20

ACCELERATIONFACTOR = 1.8
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
        print(f"Theta {self.theta}")
        linear_displacement = ROTATION_RADIUS * np.sin(self.theta)
        print(f"linear_displacement {linear_displacement}")
        self.x = linear_displacement[0]
        self.y = linear_displacement[1] 
        # self.z = MARBLE_R + CONTAINER_HEIGHT + ROTATION_RADIUS*(1 - cos(self.theta))
        
    def set_acceleration(self, accel, angle=0.0):
        self.alpha = np.array([accel * np.cos(angle), accel * np.sin(angle)])
        
        print("Setting Acceleration :: ", self.alpha, "Angle :: ", angle)

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
        acceleration_angle = np.radians(self._heading)

        # print("Accélération à: ", self._acceleration)

        # Calcul du cap
        circon = np.abs(self.angle_to_radius(self._wheel_angle)) * 2 * np.pi
        print("CIRCONFERENCE: ", circon)
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
            
            print("WHEEL ANGLE :: ", self._wheel_angle)
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

            # if self._heading > np.pi/2 and self._heading < 3*np.pi/2:
            #     acceleration_angle *= -1

        print("HEADING ::", self._heading)

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
            print("Stop: ", self._coordinates)
        else:
            print("Erreur, état invalide")

        # On met à jour l'ancienne vitesse
        self._prev_speed = self._speed

        # Simule le mouvement de la bille

        if car_acceleration == 0:
            acceleration_angle = 0
        self._marble.set_acceleration(car_acceleration, angle=acceleration_angle)
        self._marble.simulate()
        return self._coordinates

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
            angle = self.last_angle
        else:
            angle = (2 - np.mean(np.nonzero(read))) * 90/3
        self.last_angle = angle
 
        return np.radians(angle)


def animate_frame(frame_num, car, blender_car, blender_marble):
    bpy.context.scene.frame_set(frame_num)
    print(f"\n***********FRAME_NUM: {frame_num}******************")
    
    # Calcule nouvelle position de la bille
    blender_marble.location = car.get_marble_position(car._heading)
    
    # On déplace le véhicule
    blender_car.location = car.update()
    blender_car.rotation_euler.z = car._heading

    # On ajout un keyframe
    blender_car.keyframe_insert(data_path="location", frame=frame_num)
    blender_car.keyframe_insert("rotation_euler", frame=frame_num)
    blender_marble.keyframe_insert(data_path="location", frame=frame_num)

def init_car():
    start_pos = [-0.3, 0, 0.025]
    start_angle = (0, 0, np.pi / 18)

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

def modif_speed(f, car):

    if f == 40:
        car.speed(80)
    
    if f == 160:
        car.speed(30)

    if f == 520:
        car.speed(80)

    if f == 580:
        car.speed(30)
    
    if f == 850:
        car.speed(70)


def main():
    car, blender_car = init_car()
    blender_marble = init_marble()
    line_follower = LineFollower(sensors_names=LF_SENSORS, line_name=LINE)

    animate_frame(frame_num=0, car=car, blender_car=blender_car, blender_marble=blender_marble)

    for i in range(1, FRAME_NUM):
        angle = line_follower.get_angle_to_turn()
        car.turn(np.degrees(angle)+90)
        animate_frame(frame_num=i, car=car, blender_car=blender_car, blender_marble=blender_marble)

        # modif_speed(i, car)


if __name__ == "__main__":
    main()
    print("DONE")