import time
from distance_sensor import DistanceSensor
from line_follower import LineFollower
from picar import vehicle
from math import degrees
import math
from enum import Enum
import asyncio
import RPi.GPIO as GPIO


class States(Enum):
    OBSTACLE_APPROACHING = 1
    OBSTACLE_WAITING = 2
    OBSTACLE_BACKWARD = 3
    OBSTACLE_TURN = 4
    OBSTACLE_FIND_LINE = 5
    FOLLOW_LINE = 6

AVOID_DISTANCE = 100
BACKWARD_DISTANCE = 300
BACKWARD_SPEED = 50
CRUISE_SPEED = 80
DISTANCE_WHEELS = 0.14 # 14cm d'empattement
FIND_LINE_ANGLE = 30
SLOW_SPEED = 40
TURN_ANGLE = 15
TURN_SPEED = 50
WAIT_TIME = 5



def race(v, timeout, log=False, calibrate=False):
    # Initialize car and sensors
    v.forward()
    v.turn_straight()
    v.stop()
    line_follower = LineFollower()
    distance_sensor = DistanceSensor(channel=16, avoid_distance=AVOID_DISTANCE, log=log)

    # Init variables
    time_elapsed = 0
    is_race_over = False  # we should somehow get the information when we find the finish line (T shape)
    current_state = States.FOLLOW_LINE

    if calibrate:
        line_follower.calibrate(v)
    input("Ready...set...")
    v.speed(CRUISE_SPEED)
    start_time = time.time()
    count = 0
    while time_elapsed < timeout and not is_race_over:
        # count+=1
        time_elapsed = time.time() - start_time
        if(current_state == States.FOLLOW_LINE):
            print(f"------------------Current state : {current_state}---------------")
            closest_obstacle_distance = distance_sensor.get_corrected_distance()
            if closest_obstacle_distance > 0:
                if distance_sensor.should_slow_down(closest_obstacle_distance):
                    v.speed(SLOW_SPEED)
                if distance_sensor.should_avoid(closest_obstacle_distance):
                    current_state = States.OBSTACLE_WAITING
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

        elif(current_state == States.OBSTACLE_WAITING):
            print(f"------------------Current state : {current_state}---------------")
            v.stop()
            time.sleep(WAIT_TIME)
            current_state = States.OBSTACLE_BACKWARD
        elif(current_state == States.OBSTACLE_BACKWARD):
            print(f"------------------Current state : {current_state}---------------")
            v.backward()
            v.turn_straight()
            v.speed(50)
            if closest_obstacle_distance >= BACKWARD_DISTANCE:
                current_state = States.OBSTACLE_TURN
        elif(current_state == States.OBSTACLE_TURN):
            print(f"------------------Current state : {current_state}---------------")
            time_in_turn = math.sqrt(0.3**2+(DISTANCE_WHEELS/2)**2)/(v._speed)        
            v.forward()
            v.speed(TURN_SPEED)   
            v.turn(90+TURN_ANGLE)
            time.sleep(time_in_turn)
            current_state = States.OBSTACLE_FIND_LINE
        elif(current_state == States.OBSTACLE_FIND_LINE):
            print(f"------------------Current state : {current_state}---------------")
            v.turn(90-FIND_LINE_ANGLE)
            if line_follower.is_over_line():
                current_state= States.FOLLOW_LINE    
    v.stop()
    # print(count)
    return time_elapsed


if __name__ == '__main__':
    v = vehicle.Vehicle()
    try: 
        calibrate = False
        log_main = True
        race_timeout = 80  # seconds
        race_time = race(v, timeout=race_timeout, log=log_main, calibrate=calibrate)
        if log_main:
            print(f'Race over, time elapsed : {race_time}, timeout exceeded? : {race_time > race_timeout}')
    except:
        pass

    v.stop()
    GPIO.cleanup()
        