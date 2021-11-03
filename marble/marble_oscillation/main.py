from matplotlib import pyplot as plt
from math import sin, cos, asin, sqrt, exp

ROTATION_RADIUS = 0.140
DAMP = 1
G = 9.81
Z = sqrt(G / ROTATION_RADIUS)
CONTAINER_HEIGHT = 0.0085
MARBLE_R = 0.005

TOTAL_FRAMES = 300
FRAME_RATE = 30
TIME = 1 / FRAME_RATE


class Marble:

    def __init__(self, x=0.0, y=0.0, z=0.0, accel=0.0):
        self.x = x
        self.y = y
        self.z = z

        self.alpha = accel
        self.alpha_angle = 0
        self.omega = 0
        self.theta = asin(sqrt(x ** 2 + y ** 2) / ROTATION_RADIUS)

        self.init_theta = self.theta
        self.init_omega = self.omega

        self.rel_time = 0

    def get_cartesian_position(self):
        return self.x, self.y, self.z

    def update_cartesian_position(self):
        linear_displacement = ROTATION_RADIUS * sin(self.theta)
        self.x = linear_displacement * cos(self.alpha_angle)
        self.y = linear_displacement * sin(self.alpha_angle)
        self.z = MARBLE_R + CONTAINER_HEIGHT + ROTATION_RADIUS * \
                 (1 - cos(self.theta))

    def compute_raw_position(self):
        C = -self.alpha / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        return A * cos(Z * self.rel_time) + \
               B * sin(Z * self.rel_time) + C / Z ** 2

    def compute_raw_velocity(self):
        C = -self.alpha / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        return -A * sin(Z * self.rel_time) * Z + B * cos(Z * self.rel_time) * Z

    def compute_theta(self):
        damping_factor = exp(-DAMP * self.rel_time)

        raw_position = self.compute_raw_position()

        return damping_factor * raw_position

    def compute_omega(self):
        damping_factor = exp(-DAMP * self.rel_time)

        raw_position = self.compute_raw_position()
        raw_velocity = self.compute_raw_velocity()

        return raw_velocity * damping_factor + -DAMP * damping_factor * raw_position

    def simulate(self):
        if self.rel_time == TIME:
            self.init_omega = self.omega
            self.init_theta = self.theta

        self.theta = self.compute_theta()
        self.omega = self.compute_omega()

        self.update_cartesian_position()
        self.rel_time += TIME

    def set_accel(self, accel, angle=0.0):
        self.alpha = accel
        self.alpha_angle = angle
        self.rel_time = TIME


if __name__ == "__main__":
    marble = Marble(accel=1.3)
    positions = []
    velocities = []

    for i in range(TOTAL_FRAMES):
        if i == 15:
            marble.set_accel(0)

        # if i == 80:
        #     marble.set_accel(-1.3)
        #
        # if i == 92:
        #     marble.set_accel(0)

        marble.simulate()
        positions.append(marble.theta)
        velocities.append(marble.omega)

    plt.figure()
    plt.plot(positions)

    plt.figure()
    plt.plot(velocities)
    plt.show()
