from distance_sensor import DistanceSensor
from line_follower import LineFollower
from picar import vehicle

class FlashMcQueen:

    def __init__(self):
        self.distance_sensor = DistanceSensor()
        self.line_follower = LineFollower()
        self.vehicle = vehicle.Vehicle()

    def follow_line_forward(self):
        pass

    def follow_line_backward(self):
        pass

    def dodge_obstacle_right(self):
        pass

    def dodge_obstacle_left(self):
        pass

    
