import time
from distance_sensor import DistanceSensor
from line_follower import LineFollower
from picar import vehicle
from picar import back_wheels
from math import degrees


def race(timeout, log=False, calibrate = False):
    bw = back_wheels.Back_Wheels()
    v = vehicle.Vehicle()
    bw.forward()
    v.turn_straight()
    bw.speed(0,0)
    line_follower = LineFollower()
    
    time_elapsed = 0
    is_race_over = False  # we should somehow get the information when we find the finish line (T shape)
    distance_sensor = DistanceSensor(channel=20, log=log)


    if(calibrate):
        line_follower.calibrate(v)
    input("Ready...set...")
    bw.speed(80,80)
    start_time = time.time()
    while time_elapsed < timeout and not is_race_over:
        time_elapsed = time.time() - start_time
        closest_obstacle_distance = distance_sensor.get_corrected_distance()
        is_race_over =  line_follower.is_race_over()
        if log:
            print(f'closest obstacle distance : {closest_obstacle_distance}')
            print(f'Car racing, time elapsed : {time_elapsed}')
        angle = line_follower.get_angle_to_turn()
        v.turn(90-degrees(angle))
    bw.speed(0,0)
    return time_elapsed

if __name__ == '__main__':
    calibrate = False
    
        
    log_main = True
    race_timeout = 60  # seconds
    race_time = race(timeout=race_timeout, log=log_main, calibrate=calibrate)
    if log_main:
        print(f'Race over, time elapsed : {race_time}, timeout exceeded? : {race_time > race_timeout}')