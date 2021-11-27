import bpy
import mathutils
import math
from statistics import mean
from bpy import data as d
from math import pi
from mathutils import Vector
from math import radians

LF_SENSORS = ["Capteur.002", "Capteur.001", "Capteur", "Capteur.003", "Capteur.004"]
SENSOR = d.objects["CapteurDistance"]
LINE = "Plane.001"
CAR = "Voiture"

FRAME_NUM = 900


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
            angle = (mean([i for i, n in enumerate(read) if n == 1]) - 2) * -2
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
    start_pos = (0, 0, 0.025)
    start_angle = (0, 0, math.pi / 18)

    car = bpy.data.objects.get(CAR)
    car.select_set(True)
    car.animation_data_clear()
    car.location = start_pos
    car.rotation_euler = start_angle

    return car


def animate_frame(frame_num, car, angle, move_step=0.001):
    print("FRAME :: ", frame_num)
    bpy.context.scene.frame_set(frame_num)

    car.rotation_euler.z += angle

    # Rotate the move vector, to have it in the direction facing the car
    move = mathutils.Vector((move_step, 0, 0))
    inv = car.matrix_world.copy()
    inv.invert()
    vec_rot = move @ inv

    car.location += vec_rot

    bpy.ops.anim.keyframe_insert(type='LocRotScale')


def main():
    car = init_car()
    distance_sensor = DistanceSensor(vehicule=car, sensor=SENSOR)
    line_follower = LineFollower(sensors_names=LF_SENSORS, line_name=LINE)

    for i in range(FRAME_NUM):
        obstacle_distance, name = distance_sensor.get_raw_distance(debug=True)
        if should_stop(distance=obstacle_distance):
            break
        else:
            angle = line_follower.get_angle_to_turn()
            animate_frame(frame_num=i, car=car, angle=angle)


if __name__ == '__main__':
    main()
    print("Done")
