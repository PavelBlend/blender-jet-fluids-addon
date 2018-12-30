
import struct
import os
import numpy

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


def get_triangle_mesh(context, source, solver):
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
    triangle_mesh = pyjet.TriangleMesh3(
        points=[[v.co.x, v.co.z, v.co.y] for v in mesh.vertices],
        pointIndices=[[p.vertices[0], p.vertices[2], p.vertices[1]] for p in mesh.polygons]
    )
    imp_triangle_mesh = pyjet.ImplicitTriangleMesh3(mesh=triangle_mesh, resolutionX=solver.resolution.x, margin=0)
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


class JetFluidBakeMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_mesh"
    bl_label = "Bake Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pyjet.Logging.mute()
        scn = context.scene
        domain = context.object
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = calc_res(self, domain)
        solv = solvers[domain.jet_fluid.solver_type](
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=domain_size_x
        )
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = calc_res(self, domain, type='MESH')
        grid = pyjet.CellCenteredScalarGrid3(
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=self.domain_size_x
        )
        for frame_index in range(scn.frame_start, scn.frame_end + 1):
            file_path = '{}mesh_{}.bin'.format(
                bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                frame_index
            )
            if os.path.exists(file_path):
                print('skip frame', frame_index)
                continue
            else:
                print('frame', frame_index)
                file_path = '{}particles_{}.bin'.format(
                    bpy.path.abspath(domain.jet_fluid.cache_folder),
                    frame_index
                )
                if not os.path.exists(file_path):
                    print('can\'t find particles file in {} frame'.format(frame_index))
                    continue
                print('open particles file')
                particles_file = open(file_path, 'rb')
                particles_data = particles_file.read()
                particles_file.close()
                print('read particles')
                p = 0
                particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
                p += 4
                points = []
                for particle_index in range(particles_count):
                    particle_position = struct.unpack('3f', particles_data[p : p + 12])
                    p += 36    # skip velocities and forces
                    points.append(particle_position)
    
                print('create converter')
                converter = pyjet.SphPointsToImplicit3(2.0 * solv.gridSpacing.x, 0.5)
                print('convert')
                converter.convert(points, grid)
                print('meshing')
                surface_mesh = pyjet.marchingCubes(
                    grid,
                    (solv.gridSpacing.x, solv.gridSpacing.y, solv.gridSpacing.z),
                    (0, 0, 0),
                    0.0,
                    pyjet.DIRECTION_ALL
                )
                print('save verts')
                coef = self.domain.jet_fluid.resolution / self.domain.jet_fluid.resolution_mesh
                bin_mesh_data = bytearray()
                points_count = surface_mesh.numberOfPoints()
                bin_mesh_data.extend(struct.pack('I', points_count))
                for point_index in range(points_count):
                    point = surface_mesh.point(point_index)
                    bin_mesh_data.extend(struct.pack('3f', point.x * coef, point.y * coef, point.z * coef))
    
                print('save tris')
                triangles_count = surface_mesh.numberOfTriangles()
                bin_mesh_data.extend(struct.pack('I', triangles_count))
                for triangle_index in range(triangles_count):
                    tris = surface_mesh.pointIndex(triangle_index)
                    bin_mesh_data.extend(struct.pack('3I', tris.x, tris.y, tris.z))
    
                print('write file')
                file_path = '{}mesh_{}.bin'.format(
                    bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                    frame_index
                )
                file = open(file_path, 'wb')
                file.write(bin_mesh_data)
                file.close()
                print('save mesh end')
        return {'FINISHED'}


class JetFluidBake(bpy.types.Operator):
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
        print('EXECUTE START')
        solv = self.solver
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, grid_spacing = calc_res(self, self.domain, type='MESH')
        jet = self.domain.jet_fluid
        create_mesh = jet.create_mesh
        create_particles = jet.create_particles
        show_particles = jet.show_particles
        jet.create_mesh = False
        jet.create_particles = False
        jet.show_particles = False
        current_frame = self.context.scene.frame_current
        print('grid')
        while self.frame.index + offset <= self.frame_end:
            print('frame start', self.frame.index + offset)
            for emitter in self.emitters:
                jet_emmiter = self.jet_emitters_dict[emitter.name]
                vel = emitter.jet_fluid.velocity
                jet_emmiter.initialVelocity = vel[0], vel[2], vel[1]
                jet_emmiter.isOneShot = emitter.jet_fluid.one_shot
            self.context.scene.frame_set(self.frame.index + offset)
            file_path = '{}particles_{}.bin'.format(
                bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                self.frame.index + offset
            )
            print('solver update start')
            solv.update(self.frame)
            print('solver update end')
            print('start save particles')
            positions = numpy.array(solv.particleSystemData.positions, copy=False)
            velocities = numpy.array(solv.particleSystemData.velocities, copy=False)
            forces = numpy.array(solv.particleSystemData.forces, copy=False)
            print('numpy convert')
            bin_data = bytearray()
            vertices_count = len(positions)
            bin_data += struct.pack('I', vertices_count)
            print('start save position and velocity')
            for vert_index in range(vertices_count):
                bin_data.extend(struct.pack('3f', *positions[vert_index]))
                bin_data.extend(struct.pack('3f', *velocities[vert_index]))
                bin_data.extend(struct.pack('3f', *forces[vert_index]))
            file = open(file_path, 'wb')
            file.write(bin_data)
            file.close()
            print('end save particles')
            self.frame.advance()
        jet.create_mesh = create_mesh
        jet.create_particles = create_particles
        jet.show_particles = show_particles
        self.context.scene.frame_set(current_frame)
        return {'FINISHED'}

    def execute(self, context):
        print('INVOKE START')
        self.context = context
        pyjet.Logging.mute()
        obj = context.object
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = calc_res(self, obj)
        solver = solvers[obj.jet_fluid.solver_type](
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=domain_size_x
        )
        solver.maxCfl = obj.jet_fluid.max_cfl
        solver.advectionSolver = advection_solvers[obj.jet_fluid.advection_solver_type]()
        solver.diffusionSolver = diffusion_solvers[obj.jet_fluid.diffusion_solver_type]()
        solver.pressureSolver = pressure_solvers[obj.jet_fluid.pressure_solver_type]()
        solver.useCompressedLinearSystem = obj.jet_fluid.compressed_linear_system
        solver.isUsingFixedSubTimeSteps = obj.jet_fluid.fixed_substeps
        solver.numberOfFixedSubTimeSteps = obj.jet_fluid.fixed_substeps_count
        set_closed_domain_boundary_flag(solver, obj)
        solver.viscosityCoefficient = obj.jet_fluid.viscosity
        grav = obj.jet_fluid.gravity
        solver.gravity = grav[0], grav[2], grav[1]
        if obj.jet_fluid.use_scene_fps:
            frame = pyjet.Frame(0, 1.0 / context.scene.render.fps)
        else:
            frame = pyjet.Frame(0, 1.0 / obj.jet_fluid.fps)
        self.solver = solver
        self.frame = frame
        self.frame_end = context.scene.frame_end
        for frame_index in range(0, self.frame_end):
            file_path = '{}particles_{}.bin'.format(
                bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                frame_index
            )
            if os.path.exists(file_path):
                print('skip frame', frame_index)
                continue
            else:
                if frame_index == 0:
                    emitters, colliders = self.find_emitters_and_colliders()
                    jet_emitters = []
                    self.jet_emitters_dict = {}
                    for emitter_object in emitters:
                        triangle_mesh = get_triangle_mesh(context, emitter_object, solver)
                        init_vel = emitter_object.jet_fluid.velocity
                        emitter = pyjet.VolumeParticleEmitter3(
                            implicitSurface=triangle_mesh,
                            spacing=self.domain_max_size / (obj.jet_fluid.resolution * emitter_object.jet_fluid.particles_count),
                            isOneShot=emitter_object.jet_fluid.one_shot,
                            initialVelocity=[init_vel[0], init_vel[2], init_vel[1]]
                        )
                        self.jet_emitters_dict[emitter_object.name] = emitter
                        jet_emitters.append(emitter)
                    self.emitters = emitters
                    emitter_set = pyjet.ParticleEmitterSet3(emitters=jet_emitters)
                    solver.particleEmitter = emitter_set
                    # set colliders
                    jet_colliders = []
                    for collider_object in colliders:
                        triangle_mesh = get_triangle_mesh(context, collider_object, solver)
                        jet_colliders.append(triangle_mesh)
                    if jet_colliders:
                        collider_surface = pyjet.SurfaceSet3(others=jet_colliders)
                        collider = pyjet.RigidBodyCollider3(surface=collider_surface)
                        solver.collider = collider
                    # simulate
                    self.simulate()
                    break
                else:
                    last_frame = frame_index - 1
                    file_path = '{}particles_{}.bin'.format(
                        bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                        last_frame
                    )
                    emitters, colliders = self.find_emitters_and_colliders()
                    jet_emitters = []
                    self.jet_emitters_dict = {}
                    for emitter_object in emitters:
                        if not emitter_object.jet_fluid.one_shot:
                            triangle_mesh = get_triangle_mesh(context, emitter_object, solver)
                            init_vel = emitter_object.jet_fluid.velocity
                            emitter = pyjet.VolumeParticleEmitter3(
                                implicitSurface=triangle_mesh,
                                spacing=self.domain_max_size / (obj.jet_fluid.resolution * emitter_object.jet_fluid.particles_count),
                                isOneShot=emitter_object.jet_fluid.one_shot,
                                initialVelocity=[init_vel[0], init_vel[2], init_vel[1]]
                            )
                            self.jet_emitters_dict[emitter_object.name] = emitter
                            jet_emitters.append(emitter)
                    self.emitters = emitters
                    emitter_set = pyjet.ParticleEmitterSet3(emitters=jet_emitters)
                    solver.particleEmitter = emitter_set
                    # set colliders
                    jet_colliders = []
                    for collider_object in colliders:
                        triangle_mesh = get_triangle_mesh(context, collider_object, solver)
                        jet_colliders.append(triangle_mesh)
                    if jet_colliders:
                        collider_surface = pyjet.SurfaceSet3(others=jet_colliders)
                        collider = pyjet.RigidBodyCollider3(surface=collider_surface)
                        solver.collider = collider
                    # resume particles
                    pos, vel, forc = read_particles(file_path)
                    solver.particleSystemData.addParticles(pos, vel, forc)
                    self.simulate(offset=last_frame)
                    break
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBake)
    bpy.utils.register_class(JetFluidBakeMesh)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeMesh)
    bpy.utils.unregister_class(JetFluidBake)
