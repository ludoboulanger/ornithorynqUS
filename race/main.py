import time
from distance_sensor import DistanceSensor


def race(timeout, log=False):
    start_time = time.time()
    time_elapsed = 0
    is_race_over = False  # we should somehow get the information when we find the finish line (T shape)
    distance_sensor = DistanceSensor(channel=20, log=log)
    while time_elapsed < timeout and not is_race_over:
        time_elapsed = time.time() - start_time
        closest_obstacle_distance = distance_sensor.get_corrected_distance()
        is_race_over = distance_sensor.should_avoid(closest_obstacle_distance)  # for testing purposes
        if log:
            print(f'closest obstacle distance : {closest_obstacle_distance}')
            print(f'Car racing, time elapsed : {time_elapsed}')
    return time_elapsed


if __name__ == '__main__':
    log_main = False
    race_timeout = 10  # seconds
    race_time = race(timeout=race_timeout, log=log_main)
    if log_main:
        print(f'Race over, time elapsed : {race_time}, timeout exceeded? : {race_time > race_timeout}')