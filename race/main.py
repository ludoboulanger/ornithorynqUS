import time
from distance_sensor import DistanceSensor
from line_follower import LineFollower
from picar import vehicle
from math import degrees
from enum import Enum
import asyncio


class States(Enum):
    FOLLOW = 1
    AVOID = 2
    DONE = 3


def race(timeout, log=False, calibrate=False):
    # Initialize car and sensors
    v = vehicle.Vehicle()
    v.forward()
    v.turn_straight()
    v.stop()
    line_follower = LineFollower()
    distance_sensor = DistanceSensor(channel=5, avoid_distance=100, log=log)
    cruise_speed = 80;
    slow_speed = 40;

    # Init variables
    time_elapsed = 0
    is_race_over = False  # we should somehow get the information when we find the finish line (T shape)
    current_state = States.FOLLOW

    if calibrate:
        line_follower.calibrate(v)
    input("Ready...set...")
    v.speed(cruise_speed)
    start_time = time.time()
    count = 0
    while time_elapsed < timeout and not is_race_over:
        # count+=1
        time_elapsed = time.time() - start_time
        closest_obstacle_distance = distance_sensor.get_corrected_distance()
        if closest_obstacle_distance > 0:
            if distance_sensor.should_slow_down(closest_obstacle_distance):
                v.speed(slow_speed)
            if distance_sensor.should_avoid(closest_obstacle_distance):
                current_state = States.AVOID
                v.stop()  # instead of stopping, we should avoid obstacle
                # call avoid function here or while loop
                break  # remove when avoid is implemented

        is_race_over = line_follower.is_race_over()
        # if log:
        # print(f'closest obstacle distance : {closest_obstacle_distance}')
        # print(f'Car racing, time elapsed : {time_elapsed}')
        desired_angle = 90 + line_follower.get_angle_to_turn()
        current_angle = 90 - degrees(v._wheel_angle)
        diff = desired_angle - current_angle
        # print(f"Diff {diff} desired_angle {desired_angle} current_angle {current_angle}")
        # print(f"Turning with angle : {current_angle + diff * 0.5}")
        v.turn(current_angle + diff * 0.5)
    current_state = States.DONE
    v.stop()
    # print(count)
    return time_elapsed


if __name__ == '__main__':
    calibrate = False
    log_main = True
    race_timeout = 80  # seconds
    race_time = race(timeout=race_timeout, log=log_main, calibrate=calibrate)
    if log_main:
        print(f'Race over, time elapsed : {race_time}, timeout exceeded? : {race_time > race_timeout}')