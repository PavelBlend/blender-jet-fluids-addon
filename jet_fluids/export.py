
import bpy


from . import pyjet
from . import bake
from . import bake_particles


solvers = {
    'APIC': 'pyjet.ApicSolver3',
    'PIC': 'pyjet.PicSolver3',
    'FLIP': 'pyjet.FlipSolver3'
}
advection_solvers = {
    'SEMI_LAGRANGIAN': 'pyjet.SemiLagrangian3',
    'CUBIC_SEMI_LAGRANGIAN': 'pyjet.CubicSemiLagrangian3'
}
diffusion_solvers = {
    'FORWARD_EULER': 'pyjet.GridForwardEulerDiffusionSolver3',
    'BACKWARD_EULER': 'pyjet.GridBackwardEulerDiffusionSolver3'
}
pressure_solvers = {
    'FRACTIONAL_SINGLE_PHASE': 'pyjet.GridFractionalSinglePhasePressureSolver3',
    'SINGLE_PHASE': 'pyjet.GridSinglePhasePressureSolver3'
}


def add_collider(code, context, collider_object, solver, obj, domain_max_size):
    code = get_triangle_mesh(code, context, collider_object, solver, obj)
    return code
    


def add_emitter(code, context, emitter_object, solver, obj, domain_max_size):
    code = get_triangle_mesh(code, context, emitter_object, solver, obj)
    init_vel = emitter_object.jet_fluid.velocity
    code += '''emitter = pyjet.VolumeParticleEmitter3(
implicitSurface={},
spacing={},
isOneShot={},
initialVelocity={},
jitter={},
allowOverlapping={},
seed={},
maxNumberOfParticles={}
)
emitters.append(emitter)\n'''.format(
            'triangle_mesh',
            domain_max_size / (obj.jet_fluid.resolution * emitter_object.jet_fluid.particles_count),
            emitter_object.jet_fluid.one_shot,
            [init_vel[0], init_vel[2], init_vel[1]],
            emitter_object.jet_fluid.emitter_jitter,
            emitter_object.jet_fluid.allow_overlapping,
            emitter_object.jet_fluid.emitter_seed,
            emitter_object.jet_fluid.max_number_of_particles
        )
    return code


def get_triangle_mesh(code, context, source, solver, domain_object):
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
    obj_file = open(bpy.path.abspath(domain_object.jet_fluid.cache_folder) + source.name + '.obj', 'w')
    points=[[v.co.x, v.co.z, v.co.y] for v in mesh.vertices]
    pointIndices=[[p.vertices[0], p.vertices[2], p.vertices[1]] for p in mesh.polygons]
    for point in points:
        obj_file.write('v {} {} {}\n'.format(point[0], point[1], point[2]))
    for pointIndex in pointIndices:
        obj_file.write('f {} {} {}\n'.format(pointIndex[0], pointIndex[1], pointIndex[2]))
    obj_file.close()
    code += 'triangle_mesh = pyjet.TriangleMesh3()\n'.format()
    code += 'triangle_mesh.readObj("{}")\n'.format(source.name + '.obj')
    res_x = int(round(obj.dimensions[0] / domain_object.dimensions[0] * solver.resolution.x, 0))
    code += 'imp_triangle_mesh = pyjet.ImplicitTriangleMesh3(mesh={}, resolutionX={}, margin=0.2)\n'.format('triangle_mesh', res_x)
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(mesh)
    for obj_name in selected_objects_name:
        bpy.data.objects[obj_name].select = True
    bpy.context.scene.objects.active = bpy.data.objects[active_object_name]
    return code


class JetFluidExportToScript(bpy.types.Operator):
    bl_idname = "jet_fluid.export_to_script"
    bl_label = "Export to Script"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        res_x, res_y, res_z, orig_x, orig_y, orig_z, size_x, _ = bake.calc_res(self, obj)
        solver = bake.solvers[obj.jet_fluid.solver_type](
            resolution=(res_x, res_z, res_z),
            gridOrigin=(orig_x, orig_z, orig_y),
            domainSizeX=size_x
        )
        code = 'import pyjet\n\n'
        code += 'solver = {}(resolution=({}, {}, {}), gridOrigin=({}, {}, {}), domainSizeX={})\n'.format(
            solvers[obj.jet_fluid.solver_type],
            res_x, res_y, res_z,
            orig_x, orig_y, orig_z,
            size_x
        )
        code += 'solver.maxCfl = {}\n'.format(obj.jet_fluid.max_cfl)
        code += 'solver.advectionSolver = {}()\n'.format(advection_solvers[obj.jet_fluid.advection_solver_type])
        code += 'solver.diffusionSolver = {}()\n'.format(diffusion_solvers[obj.jet_fluid.diffusion_solver_type])
        code += 'solver.pressureSolver = {}()\n'.format(pressure_solvers[obj.jet_fluid.pressure_solver_type])
        code += 'solver.useCompressedLinearSystem = {}\n'.format(obj.jet_fluid.compressed_linear_system)
        code += 'solver.isUsingFixedSubTimeSteps = {}\n'.format(obj.jet_fluid.fixed_substeps)
        code += 'solver.numberOfFixedSubTimeSteps = {}\n'.format(obj.jet_fluid.fixed_substeps_count)
        bake.set_closed_domain_boundary_flag(solver, obj)
        code += 'solver.closedDomainBoundaryFlag = {}\n'.format(solver.closedDomainBoundaryFlag)
        code += 'solver.viscosityCoefficient = {}\n'.format(obj.jet_fluid.viscosity)
        grav = obj.jet_fluid.gravity
        code += 'solver.gravity = ({}, {}, {})\n'.format(grav[0], grav[2], grav[1])
        if obj.jet_fluid.use_scene_fps:
            code += 'frame = pyjet.Frame(0, 1.0 / {})\n'.format(context.scene.render.fps)
        else:
            code += 'frame = pyjet.Frame(0, 1.0 / {})\n'.format(obj.jet_fluid.fps)
        frame_end = context.scene.frame_end
        emitters, colliders = bake_particles.find_emitters_and_colliders()
        code += 'emitters = []\n'
        for emitter_object in emitters:
            code = add_emitter(code, context, emitter_object, solver, obj, self.domain_max_size)
        code += 'emitter_set = pyjet.ParticleEmitterSet3(emitters=emitters)\n'
        code += 'solver.particleEmitter = emitter_set\n'
        code += 'colliders = []\n'
        for collider_object in colliders:
            code = add_collider(code, context, collider_object, solver, obj, self.domain_max_size)
            code += 'colliders.append(imp_triangle_mesh)\n'
        code += 'collider_surface = pyjet.SurfaceSet3(others=colliders)\n'
        code += 'collider = pyjet.RigidBodyCollider3(surface=collider_surface)\n'
        code += 'solver.collider = collider\n'
        code += 'for frame_index in range(0, {}):\n'.format(context.scene.frame_end)
        code += '    print("frame", frame_index)\n'
        code += '    solver.update(frame)\n'
        code += '    frame.advance()\n'
        code_file = open(bpy.path.abspath(obj.jet_fluid.cache_folder) + 'jet_fluid.py', 'w')
        code_file.write(code)
        code_file.close()
        return {'FINISHED'}


__CLASSES__ = [
    JetFluidExportToScript,
]


def register():
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
