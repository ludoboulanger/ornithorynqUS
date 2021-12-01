from distance_sensor import DistanceSensor
from line_follower import LineFollower
from picar import vehicle
from enum import Enum

class States(Enum):
    FOLLOW = 1
    AVOID = 2
    DONE = 3

class FlashMcQueen:

    ACCELERATION_RATE = 0.01
    MAX_BACKWARD_DIST = 30

    def __init__(self, avoid_distance):
        self.distance_sensor = DistanceSensor(channel=20)
        self.line_follower = LineFollower()
        self.vehicle = vehicle.Vehicle()
        self.avoid_distance = avoid_distance

        # Init variables
        self.time_elapsed = 0
        self.race_over = False
        self.current_state = States.FOLLOW

    def read_distance(self):
        return self.distance_sensor.get_corrected_distance()
    
    def should_avoid_obstacle(self):
        distance = self.read_distance()
        should_avoid = distance <= self.avoid_distance
        self.current_state = States.AVOID
        return should_avoid

    def calibrate_line_follower(self):
        self.line_follower.calibrate(self.vehicle)

    def follow_line(self):
        angle = self.line_follower.get_angle_to_turn()
        diff_angle = angle - self.vehicle._wheel_angle
        self.vehicle.turn(90 - self.vehicle._wheel_angle + diff_angle * 0.5)

    def forward(self):
        self.vehicle.forward()

        if self.should_avoid_obstacle():
            self.current_state = States.AVOID

        self.follow_line()

    def backward(self):
        self.vehicle.backward()
        self.follow_line()

    def accelerate(self, percent, rate=0.01):
        # Need to read distances to make sure we can keep going
        if self.should_avoid_obstacle():
            return

        if self.current_speed < percent:
            self.current_speed += rate
            self.vehicle.speed(int(self.current_speed))

    def deccelerate(self, percent, rate=0.01):
        # Need to read distances to make sure we can keep going
        if self.should_avoid_obstacle():
            return

        if self.current_speed > percent:
            self.current_speed -= rate
            self.vehicle.speed(int(self.current_speed))

    def dodge_obstacle(self):
        self.vehicle.stop()

        # Backup to desired distance
        while self.read_distance() < self.MAX_BACKWARD_DIST:
            self.backward()

        # Dodge sequence
        


    def race(self):
        while not self.race_over:
            pass

    
