from matplotlib import pyplot as plt
from math import sin, cos, asin, sqrt, exp

ROTATION_RADIUS = 0.140
DAMP = 1
G = 9.81
Z = sqrt(G / ROTATION_RADIUS)

TOTAL_FRAMES = 300
FRAME_RATE = 30
TIME = 1 / FRAME_RATE


class Marble:

    def __init__(self, x=0.0, y=0.0, z=0.0, accel=0.0):
        self.x = x
        self.y = y
        self.z = z

        self.alpha = 0
        self.omega = 0
        self.theta = asin(sqrt(x ** 2 + z ** 2))

        self.init_theta = self.theta
        self.init_omega = self.omega

        self.accel = accel
        self.rel_time = 0

    def get_cartesian_position(self):
        return self.x, self.y, self.z

    def update_cartesian_position(self, angle):
        linear_displacement = ROTATION_RADIUS * sin(self.theta)
        self.x = linear_displacement * cos(angle)
        self.y = linear_displacement * sin(angle)

    def compute_theta(self):
        damping_factor = exp(-DAMP * self.rel_time)
        C = -self.accel / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        pos = A * cos(Z * self.rel_time) + \
              B * cos(Z * self.rel_time) + C / Z ** 2

        return damping_factor * pos

    def compute_omega(self):
        damping_factor = exp(-DAMP * self.rel_time)
        C = -self.accel / ROTATION_RADIUS

        A = self.init_theta - C / Z ** 2
        B = self.init_omega / Z

        pos = A * cos(Z * self.rel_time) + B * cos(Z * self.rel_time) + C / Z ** 2
        vel = -A * sin(Z * self.rel_time) * Z + B * cos(Z * self.rel_time) * Z

        return vel * damping_factor + -DAMP * damping_factor * pos

    def simulate(self):
        if self.rel_time == TIME:
            self.init_omega = self.omega
            self.init_theta = self.theta

        self.theta = self.compute_theta()
        self.omega = self.compute_omega()
        self.rel_time += TIME

    def set_accel(self, accel, angle=0.0):
        self.accel = accel
        self.rel_time = TIME


if __name__ == "__main__":
    marble = Marble(accel=0.1)
    positions = []
    velocities = []

    for i in range(TOTAL_FRAMES):
        if i == 12:
            marble.set_accel(0)

        if i == 80:
            marble.set_accel(-0.1)

        if i == 92:
            marble.set_accel(0)

        marble.simulate()
        positions.append(marble.theta)
        velocities.append(marble.omega)

    plt.figure()
    plt.plot(positions)

    plt.figure()
    plt.plot(velocities)
    plt.show()
