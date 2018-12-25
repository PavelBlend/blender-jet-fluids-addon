
import struct
import os

import bpy
import bgl


handle_3d = None
minc = (0.0, 0.0, 1.0)
maxc = (0.0, 1.0, 1.0)
max_velocity = 10


def generate_particle_color(factor):
    r = minc[0] + factor * (maxc[0] - minc[0])
    g = minc[1] + factor * (maxc[1] - minc[1])
    b = minc[2] + factor * (maxc[2] - minc[2])
    return (r, g, b)


def draw_scene_particles():
    for obj in bpy.data.objects:
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.show_particles:
                draw_particles(obj)


def draw_particles(domain):
    file_path = '{}{}.bin'.format(domain.jet_fluid.cache_folder, bpy.context.scene.frame_current)
    if not os.path.exists(file_path):
        return
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    bgl.glPointSize(3)
    bgl.glBegin(bgl.GL_POINTS)
    for particle_index in range(particles_count):
        particle_position = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        vel = struct.unpack('3f', particles_data[p : p + 12])
        p += 12
        color_factor = (vel[0]**2 + vel[1]**2 + vel[2]**2) ** (1/2) / max_velocity
        color = generate_particle_color(color_factor)
        bgl.glColor4f(color[0], color[1], color[2], 1.0)
        bgl.glVertex3f(
            particle_position[0],
            particle_position[2],
            particle_position[1]
        )
    bgl.glEnd()


def register():
    handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_scene_particles, (), 'WINDOW', 'POST_VIEW')


def unregister():
    bpy.types.SpaceView3D.draw_handler_remove(handle_3d, 'WINDOW')
