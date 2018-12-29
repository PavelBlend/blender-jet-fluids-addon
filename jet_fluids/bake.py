
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
        frame_index = scn.frame_start
        while frame_index <= scn.frame_end:
            print('frame', frame_index)
            file_path = '{}particles_{}.bin'.format(
                bpy.path.abspath(domain.jet_fluid.cache_folder),
                frame_index
            )
            if not os.path.exists(file_path):
                frame_index += 1
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
            frame_index += 1
        return {'FINISHED'}


class JetFluidBake(bpy.types.Operator):
    bl_idname = "jet_fluid.bake"
    bl_label = "Bake Particles"
    bl_options = {'REGISTER'}

    def simulate(self, offset=0):
        print('EXECUTE START')
        solv = self.solver
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, grid_spacing = calc_res(self, self.domain, type='MESH')
        print('grid')
        while self.frame.index + offset <= self.frame_end:
            print('frame start', self.frame.index + offset)
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
        return {'FINISHED'}

    def execute(self, context):
        print('INVOKE START')
        pyjet.Logging.mute()
        obj = context.scene.objects.active
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = calc_res(self, obj)
        solver = solvers[obj.jet_fluid.solver_type](
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=domain_size_x
        )
        solver.useCompressedLinearSystem = True
        solver.viscosityCoefficient = obj.jet_fluid.viscosity
        frame = pyjet.Frame(0, 1.0 / context.scene.render.fps)
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
                    triangle_mesh = get_triangle_mesh(context, bpy.data.objects[obj.jet_fluid.emitter], solver)
                    emitter = pyjet.VolumeParticleEmitter3(
                        implicitSurface=triangle_mesh,
                        spacing=self.domain_max_size / (obj.jet_fluid.resolution * obj.jet_fluid.particles_count),
                        isOneShot=obj.jet_fluid.one_shot,
                        initialVel=[v for v in obj.jet_fluid.velocity]
                    )
                    solver.particleEmitter = emitter
                    collider_name = obj.jet_fluid.collider
                    if collider_name:
                        triangle_mesh = get_triangle_mesh(context, bpy.data.objects[obj.jet_fluid.collider], solver)
                        collider = pyjet.RigidBodyCollider3(surface=triangle_mesh)
                        solver.collider = collider
                    self.simulate()
                    break
                else:
                    last_frame = frame_index - 1
                    file_path = '{}particles_{}.bin'.format(
                        bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                        last_frame
                    )
                    if not obj.jet_fluid.one_shot:
                        triangle_mesh = get_triangle_mesh(context, bpy.data.objects[obj.jet_fluid.emitter], solver)
                        emitter = pyjet.VolumeParticleEmitter3(
                            implicitSurface=triangle_mesh,
                            spacing=self.domain_max_size / (obj.jet_fluid.resolution * obj.jet_fluid.particles_count),
                            isOneShot=obj.jet_fluid.one_shot,
                            initialVel=[v for v in obj.jet_fluid.velocity]
                        )
                        solver.particleEmitter = emitter
                    collider_name = obj.jet_fluid.collider
                    if collider_name:
                        triangle_mesh = get_triangle_mesh(context, bpy.data.objects[obj.jet_fluid.collider], solver)
                        collider = pyjet.RigidBodyCollider3(surface=triangle_mesh)
                        solver.collider = collider
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
