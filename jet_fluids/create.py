
import os
import struct

import bpy


def remove_par_object(domain):
    if domain.jet_fluid.particles_object:
        par_object = bpy.data.objects[domain.jet_fluid.particles_object]
        par_mesh = par_object.data
        domain.jet_fluid.particles_object = ''
        bpy.data.objects.remove(par_object)
        bpy.data.meshes.remove(par_mesh)


def update_par_object(self, context):
    obj_names = {obj.name for obj in bpy.data.objects}
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.create_particles:
                create_particles(obj)
            else:
                remove_par_object(obj)


def create_particles(domain):
    file_path = '{}{}.bin'.format(domain.jet_fluid.cache_folder, bpy.context.scene.frame_current)
    if not os.path.exists(file_path):
        remove_par_object(domain)
        return
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    vertices = []
    for particle_index in range(particles_count):
        pos = struct.unpack('3f', particles_data[p : p + 12])
        p += 24    # skip velocities
        vertices.append((pos[0], pos[2], pos[1]))

    par_mesh = bpy.data.meshes.new('temp_name')
    if not domain.jet_fluid.particles_object:
        par_object = bpy.data.objects.new('jet_fluid_particles', par_mesh)
        domain.jet_fluid.particles_object = par_object.name
        bpy.context.scene.objects.link(par_object)
    else:
        par_object = bpy.data.objects[domain.jet_fluid.particles_object]
        old_par_mesh = par_object.data
        par_object.data = par_mesh
        bpy.data.meshes.remove(old_par_mesh)
    par_mesh.from_pydata(vertices, (), ())
    par_mesh.name = 'jet_fluid_particles'


@bpy.app.handlers.persistent
def import_particles(scene):
    obj_names = {obj.name for obj in bpy.data.objects}
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.create_particles:
                create_particles(obj)


def register():
    bpy.app.handlers.frame_change_pre.append(import_particles)


def unregister():
    bpy.app.handlers.frame_change_pre.remove(import_particles)
