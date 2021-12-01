'''
********************************************************************
* Filename    : Ultrasonic_Avoidance.py
* Description : A module for SunFounder Ultrasonic Avoidance
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-26    New release
********************************************************************
'''

import RPi.GPIO as GPIO
import time
import math
import numpy as np


class DistanceSensor(object):
    timeout = 0.05

    def __init__(self, channel, avoid_distance=200, log=False):
        self.channel = channel
        self.log = log
        self.avoid_distance = avoid_distance
        GPIO.setmode(GPIO.BCM)

    def distance(self):
        pulse_end = 0
        pulse_start = 0
        GPIO.setup(self.channel, GPIO.OUT)
        GPIO.output(self.channel, False)
        time.sleep(0.06)
        GPIO.output(self.channel, True)
        time.sleep(0.00001)
        GPIO.output(self.channel, False)
        GPIO.setup(self.channel, GPIO.IN)

        timeout_start = time.time()
        while GPIO.input(self.channel) == 0:
            pulse_start = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1
        while GPIO.input(self.channel) == 1:
            pulse_end = time.time()
            if pulse_start - timeout_start > self.timeout:
                return -1

        if pulse_start != 0 and pulse_end != 0:
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 1000 * 343.0 / 2
            distance = int(distance)
            if distance >= 0:
                return distance
            else:
                return -1
        else:
            return -1

    def apply_linear_regression(self, distance):
        corrected_distance = 1.0038 * distance + 41.938

        if self.log:
            print(f'corrected distance : {corrected_distance}')

        return corrected_distance

    def remove_aberrations(self, distances):
        mean = np.mean(distances)
        std = np.std(distances)
        diff_arr = np.abs(distances - mean)
        kept_distances_idx = diff_arr < std
        ket_distances = distances[kept_distances_idx]
        if self.log:
            print(f'distance array without aberrations : {ket_distances}')
        return ket_distances

    def calculate_mean_distance(self, mount=8):
        distances = np.array([])
        while len(distances) <= mount:
            distance = self.distance()
            if distance > 0 and not (74 <= distance <= 76):
                distances = np.append(distances, distance)
            if self.log:
                print(f'current distance:  {distance}')
                print(f'distance array : {distances}')
        valid_distances = self.remove_aberrations(distances)
        return np.mean(valid_distances)

    def get_corrected_distance(self):
        mean_distance = self.calculate_mean_distance()
        return self.apply_linear_regression(mean_distance)

    def should_avoid(self, distance):
        should_avoid = distance <= self.avoid_distance
        if self.log:
            print(f"should avoid ? : {should_avoid}")
        return should_avoid

    def calibrate(self):
        input("Appuyer sur une touche...")
        distance = self.calculate_mean_distance()
        print(f"La distance mesurée est : {distance}")