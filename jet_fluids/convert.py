
import os
import struct

import bpy

from . import bake


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

    particles_count = indices[-1]
    return particles_count


def save_blender_particles_cache(frame_index, folder, positions, velocities, times):
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
            times[particle_index] = frame_index

    file = open(folder + 'fluid_{:0>6}_00.bphys'.format(frame_index), 'wb')
    file.write(bin_data)
    file.close()

    return times


def convert_particles_to_standart_particle_system(context, domain):
    times = {}
    folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
    frame_end = context.scene.frame_end + 1

    for frame_index in range(0, frame_end):
        file_path = '{}particles_{}.bin'.format(folder, frame_index)
        if not os.path.exists(file_path):
            continue
        positions, velocities, forces = bake.read_particles(file_path)
        times = save_blender_particles_cache(frame_index, folder, positions, velocities, times)

    if times:
        particles_count = save_blender_particles_cache_times(folder, times, frame_end)

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
        par_sys.settings.draw_color = 'VELOCITY'
        par_sys.settings.color_maximum = 10.0
