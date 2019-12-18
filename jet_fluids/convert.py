import os
import struct
import time

import bpy

from .utils import get_log_path


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
    print_convert_info('Save time: {0:.3}s'.format(time.time() - start_time))
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
    print_convert_info('Convert time: {0:.3}s'.format(time.time() - start_time))
    print_convert_info('-' * 79)

    return times


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

        if domain.particle_systems.get('fluid'):
            par_sys = domain.particle_systems['fluid']
        else:
            bpy.ops.object.particle_system_add()
            par_sys = domain.particle_systems.active
            par_sys.name = 'fluid'

        par_sys.point_cache.use_external = True
        par_sys.point_cache.filepath = domain.jet_fluid.cache_folder
        par_sys.point_cache.name = 'fluid'
        par_sys.point_cache.index = 0
        par_sys.settings.count = particles_count
        par_sys.settings.display_color = 'VELOCITY'
        par_sys.settings.color_maximum = 10.0
