import bpy

verts = ((-0.3999999761581421, -0.19999998807907104, 0.0),
         (0.3999999761581421, -0.19999998807907104, 0.0),
         (-0.3999999761581421, 0.19999998807907104, 0.0),
         (0.3999999761581421, 0.19999998807907104, 0.0))

faces = ((0, 1, 3, 2))

scene = bpy.context.scene
me = bpy.data.meshes.new("Plane")
me.from_pydata(verts, [], faces)
ob = bpy.data.objects.new("Plane", me)
scene.collection.objects.link(ob)
scene.view_layer.objects.active = ob