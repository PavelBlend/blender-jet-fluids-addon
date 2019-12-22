import bpy

from . import pyjet, bake, bake_mesh, bake_particles
from .utils import print_info


def get_emitter(solver, solver_object):
    source = None
    for obj in bpy.data.objects:
        if obj.jet_fluid.object_type == 'EMITTER':
            source = obj
            break
    implicit_triangle_mesh = bake.get_triangle_mesh(bpy.context, source, solver, solver_object)
    emitter = pyjet.VolumeGridEmitter3(implicit_triangle_mesh, True)
    emitter.addSignedDistanceTarget(solver.signedDistanceField)
    pos, rot = bake_particles.get_transforms(source)
    transform = pyjet.Transform3(
        translation=(pos[0], pos[2], pos[1]),
        orientation=(-rot[0], rot[1], rot[3], rot[2])
    )
    emitter.sourceRegion.transform = transform
    return emitter


def get_frame_range(solver_object):
    jet = solver_object.jet_fluid

    if jet.frame_range_simulation == 'CUSTOM':
        frame_start = jet.frame_range_simulation_start
        frame_end = jet.frame_range_simulation_end
    elif jet.frame_range_simulation == 'TIMELINE':
        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end
    else:
        frame_start = bpy.context.scene.frame_current
        frame_end = bpy.context.scene.frame_current

    return frame_start, frame_end


def create_solver(operator, solver_object):
    (
        resolution_x, resolution_y, resolution_z,
        origin_x, origin_y, origin_z,
        domain_size_x, grid_spacing
    ) = bake.calc_res(operator, solver_object)
    solver = pyjet.LevelSetLiquidSolver3(
        resolution=(resolution_x, resolution_z, resolution_y),
        gridSpacing=grid_spacing,
        gridOrigin=(origin_x, origin_z, origin_y),
        domainSizeX=domain_size_x
    )
    return solver


def create_frame_object(solver_object):
    if solver_object.jet_fluid.use_scene_fps:
        frame = pyjet.Frame(0, 1.0 / bpy.context.scene.render.fps)
    else:
        frame = pyjet.Frame(0, 1.0 / solver_object.jet_fluid.fps)
    return frame


def get_mesh(operator, solver):
    sdf = solver.signedDistanceField
    surface_mesh = pyjet.marchingCubes(
        sdf,
        solver.gridSpacing,
        (0, 0, 0),
        0.0, 0, 0
    )
    return surface_mesh


def simulate(solver, frame, frame_start, frame_end, operator, solver_object):
    for frame_index in range(frame_start, frame_end):
        print_info('Frame start', frame.index)
        solver.update(frame)
        mesh = get_mesh(operator, solver)
        bake_mesh.save_mesh(operator, mesh, frame_index, None, None)
        frame.advance()
        print_info('Frame end', frame.index)
        print_info('-' * 79)


def run_simulation(operator, solver_object):
    pyjet.Logging.mute()
    bake_mesh.domain = solver_object
    solver = create_solver(operator, solver_object)
    frame = create_frame_object(solver_object)
    frame_start, frame_end = get_frame_range(solver_object)
    emitter = get_emitter(solver, solver_object)
    solver.emitter = emitter
    simulate(solver, frame, frame_start, frame_end, operator, solver_object)


class JetFluidBakeFluid(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_fluid"
    bl_label = "Bake Fluid"
    bl_options = {'REGISTER'}

    def execute(self, context):
        solver_object = context.object
        self.domain = solver_object
        run_simulation(self, solver_object)
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBakeFluid)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeFluid)
