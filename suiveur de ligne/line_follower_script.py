import bpy
import mathutils
import math

from statistics import mean

############ Setup ############
start_pos = (0,0,0)
start_angle = (0,0,math.pi/32)

ob = bpy.data.objects.get("Suiveur")
ob.select_set(True)
ob.animation_data_clear()
ob.location = start_pos
ob.rotation_mode= 'XYZ'
ob.rotation_euler = start_angle
frame_num = 0

c1 = bpy.data.objects.get("Capteur")
c2 = bpy.data.objects.get("Capteur.001")
c3 = bpy.data.objects.get("Capteur.003")
c4 = bpy.data.objects.get("Capteur.002")
c5 = bpy.data.objects.get("Capteur.004")
line = bpy.data.objects.get("Plane")

capteurs = [c4, c2, c1, c3, c5]

last_angle = 0.0

##### Functions #######
def is_captor_over_line(captor, line):
    origin = captor.matrix_world.translation
    print("captor position : " + str(origin))
    
    ray_direction = mathutils.Vector((0,0,-1))
    
    ray_begin_local = line.matrix_world.inverted() @ origin

    result, loc, normal, face_idx = line.ray_cast(ray_begin_local, ray_direction)

    return result

def lf_read_digital():
    return [int(is_captor_over_line(captor, line)) for captor in capteurs] 


def get_angle_to_turn():
    angle = 0
    read = lf_read_digital()
    print(read)
    
    if read == [0,0,0,0,0]:
        return last_angle
    
    angle = (mean([i for i, n in enumerate(read) if n==1])-2)*-2
    print("Angle: ",angle)
    return math.radians(angle)
            


##### Animation #######
for i in range(2500):
    print("FRAME :: ", i)
    bpy.context.scene.frame_set(frame_num)
    
    angle = get_angle_to_turn()
    last_angle = angle
    print("Angle rad:", angle)
    ob.rotation_euler.z += angle
    print("Angle ob:", ob.rotation_euler.z)
    
    vec = mathutils.Vector((0.001,0,0))
    inv = ob.matrix_world.copy()
    inv.invert()
    vec_rot = vec @ inv
    
    ob.location += vec_rot 
    
    bpy.ops.anim.keyframe_insert(type='LocRotScale') 
    frame_num+=1
    

print("Done")