from distance_sensor import DistanceSensor
from line_follower import LineFollower
from picar import vehicle
from enum import Enum

class States(Enum):
    FOLLOW = 1
    AVOID = 2
    DONE = 3

class FlashMcQueen:

    def __init__(self, avoid_distance):
        self.distance_sensor = DistanceSensor(channel=20)
        self.line_follower = LineFollower()
        self.vehicle = vehicle.Vehicle()
        self.avoid_distance = avoid_distance

        # Init variables
        self.time_elapsed = 0
        self.race_over = False
        self.current_state = States.FOLLOW

    def should_avoid_obstacle(self, distance):
        should_avoid = distance <= self.avoid_distance
        return should_avoid

    def calibrate_line_follower(self):
        self.line_follower.calibrate(self.vehicle)

    def follow_line_forward(self):
        pass

    def follow_line_backward(self):
        pass

    def dodge_obstacle_right(self):
        pass

    def dodge_obstacle_left(self):
        pass

    def race(self):
        pass

    
