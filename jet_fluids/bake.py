
import struct
import os

import bpy

from . import pyjet


solvers = {
    'APIC': pyjet.ApicSolver3,
    'PIC': pyjet.PicSolver3,
    'FLIP': pyjet.FlipSolver3
}
advection_solvers = {
    'SEMI_LAGRANGIAN': pyjet.SemiLagrangian3,
    'CUBIC_SEMI_LAGRANGIAN': pyjet.CubicSemiLagrangian3
}
diffusion_solvers = {
    'FORWARD_EULER': pyjet.GridForwardEulerDiffusionSolver3,
    'BACKWARD_EULER': pyjet.GridBackwardEulerDiffusionSolver3
}
pressure_solvers = {
    'FRACTIONAL_SINGLE_PHASE': pyjet.GridFractionalSinglePhasePressureSolver3,
    'SINGLE_PHASE': pyjet.GridSinglePhasePressureSolver3
}


def read_particles(file_path):
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    positions = []
    velocities = []
    forces = []
    for particle_index in range(particles_count):
        pos = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        positions.append(pos)
        vel = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        velocities.append(vel)
        force = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        forces.append(force)
    return positions, velocities, forces


def get_triangle_mesh(context, source, solver, domain_object):
    selected_objects_name = [o.name for o in context.selected_objects]
    active_object_name = context.scene.objects.active.name
    bpy.ops.object.select_all(action='DESELECT')
    source.select = True
    bpy.ops.object.duplicate()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    obj = context.selected_objects[0]
    mesh = obj.data
    context.scene.objects.active = obj
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.reveal()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    bpy.ops.object.mode_set(mode='OBJECT')
    print('generete Triangle Mesh')
    triangle_mesh = pyjet.TriangleMesh3(
        points=[[v.co.x, v.co.z, v.co.y] for v in mesh.vertices],
        pointIndices=[[p.vertices[0], p.vertices[2], p.vertices[1]] for p in mesh.polygons]
    )
    print('generete Implicit Triangle Mesh')
    res_x = int(round(obj.dimensions[0] / domain_object.dimensions[0] * solver.resolution.x, 0))
    imp_triangle_mesh = pyjet.ImplicitTriangleMesh3(mesh=triangle_mesh, resolutionX=res_x, margin=0.2)
    print('remove objects')
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    for obj_name in selected_objects_name:
        bpy.data.objects[obj_name].select = True
    bpy.context.scene.objects.active = bpy.data.objects[active_object_name]
    return imp_triangle_mesh


def set_closed_domain_boundary_flag(solver, obj):
    jet = obj.jet_fluid
    bounds = [
        jet.bound_right,
        jet.bound_left,
        jet.bound_front,
        jet.bound_back,
        jet.bound_up,
        jet.bound_down
    ]
    flags = [
        pyjet.DIRECTION_RIGHT,
        pyjet.DIRECTION_LEFT,
        pyjet.DIRECTION_FRONT,
        pyjet.DIRECTION_BACK,
        pyjet.DIRECTION_UP,
        pyjet.DIRECTION_DOWN
        
    ]

    bound_flag = 0
    for bound_index, bound in enumerate(bounds):
        if bound:
            bound_flag |= flags[bound_index]

    solver.closedDomainBoundaryFlag = bound_flag


def calc_res(self, obj, type='FLUID'):
    self.domain = obj
    domain_size_x = obj.bound_box[6][0] * obj.scale[0] - obj.bound_box[0][0] * obj.scale[0]
    domain_size_y = obj.bound_box[6][1] * obj.scale[1] - obj.bound_box[0][1] * obj.scale[1]
    domain_size_z = obj.bound_box[6][2] * obj.scale[2] - obj.bound_box[0][2] * obj.scale[2]
    domain_sizes = [
        domain_size_x,
        domain_size_y,
        domain_size_z
    ]
    self.domain_size_x = domain_size_x
    if type == 'FLUID':
        resolution = obj.jet_fluid.resolution
        grid_spacing = (0, 0, 0)
    elif type == 'MESH':
        resolution = obj.jet_fluid.resolution_mesh
        fluid_res = obj.jet_fluid.resolution
        grid_spacing_x = resolution
        grid_spacing_y = resolution
        grid_spacing_z = resolution
        grid_spacing = (grid_spacing_x, grid_spacing_z, grid_spacing_y)
    self.domain_max_size = max(domain_sizes)
    resolution_x = int(round((domain_size_x / self.domain_max_size) * resolution, 1))
    resolution_y = int(round((domain_size_y / self.domain_max_size) * resolution, 1))
    resolution_z = int(round((domain_size_z / self.domain_max_size) * resolution, 1))
    origin_x = obj.bound_box[0][0] * obj.scale[0] + obj.location[0]
    origin_y = obj.bound_box[0][1] * obj.scale[1] + obj.location[1]
    origin_z = obj.bound_box[0][2] * obj.scale[2] + obj.location[2]
    return resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, grid_spacing


def read_times_cache(folder):
    frame_index = 0
    times = {}
    cache_path = folder + 'fluid_{:0>6}_00.bphys'.format(frame_index)
    if os.path.exists(cache_path):
        file = open(cache_path, 'rb')
        data = file.read()
        file.close()

        header = b'BPHYSICS'
        header_size = len(header)
        p = 0
        struct.unpack('{}s'.format(header_size), data[p : p + header_size])
        p += header_size

        cache_type = struct.unpack('I', data[p : p + 4])[0]
        p += 4

        particles_count = struct.unpack('I', data[p : p + 4])[0]
        p += 4

        data_type = struct.unpack('I', data[p : p + 4])[0]
        p += 4

        for particle_index in range(particles_count):
            time = struct.unpack('fff', data[p : p + 12])
            p += 12
            times[particle_index] = int(round(time[0], 0))

    return times


def append_blender_particles_cache_times(folder, times, frame_end):
    indices = list(times.keys())
    indices.sort()

    bin_data = bytearray()
    bin_data.extend(b'BPHYSICS')
    bin_data.extend(struct.pack('I', 1))    # cache type (1 - particles)
    bin_data.extend(struct.pack('I', indices[-1]))    # particles count
    bin_data.extend(struct.pack('I', 0b1000000))    # particles data types

    for index in indices:
        time = times[index]
        bin_data.extend(struct.pack('3f', time, frame_end, frame_end))

    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(0), 'wb')
    file.write(bin_data)
    file.close()

    return indices[-1]


def save_blender_particles_cache_times(folder, times, frame_end):
    indices = list(times.keys())
    indices.sort()

    bin_data = bytearray()
    bin_data.extend(b'BPHYSICS')
    bin_data.extend(struct.pack('I', 1))    # cache type (1 - particles)
    bin_data.extend(struct.pack('I', indices[-1]))    # particles count
    bin_data.extend(struct.pack('I', 0b1000000))    # particles data types

    for index in indices:
        time = times[index]
        bin_data.extend(struct.pack('3f', time, frame_end, frame_end))

    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(0), 'wb')
    file.write(bin_data)
    file.close()

    return indices[-1]


def save_blender_particles_cache(frame_index, folder, positions, velocities, times, offset):
    bin_data = bytearray()
    particles_count = len(positions)
    bin_data.extend(b'BPHYSICS')
    bin_data.extend(struct.pack('I', 1))    # cache type (1 - particles)
    bin_data.extend(struct.pack('I', particles_count))
    bin_data.extend(struct.pack('I', 0b111))    # particles data types

    for particle_index in range(particles_count):

        bin_data.extend(struct.pack('I', particle_index))

        pos = positions[particle_index]
        bin_data.extend(struct.pack('3f', pos[0], pos[2], pos[1]))

        vel = velocities[particle_index]
        bin_data.extend(struct.pack('3f', vel[0], vel[2], vel[1]))

        if not times.get(particle_index):
            times[particle_index] = offset + frame_index

    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(offset + frame_index), 'wb')
    file.write(bin_data)
    file.close()
