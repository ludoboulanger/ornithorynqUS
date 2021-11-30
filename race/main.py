import time
from distance_sensor import DistanceSensor
from line_follower import LineFollower
from vehicle import vehicle
from back_wheels import Back_Wheels
from math import degrees


def race(timeout, log=False, calibrate = False):
    bw = Back_Wheels()
    vehicle = vehicle()
    bw.forward()
    vehicle.turn_straight()
    bw.speed(20)
    line_follower = LineFollower()
    start_time = time.time()
    time_elapsed = 0
    is_race_over = False  # we should somehow get the information when we find the finish line (T shape)
    distance_sensor = DistanceSensor(channel=20, log=log)


    if(calibrate):
        line_follower.calibrate(vehicle)

    while time_elapsed < timeout and not is_race_over:
        time_elapsed = time.time() - start_time
        closest_obstacle_distance = distance_sensor.get_corrected_distance()
        is_race_over =   line_follower.is_race_over()
        if log:
            print(f'closest obstacle distance : {closest_obstacle_distance}')
            print(f'Car racing, time elapsed : {time_elapsed}')
        angle = line_follower.get_angle_to_turn()
        vehicle.turn(degrees(angle)+90)
    bw.speed(0)
    return time_elapsed


if __name__ == '__main__':
    calibrate = True
        
    log_main = True
    race_timeout = 10  # seconds
    race_time = race(timeout=race_timeout, log=log_main, calibrate=calibrate)
    if log_main:
        print(f'Race over, time elapsed : {race_time}, timeout exceeded? : {race_time > race_timeout}')