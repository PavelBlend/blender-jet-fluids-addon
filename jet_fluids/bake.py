
import struct
import numpy

import bpy

from . import pyjet


solvers = {
    'APIC': pyjet.ApicSolver3,
    'PIC': pyjet.PicSolver3,
    'FLIP': pyjet.FlipSolver3
}


def get_triangle_mesh(context, source):
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
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    for obj_name in selected_objects_name:
        bpy.data.objects[obj_name].select = True
    bpy.context.scene.objects.active = bpy.data.objects[active_object_name]
    return triangle_mesh


class JetFluidBake(bpy.types.Operator):
    bl_idname = "jet_fluid.bake"
    bl_label = "Bake"
    bl_options = {'REGISTER'}

    def execute(self, context):
        while self.frame.index <= self.frame_end:
            self.solver.update(self.frame)
            positions = numpy.array(self.solver.particleSystemData.positions, copy=False)
            velocities = numpy.array(self.solver.particleSystemData.velocities, copy=False)
            bin_data = b''
            bin_data += struct.pack('I', len(positions))
            for position, velocity in zip(positions, velocities):
                bin_position = struct.pack('3f', *position)
                bin_data += bin_position
                bin_velocity = struct.pack('3f', *velocity)
                bin_data += bin_velocity
            file_path = '{}{}.bin'.format(self.domain.jet_fluid.cache_folder, self.frame.index)
            file = open(file_path, 'wb')
            file.write(bin_data)
            file.close()
            context.scene.frame_set(self.frame.index)
            self.frame.advance()
        return {'FINISHED'}

    def invoke(self, context, event):
        pyjet.Logging.mute()
        obj = context.scene.objects.active
        self.domain = obj
        domain_size_x = obj.bound_box[6][0] * obj.scale[0] - obj.bound_box[0][0] * obj.scale[0]
        domain_size_y = obj.bound_box[6][1] * obj.scale[1] - obj.bound_box[0][1] * obj.scale[1]
        domain_size_z = obj.bound_box[6][2] * obj.scale[2] - obj.bound_box[0][2] * obj.scale[2]
        domain_sizes = [
            domain_size_x,
            domain_size_y,
            domain_size_z
        ]
        resolution = obj.jet_fluid.resolution
        domain_max_size = max(domain_sizes)
        resolution_x = int((domain_size_x / domain_max_size) * resolution)
        resolution_y = int((domain_size_y / domain_max_size) * resolution)
        resolution_z = int((domain_size_z / domain_max_size) * resolution)
        solver = solvers[obj.jet_fluid.solver_type](
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(
                obj.bound_box[0][0] * obj.scale[0] + obj.location[0],
                obj.bound_box[0][2] * obj.scale[2] + obj.location[2],
                obj.bound_box[0][1] * obj.scale[1] + obj.location[1]
            ),
            domainSizeX=domain_size_x
        )
        solver.viscosityCoefficient = obj.jet_fluid.viscosity
        triangle_mesh = get_triangle_mesh(context, bpy.data.objects[obj.jet_fluid.emitter])
        emitter = pyjet.VolumeParticleEmitter3(
            implicitSurface=triangle_mesh,
            spacing=domain_max_size / (resolution * obj.jet_fluid.particles_count),
            isOneShot=obj.jet_fluid.one_shot,
            initialVel=[v for v in obj.jet_fluid.velocity]
        )
        solver.particleEmitter = emitter
        collider_name = obj.jet_fluid.collider
        if collider_name:
            triangle_mesh = get_triangle_mesh(context, bpy.data.objects[obj.jet_fluid.collider])
            collider = pyjet.RigidBodyCollider3(surface=triangle_mesh)
            solver.collider = collider

        frame = pyjet.Frame(0, 1.0 / context.scene.render.fps)
        self.solver = solver
        self.frame = frame
        self.frame_end = context.scene.frame_end
        self.execute(context)
        return {'RUNNING_MODAL'}


def register():
    bpy.utils.register_class(JetFluidBake)


def unregister():
    bpy.utils.unregister_class(JetFluidBake)
