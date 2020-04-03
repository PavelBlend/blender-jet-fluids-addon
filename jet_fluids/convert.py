import os
import struct
import time

import bpy

from .utils import get_log_path, convert_time_to_string


domain = None


def print_convert_info(*print_params):
    global domain
    if domain.jet_fluid.print_debug_info:
        print(*print_params)
    if domain.jet_fluid.write_log:
        log_file_path = get_log_path(domain, '_jet_fluids_convert.log')
        with open(log_file_path, 'a') as log_file:
            print(*print_params, file=log_file)


def save_blender_particles_cache_times(folder, times, frame_end):
    start_time = time.time()
    print_convert_info('Save patricles times start')
    indices = list(times.keys())
    indices.sort()

    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(0), 'wb')
    file.write(b'BPHYSICS')
    file.write(struct.pack('I', 1))    # cache type (1 - particles)
    file.write(struct.pack('I', indices[-1]))    # particles count
    file.write(struct.pack('I', 0b1000000))    # particles data types

    io = struct.Struct('3f')
    for index in indices:
        patricle_time = times[index]
        file.write(io.pack(patricle_time, frame_end, frame_end))

    file.close()

    particles_count = indices[-1]
    print_convert_info('Save patricles times end')
    print_convert_info('Save time: {0}'.format(convert_time_to_string(start_time)))
    print_convert_info('-' * 79)
    return particles_count


def save_blender_particles_cache(frame_index, folder, par_file, times):
    global domain
    start_time = time.time()
    cache_path = folder + 'fluid_{:0>6}_00.bphys'.format(frame_index)
    if os.path.exists(cache_path) and not domain.jet_fluid.overwrite_convert:
        print('Skip frame: {0}'.format(frame_index))
        return times
    print_convert_info('Convert patricles start: frame {0:0>6}'.format(frame_index))
    file = open(cache_path, 'wb')
    particles_count = struct.unpack('I', par_file.read(4))[0]
    file.write(b'BPHYSICS')
    file.write(struct.pack('I', 1))    # cache type (1 - particles)
    file.write(struct.pack('I', particles_count))
    file.write(struct.pack('I', 0b10111))    # particles data types
    unpacker = struct.Struct('13f')
    packer = struct.Struct('9f')

    for particle_index in range(particles_count):

        file.write(struct.pack('I', particle_index))

        (pos_x, pos_z, pos_y,
        vel_x, vel_z, vel_y,
        for_x, for_z, for_y,
        col_r, col_g, col_b, col_a) = unpacker.unpack(par_file.read(52))

        file.write(packer.pack(
            pos_x, pos_y, pos_z,
            vel_x, vel_y, vel_z,
            col_r, col_g, col_b
        ))

        if not times.get(particle_index):
            times[particle_index] = frame_index

    file.close()
    print_convert_info('Convert patricles end:   frame {0:0>6}'.format(frame_index))
    print_convert_info('Convert time: {0}'.format(convert_time_to_string(start_time)))
    print_convert_info('-' * 79)

    return times


def get_particles_count(times_file_path):
    with open(times_file_path, 'rb') as file:
        data = file.read()
    pos = 0
    header = struct.unpack('8s', data[pos : pos + 8])    # BPHYSICS
    pos += 8
    cache_type = struct.unpack('I', data[pos : pos + 4])[0]
    pos += 4
    if cache_type != 1:    # particles
        return 0
    particles_count = struct.unpack('I', data[pos : pos + 4])[0]
    pos += 4
    return particles_count


def create_standart_particles_system(domain, particles_count=None):
    if domain.particle_systems.get('fluid'):
        par_sys = domain.particle_systems['fluid']
    else:
        bpy.ops.object.particle_system_add()
        par_sys = domain.particle_systems.active
        par_sys.name = 'fluid'

    if particles_count is None:
        folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
        times_file_path = folder + 'fluid_{:0>6}_00.bphys'.format(0)
        if os.path.exists(times_file_path):
            particles_count = get_particles_count(times_file_path)
        else:
            particles_count = 0

    par_sys.point_cache.use_external = True
    par_sys.point_cache.filepath = domain.jet_fluid.cache_folder
    par_sys.point_cache.name = 'fluid'
    par_sys.point_cache.index = 0
    par_sys.settings.count = particles_count
    par_sys.settings.display_color = 'VELOCITY'
    par_sys.settings.display_method = 'DOT'
    par_sys.settings.display_size = 0.025
    par_sys.settings.color_maximum = 10.0


def convert_particles_to_standart_particle_system(context, domain_object):
    global domain
    domain = domain_object
    log_path = get_log_path(domain, '_jet_fluids_convert.log')
    with open(log_path, 'w') as log_file:
        pass
    times = {}
    folder = bpy.path.abspath(domain.jet_fluid.cache_folder)

    if domain.jet_fluid.frame_range_convert == 'CUSTOM':
        frame_start = domain.jet_fluid.frame_range_convert_start
        frame_end = domain.jet_fluid.frame_range_convert_end
    elif domain.jet_fluid.frame_range_convert == 'TIMELINE':
        frame_start = context.scene.frame_start
        frame_end = context.scene.frame_end
    else:
        frame_start = context.scene.frame_current
        frame_end = context.scene.frame_current

    for frame_index in range(frame_start, frame_end + 1):
        file_path = '{0}particles_{1:0>6}.bin'.format(folder, frame_index)
        if not os.path.exists(file_path):
            continue
        particles_file = open(file_path, 'rb')
        times = save_blender_particles_cache(frame_index, folder, particles_file, times)
        particles_file.close()

    if times:
        particles_count = save_blender_particles_cache_times(folder, times, frame_end + 1)
        create_standart_particles_system(domain, particles_count)


def convert_data_to_jet_particles(context, domain_object):
    global domain
    domain = domain_object
    print_convert_info('Convert data to jet particles start')
    jet = domain.jet_fluid
    verts_obj = bpy.data.objects.get(jet.input_vertices_object, None)
    par_sys = verts_obj.particle_systems.active
    if jet.frame_range_convert == 'CUSTOM':
        frame_start = jet.frame_range_convert_start
        frame_end = jet.frame_range_convert_end
    elif jet.frame_range_convert == 'TIMELINE':
        frame_start = context.scene.frame_start
        frame_end = context.scene.frame_end
    else:
        frame_start = context.scene.frame_current
        frame_end = context.scene.frame_current

    for frame_index in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame_index)
        file_path = '{0}particles_{1:0>6}.bin'.format(
            bpy.path.abspath(jet.cache_folder),
            frame_index
        )
        if os.path.exists(file_path) and not jet.overwrite_convert:
            print_convert_info('    Skip frame: {0}'.format(frame_index))
            continue
        if not verts_obj:
            return
        if jet.input_data_type == 'VERTICES':
            mesh = verts_obj.data
            particles_count = len(mesh.vertices)
            data = bytearray()
            data.extend(struct.pack('I', particles_count))
            for vertex in mesh.vertices:
                vert_co = verts_obj.matrix_world @ vertex.co
                # position
                data.extend(struct.pack('3f', vert_co.x, vert_co.z, vert_co.y))
                # velocity
                data.extend(struct.pack('3f', 0.0, 0.0, 0.0))
                # forces
                data.extend(struct.pack('3f', 0.0, 0.0, 0.0))
                # color
                data.extend(struct.pack('4f', 1.0, 1.0, 1.0, 1.0))
        elif jet.input_data_type == 'PARTICLES':
            if not par_sys:
                return
            evaluated_object = context.view_layer.depsgraph.objects.get(verts_obj.name)
            if not evaluated_object:
                return
            particles = evaluated_object.particle_systems[0].particles
            particles_count = 0
            data = bytearray()
            for particle in particles:
                if particle.alive_state == 'ALIVE':
                    par_co = particle.location
                    # position
                    data.extend(struct.pack('3f', par_co.x, par_co.z, par_co.y))
                    # velocity
                    data.extend(struct.pack('3f', 0.0, 0.0, 0.0))
                    # forces
                    data.extend(struct.pack('3f', 0.0, 0.0, 0.0))
                    # color
                    data.extend(struct.pack('4f', 1.0, 1.0, 1.0, 1.0))
                    particles_count += 1
            par_count_bin = struct.pack('I', particles_count)
            data.insert(0, par_count_bin[0])
            data.insert(1, par_count_bin[1])
            data.insert(2, par_count_bin[2])
            data.insert(3, par_count_bin[3])
        particles_file = open(file_path, 'wb')
        particles_file.write(data)
        particles_file.close()
    print_convert_info('Convert data to jet particles end')
