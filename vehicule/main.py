import vehiculesim as v
import time
import _thread

if __name__ == "__main__":
    try:
        vehicule = v.vehiculesim(30, [0, 0, 0], 0)
        vehicule.speed(0.18)
        vehicule.turn_straight()
        vehicule.forward()
        for i in range(30): # Pour 90 frames (3 secondes)
            vehicule.update()
            time.sleep(1/30)
        vehicule.stop()
        for i in range(30): # Pour 90 frames (3 secondes)
            vehicule.update()
            time.sleep(1/30)
        vehicule.turn(45)
        vehicule.plot()

    except:
        print("Échec")
