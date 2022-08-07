import os

import bpy


solvers = ['FLIP', 'PIC', 'APIC']
cache_folder = os.path.join(os.path.abspath(os.curdir), 'tests_cache')
cache_folder += os.sep
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

for solver in solvers:
    bpy.ops.mesh.primitive_cube_add(
        size=2, enter_editmode=False, location=(0, 0, 0)
    )
    domain_object = bpy.context.object
    bpy.ops.jet_fluid.add()
    domain_object.jet_fluid.object_type = 'DOMAIN'
    domain_object.jet_fluid.resolution = 20
    domain_object.jet_fluid.solver_type = solver
    domain_object.jet_fluid.cache_folder = cache_folder
    
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = 5
    
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=3, radius=0.5, enter_editmode=False, location=(0, 0, 0)
    )
    emitter_object = bpy.context.object
    bpy.ops.jet_fluid.add()
    emitter_object.jet_fluid.object_type = 'EMITTER'
    emitter_object.jet_fluid.particles_count = 2.0
    
    bpy.context.view_layer.objects.active = domain_object
    bpy.ops.jet_fluid.bake_particles()
    bpy.ops.jet_fluid.bake_mesh()
    bpy.ops.jet_fluid.reset_particles()
    bpy.ops.jet_fluid.reset_mesh()

os.removedirs(cache_folder)

print('\n' * 5)
print('=' * 79)
print('FINISH!')
print('=' * 79)
