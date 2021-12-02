import numpy as np
from Line_Follower_Lib import Line_Follower
import time

class LineFollower():

    def __init__(self):
        self.last_angle = 0
        self.lf = Line_Follower()
        self.count_zeros=0
        try:
            self.lf.references = np.load("references_lf.npy")
        except:
            print("Could not find references_lf.npy")

    def lf_read_digital(self):
        return self.lf.read_digital()

    def is_over_line(self):
        if np.any(self.lf_read_digital()):
            return True
        else:
            return False

    def is_race_over(self):
        return np.count_nonzero(self.lf_read_digital()) >= 4

    def get_angle_to_turn(self):
        read = self.lf_read_digital()
        print(read)

        if read == [0, 0, 0, 0, 0]:
            self.count_zeros += 1
            if self.count_zeros>=60:
                angle = np.sign(self.last_angle) * 45
            else:
                angle = self.last_angle
        else:
            self.count_zeros = 0
            angle = (2 - np.mean(np.nonzero(read))) * -45 / 2

        self.last_angle = angle

        print("Angle: ", angle)
        return angle

    def calibrate(self, vehicle):
        references = [0, 0, 0, 0, 0]
        input("cali for module:\n  first put all sensors on white, then put all sensors on black")
        mount = 100
        vehicle.turn(70)
        print("\n cali white")
        vehicle.turn(90)
        white_references = self.lf.get_average(mount)
        vehicle.turn(95)
        time.sleep(0.5)
        vehicle.turn(85)
        time.sleep(0.5)
        vehicle.turn(90)
        time.sleep(1)

        vehicle.turn(110)
        input("\n cali black")
        vehicle.turn(90)
        black_references = self.lf.get_average(mount)
        vehicle.turn(95)
        time.sleep(0.5)
        vehicle.turn(85)
        time.sleep(0.5)
        vehicle.turn(90)
        time.sleep(1)

        for i in range(0, 5):
            references[i] = (white_references[i] + black_references[i]) / 2
        self.lf.references = references
        print("Middle references =", references)
        time.sleep(1)
        np.save("references_lf.npy", references)