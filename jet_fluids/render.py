import os

import bpy
import bgl
import gpu
from gpu_extras.batch import batch_for_shader

from . import create


handle_3d = None


def generate_particle_color(factor, jet_props):
    r = jet_props.color_1[0] + factor * (jet_props.color_2[0] - jet_props.color_1[0])
    g = jet_props.color_1[1] + factor * (jet_props.color_2[1] - jet_props.color_1[1])
    b = jet_props.color_1[2] + factor * (jet_props.color_2[2] - jet_props.color_1[2])
    return (r, g, b)


def draw_scene_particles():
    for obj in bpy.data.objects:
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.show_particles:
                particles = create.get_gl_particles_cache().get(obj.name, None)
                if not particles is None:
                    draw_particles(obj, particles)


def draw_particles(domain, particles):
    shader = gpu.shader.from_builtin('3D_FLAT_COLOR')
    if domain.jet_fluid.color_type == 'VELOCITY':
        positions = particles[0]
        colors = particles[1]
        batch = batch_for_shader(shader, 'POINTS', {"pos": positions, "color": colors})
    elif domain.jet_fluid.color_type == 'SINGLE_COLOR':
        color = domain.jet_fluid.color_1
        colors = []
        for i in range(len(particles)):
            colors.append((*color, 1.0))
        batch = batch_for_shader(shader, 'POINTS', {"pos": particles, "color": colors})
    shader.bind()
    bgl.glPointSize(domain.jet_fluid.particle_size)
    batch.draw(shader)


def register():
    global handle_3d
    handle_3d = bpy.types.SpaceView3D.draw_handler_add(draw_scene_particles, (), 'WINDOW', 'POST_VIEW')


def unregister():
    global handle_3d
    bpy.types.SpaceView3D.draw_handler_remove(handle_3d, 'WINDOW')
