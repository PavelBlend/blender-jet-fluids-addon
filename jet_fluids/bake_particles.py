import os
import numpy
import time

import bpy

from . import pyjet
from . import bake
from . import create
from .utils import print_info, convert_time_to_string


def get_transforms(obj):
    pos = obj.matrix_world.to_translation()
    rot = obj.matrix_world.to_quaternion()
    return pos, rot


def read_particles(file_path):
    data = []
    for data_type in ('POS', 'VEL', 'FORCE'):
        array = []
        file_path = get_file_path(domain, data_type, frame_index)
        if not os.path.exists(file_path):
            print_mesh_info('Can\'t find file for {} frame'.format(frame_index))
            return array
        array = get_array(file_path, 'FLOAT')
        data.append(array)
    return data


class JetFluidBakeParticles(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_particles"
    bl_label = "Bake Particles"
    bl_options = {'REGISTER'}

    def find_emitters_and_colliders(self):
        emitters = []
        colliders = []
        obj_names = {obj.name for obj in bpy.data.objects}
        for obj_name in obj_names:
            obj = bpy.data.objects.get(obj_name)
            if not obj:
                continue
            if obj.jet_fluid.is_active:
                if obj.jet_fluid.object_type == 'EMITTER':
                    emitters.append(obj)
                elif obj.jet_fluid.object_type == 'COLLIDER':
                    colliders.append(obj)
        return emitters, colliders

    def simulate(self, offset=0):
        solv = self.solver
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, grid_spacing = bake.calc_res(self, self.domain, type='MESH')
        jet = self.domain.jet_fluid
        create_mesh = jet.create_mesh
        create_particles = jet.create_particles
        jet.create_mesh = False
        jet.create_particles = False
        current_frame = self.context.scene.frame_current
        folder = bpy.path.abspath(self.domain.jet_fluid.cache_folder)
        while self.frame.index + offset <= self.frame_end:
            print_info('-' * 79)
            print_info('Frame start', self.frame.index + offset)
            self.context.scene.frame_set(self.frame.index + offset)
            vertices = []
            for emitter in self.emitters:
                jet_emmiter = self.jet_emitters_dict.get(emitter.name, None)
                if jet_emmiter:
                    vel = emitter.jet_fluid.velocity
                    jet_emmiter.initialVelocity = vel[0], vel[2], vel[1]
                    jet_emmiter.isOneShot = emitter.jet_fluid.one_shot
                    if not emitter.jet_fluid.one_shot:
                        jet_emmiter.isEnabled = emitter.jet_fluid.is_enable
                    else:
                        if emitter.animation_data:
                            if emitter.animation_data.action:
                                fcurve = emitter.animation_data.action.fcurves.find('jet_fluid.is_enable')
                                val = fcurve.evaluate(self.context.scene.frame_current - 1.0)
                                if val == 1.0:
                                    jet_emmiter.isEnabled = False
                                else:
                                    jet_emmiter.isEnabled = emitter.jet_fluid.is_enable
                    pos, rot = get_transforms(emitter)
                    jet_emmiter.surface.transform = pyjet.Transform3(
                        translation=(pos[0], pos[2], pos[1]),
                        orientation=(-rot[0], rot[1], rot[3], rot[2])
                    )
                    jet_emmiter.linearVelocity = (0, 0, 0)

            for collider, collider_object in self.jet_colliders:
                collider.frictionCoefficient = collider_object.jet_fluid.collider_friction
                pos, rot = get_transforms(collider_object)
                collider.surface.transform = pyjet.Transform3(
                    translation=(pos[0], pos[2], pos[1]),
                    orientation=(-rot[0], rot[1], rot[3], rot[2])
                )
            frame = self.frame.index + offset
            file_path = '{0}particles_{1:0>6}.bin'.format(
                bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                self.frame.index + offset
            )
            solv.viscosityCoefficient = self.domain.jet_fluid.viscosity
            print_info('Solver update start')
            solv.update(self.frame)
            print_info('Solver update end')
            print_info('Save particles start')
            print_info('    Convert particles to numpy array start')
            positions = numpy.array(solv.particleSystemData.positions, copy=False)
            velocities = numpy.array(solv.particleSystemData.velocities, copy=False)
            forces = numpy.array(solv.particleSystemData.forces, copy=False)
            print_info('    Convert particles to numpy array end')
            vertices_count = len(positions)

            pos_path = create.get_file_path(self.domain, 'POS', frame=frame)
            create.write_array(positions, pos_path, 'FLOAT', offset=self.domain.location)

            vel_path = create.get_file_path(self.domain, 'VEL', frame=frame)
            create.write_array(velocities, vel_path, 'FLOAT')

            force_path = create.get_file_path(self.domain, 'FORCE', frame=frame)
            create.write_array(forces, force_path, 'FLOAT')

            print_info('Save particles end')
            print_info('Frame end', self.frame.index + offset)
            self.frame.advance()
        jet.create_mesh = create_mesh
        jet.create_particles = create_particles
        self.context.scene.frame_set(current_frame)
        return {'FINISHED'}

    def execute(self, context):
        obj = context.object
        print_info('-' * 79)
        print_info('SIMULATION START')
        start_time = time.time()
        self.context = context
        pyjet.Logging.mute()
        if not obj.jet_fluid.cache_folder:
            self.report({'WARNING'}, 'Cache Folder not Specified!')
            return {'FINISHED'}
        print_info('Create solver start')
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = bake.calc_res(self, obj)
        solver = bake.solvers[obj.jet_fluid.solver_type](
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=domain_size_x
        )
        print_info('Create solver end')
        print_info('Set solver props start')
        solver.maxCfl = obj.jet_fluid.max_cfl
        solver.advectionSolver = bake.advection_solvers[obj.jet_fluid.advection_solver_type]()
        solver.diffusionSolver = bake.diffusion_solvers[obj.jet_fluid.diffusion_solver_type]()
        solver.pressureSolver = bake.pressure_solvers[obj.jet_fluid.pressure_solver_type]()
        solver.useCompressedLinearSystem = obj.jet_fluid.compressed_linear_system
        solver.isUsingFixedSubTimeSteps = obj.jet_fluid.fixed_substeps
        solver.numberOfFixedSubTimeSteps = obj.jet_fluid.fixed_substeps_count
        bound_flag = bake.set_closed_domain_boundary_flag(obj, 'domain_closed_boundary')
        solver.closedDomainBoundaryFlag = bound_flag
        solver.viscosityCoefficient = obj.jet_fluid.viscosity
        grav = obj.jet_fluid.gravity
        solver.gravity = grav[0], grav[2], grav[1]
        if obj.jet_fluid.fps_mode == 'SCENE':
            frame = pyjet.Frame(0, 1.0 / context.scene.render.fps)
        else:
            frame = pyjet.Frame(0, 1.0 / obj.jet_fluid.fps)
        self.solver = solver
        self.frame = frame
        print_info('Set solver props end')
        print_info('Create others objects start')

        if obj.jet_fluid.frame_range_simulation == 'CUSTOM':
            frame_start = obj.jet_fluid.frame_range_simulation_start
            frame_end = obj.jet_fluid.frame_range_simulation_end
        else:
            frame_start = context.scene.frame_start
            frame_end = context.scene.frame_end

        cache_folder = bpy.path.abspath(self.domain.jet_fluid.cache_folder)
        if not os.path.exists(cache_folder):
            os.makedirs(cache_folder)

        self.frame_end = frame_end

        for frame_index in range(frame_start, self.frame_end):
            file_path = '{0}particles_{1:0>6}.bin'.format(
                bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                frame_index
            )
            if os.path.exists(file_path) and not obj.jet_fluid.overwrite_simulation:
                print_info('Skip frame:', frame_index)
                continue
            else:
                if frame_index == frame_start:
                    emitters, colliders = self.find_emitters_and_colliders()
                    jet_emitters = []
                    self.jet_emitters_dict = {}
                    print_info('    Create emitters start')
                    for emitter_object in emitters:
                        print_info('        Create mesh start: "{0}"'.format(emitter_object.name))
                        triangle_mesh = bake.get_triangle_mesh(context, emitter_object, solver, obj)
                        print_info('        Create mesh end:   "{0}"'.format(emitter_object.name))
                        init_vel = emitter_object.jet_fluid.velocity
                        print_info('        Create particle emitter start: "{0}"'.format(emitter_object.name))
                        emitter = pyjet.VolumeParticleEmitter3(
                            implicitSurface=triangle_mesh,
                            maxRegion=solver.gridSystemData.boundingBox,
                            spacing=self.domain_max_size / (obj.jet_fluid.resolution * emitter_object.jet_fluid.particles_count),
                            isOneShot=emitter_object.jet_fluid.one_shot,
                            isEnable=emitter_object.jet_fluid.is_enable,
                            initialVelocity=[init_vel[0], init_vel[2], init_vel[1]],
                            jitter=emitter_object.jet_fluid.emitter_jitter,
                            allowOverlapping=emitter_object.jet_fluid.allow_overlapping,
                            seed=emitter_object.jet_fluid.emitter_seed,
                            maxNumberOfParticles=emitter_object.jet_fluid.max_number_of_particles
                        )
                        self.jet_emitters_dict[emitter_object.name] = emitter
                        jet_emitters.append(emitter)
                        print_info('        Create particle emitter end:   "{0}"'.format(emitter_object.name))
                    print_info('    Create emitters end')
                    print_info('    Create particle emitter set start')
                    self.emitters = emitters
                    emitter_set = pyjet.ParticleEmitterSet3(emitters=jet_emitters)
                    solver.particleEmitter = emitter_set
                    print_info('    Create particle emitter set end')
                    # set colliders
                    print_info('    Create colliders start')
                    self.jet_colliders = []
                    for collider_object in colliders:
                        print_info('        Create collider mesh start: "{0}"'.format(collider_object.name))
                        triangle_mesh = bake.get_triangle_mesh(context, collider_object, solver, obj)
                        pos, rot = get_transforms(collider_object)
                        triangle_mesh.transform = pyjet.Transform3(
                            translation=(pos[0], pos[2], pos[1]),
                            orientation=(-rot[0], rot[1], rot[3], rot[2])
                        )
                        collider = pyjet.RigidBodyCollider3(surface=triangle_mesh)
                        collider.frictionCoefficient = collider_object.jet_fluid.collider_friction
                        self.jet_colliders.append((collider, collider_object))
                        print_info('        Create collider mesh end:   "{0}"'.format(collider_object.name))
                    if self.jet_colliders:
                        print_info('    Create collider set start')
                        collider_set = pyjet.ColliderSet3()
                        for collider, collider_object in self.jet_colliders:
                            collider_set.addCollider(collider)
                        solver.collider = collider_set
                        print_info('    Create collider set end')
                    print_info('    Create colliders end')
                    # simulate
                    self.simulate(offset=frame_start)
                    break
                else:
                    last_frame = frame_index - 1
                    file_path = '{0}particles_{1:0>6}.bin'.format(
                        bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                        last_frame
                    )
                    emitters, colliders = self.find_emitters_and_colliders()
                    jet_emitters = []
                    self.jet_emitters_dict = {}
                    print_info('    Create emitters start')
                    for emitter_object in emitters:
                        if not emitter_object.jet_fluid.one_shot:
                            print_info('        Create mesh start: "{0}"'.format(emitter_object.name))
                            triangle_mesh = bake.get_triangle_mesh(context, emitter_object, solver, obj)
                            print_info('        Create mesh end:   "{0}"'.format(emitter_object.name))
                            init_vel = emitter_object.jet_fluid.velocity
                            print_info('        Create particle emitter start: "{0}"'.format(emitter_object.name))
                            emitter = pyjet.VolumeParticleEmitter3(
                                implicitSurface=triangle_mesh,
                                maxRegion=solver.gridSystemData.boundingBox,
                                spacing=self.domain_max_size / (obj.jet_fluid.resolution * emitter_object.jet_fluid.particles_count),
                                isOneShot=emitter_object.jet_fluid.one_shot,
                                isEnable=emitter_object.jet_fluid.is_enable,
                                initialVelocity=[init_vel[0], init_vel[2], init_vel[1]]
                            )
                            self.jet_emitters_dict[emitter_object.name] = emitter
                            jet_emitters.append(emitter)
                            print_info('        Create particle emitter end:   "{0}"'.format(emitter_object.name))
                    print_info('    Create emitters end')
                    print_info('    Create particle emitter set start')
                    self.emitters = emitters
                    emitter_set = pyjet.ParticleEmitterSet3(emitters=jet_emitters)
                    solver.particleEmitter = emitter_set
                    print_info('    Create particle emitter set end')
                    # set colliders
                    print_info('    Create colliders start')
                    self.jet_colliders = []
                    for collider_object in colliders:
                        print_info('        Create collider mesh start: "{0}"'.format(collider_object.name))
                        triangle_mesh = bake.get_triangle_mesh(context, collider_object, solver, obj)
                        pos, rot = get_transforms(collider_object)
                        triangle_mesh.transform = pyjet.Transform3(
                            translation=(pos[0], pos[2], pos[1]),
                            orientation=(-rot[0], rot[1], rot[3], rot[2])
                        )
                        collider = pyjet.RigidBodyCollider3(surface=triangle_mesh)
                        collider.frictionCoefficient = collider_object.jet_fluid.collider_friction
                        self.jet_colliders.append((collider, collider_object))
                        print_info('        Create collider mesh end:   "{0}"'.format(collider_object.name))
                    if self.jet_colliders:
                        print_info('    Create collider set start')
                        collider_set = pyjet.ColliderSet3()
                        for collider, collider_object in self.jet_colliders:
                            collider_set.addCollider(collider)
                        solver.collider = collider_set
                        print_info('    Create collider set end')
                    print_info('    Create colliders end')
                    # resume particles
                    print_info('Resume simulation start')
                    pos, vel, forc = read_particles(file_path)
                    solver.particleSystemData.addParticles(pos, vel, forc)
                    print_info('Resume simulation end')
                    self.simulate(offset=last_frame)
                    break
        print_info('Create others objects end')
        print_info('-' * 79)
        print_info('SIMULATION END')
        print_info('Total time: {0}'.format(convert_time_to_string(start_time)))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window.cursor_set('WAIT')
        try:
            self.execute(context)
        finally:
            context.window.cursor_set('DEFAULT')
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBakeParticles)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeParticles)
