import bpy

from . import create


def update_object_draw_type(self, context):
    obj = context.object
    jet = obj.jet_fluid
    if jet.object_type == 'DOMAIN':
        obj.display_type = 'BOUNDS'
    elif jet.object_type == 'EMITTER':
        obj.display_type = 'WIRE'
    elif jet.object_type == 'COLLIDER' or jet.object_type == 'NONE':
        obj.display_type = 'TEXTURED'


class JetFluidsProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Object

    is_active: bpy.props.BoolProperty(default=False)

    # object type
    items = [
        ('NONE', 'None', ''),
        ('DOMAIN', 'Domain', ''),
        ('EMITTER', 'Emitter', ''),
        ('COLLIDER', 'Collider', '')
    ]
    object_type: bpy.props.EnumProperty(
        items=items,
        name='Fluid Type',
        default='NONE',
        update=update_object_draw_type
    )

    # simulate props
    items = [
        ('PIC', 'PIC', ''),
        ('FLIP', 'FLIP', ''),
        ('APIC', 'APIC', '')
    ]
    solver_type: bpy.props.EnumProperty(
        items=items, name='Fluid Solver', default='APIC'
    )
    items = [
        ('SEMI_LAGRANGIAN', 'Semi-Lagrangian', ''),
        ('CUBIC_SEMI_LAGRANGIAN', 'Cubic Semi-Lagrangian', '')
    ]
    advection_solver_type: bpy.props.EnumProperty(
        items=items, name='Advection Solver', default='CUBIC_SEMI_LAGRANGIAN'
    )
    items = [
        ('FORWARD_EULER', 'Forward Euler', ''),
        ('BACKWARD_EULER', 'Backward Euler', '')
    ]
    diffusion_solver_type: bpy.props.EnumProperty(
        items=items, name='Diffusion Solver', default='BACKWARD_EULER'
    )
    items = [
        ('SINGLE_PHASE', 'Single Phase', ''),
        ('FRACTIONAL_SINGLE_PHASE', 'Fractional Single Phase', '')
    ]
    pressure_solver_type: bpy.props.EnumProperty(
        items=items, name='Pressure Solver', default='FRACTIONAL_SINGLE_PHASE'
    )
    resolution: bpy.props.IntProperty(default=30, name='Simulate Resolution', min=1)
    max_cfl: bpy.props.FloatProperty(default=5.0, name='Max CFL', min=1.0)
    compressed_linear_system: bpy.props.BoolProperty(
        default=True, name='Compressed Linear System'
    )
    fixed_substeps: bpy.props.BoolProperty(
        default=False, name='Fixed Substeps'
    )
    fixed_substeps_count: bpy.props.IntProperty(
        default=1, name='Substeps Count', min=1
    )
    items = [
        ('SCENE', 'Scene', ''),
        ('CUSTOM', 'Custom', '')
    ]
    fps_mode: bpy.props.EnumProperty(
        items=items,
        name='FPS Mode',
        default='SCENE'
    )
    fps: bpy.props.FloatProperty(default=30.0, name='FPS')
    frame_range_simulation: bpy.props.EnumProperty(
        items=items,
        name='Frame Range',
        default='SCENE'
    )
    frame_range_simulation_start: bpy.props.IntProperty(
        default=0,
        name='Frame Start',
        min=0
    )
    frame_range_simulation_end: bpy.props.IntProperty(
        default=50,
        name='Frame End',
        min=0
    )
    overwrite_simulation: bpy.props.BoolProperty(
        default=False, name='Overwrite'
    )

    # mesh generator properties
    resolution_mesh: bpy.props.IntProperty(default=30, name='Mesh Resolution', min=1)
    items = [
        ('ANISOTROPICPOINTSTOIMPLICIT', 'Anisotropic Points to Implicit', ''),
        ('SPHPOINTSTOIMPLICIT', 'SPH Points to Implicit', ''),
        ('SPHERICALPOINTSTOIMPLICIT', 'Spherical Points to Implicit', ''),
        ('ZHUBRIDSONPOINTSTOIMPLICIT', 'Zhu Bridson Points to Implicit', '')
    ]
    converter_type: bpy.props.EnumProperty(
        items=items,
        name='Converter Type',
        default='ANISOTROPICPOINTSTOIMPLICIT'
    )

    # Anisotropic Points to Implicit Properties
    kernel_radius: bpy.props.FloatProperty(
        default=1.25, name='Kernel Radius', min=0.1, max=10.0
    )
    cut_off_density: bpy.props.FloatProperty(
        default=0.05, name='Cut Off Density'
    )
    position_smoothing_factor: bpy.props.FloatProperty(
        default=0.5, name='Position Smoothing Factor'
    )
    min_num_neighbors: bpy.props.IntProperty(
        default=25,
        min=0,
        name='Min Num Neighbors'
    )
    is_output_sdf: bpy.props.BoolProperty(
        default=True, name='Is Out SDF'
    )
    radius: bpy.props.FloatProperty(
        default=1.0, name='Radius'
    )
    cut_off_threshold: bpy.props.FloatProperty(
        default=0.25, name='Cut Off Threshold'
    )

    # SphPointsToImplicit3 properties
    iso_value: bpy.props.FloatProperty(
        default=0.0, name='Iso Value'
    )
    items = [
        ('SCENE', 'Scene', ''),
        ('CURRENT_FRAME', 'Current Frame', ''),
        ('CUSTOM', 'Custom', '')
    ]
    frame_range_mesh: bpy.props.EnumProperty(
        items=items,
        name='Frame Range',
        default='SCENE'
    )
    frame_range_mesh_start: bpy.props.IntProperty(
        default=0,
        name='Start Frame',
        min=0
    )
    frame_range_mesh_end: bpy.props.IntProperty(
        default=50,
        name='End Frame',
        min=0
    )
    overwrite_mesh: bpy.props.BoolProperty(
        default=False, name='Overwrite'
    )

    # boundary
    bound_right: bpy.props.BoolProperty(default=True, name='Right')
    bound_left: bpy.props.BoolProperty(default=True, name='Left')

    bound_front: bpy.props.BoolProperty(default=True, name='Front')
    bound_back: bpy.props.BoolProperty(default=True, name='Back')

    bound_up: bpy.props.BoolProperty(default=True, name='Up')
    bound_down: bpy.props.BoolProperty(default=True, name='Down')

    # connectivity
    con_right: bpy.props.BoolProperty(default=True, name='Right')
    con_left: bpy.props.BoolProperty(default=True, name='Left')

    con_front: bpy.props.BoolProperty(default=True, name='Front')
    con_back: bpy.props.BoolProperty(default=True, name='Back')

    con_up: bpy.props.BoolProperty(default=True, name='Up')
    con_down: bpy.props.BoolProperty(default=True, name='Down')

    # close
    close_right: bpy.props.BoolProperty(default=True, name='Right')
    close_left: bpy.props.BoolProperty(default=True, name='Left')

    close_front: bpy.props.BoolProperty(default=True, name='Front')
    close_back: bpy.props.BoolProperty(default=True, name='Back')

    close_up: bpy.props.BoolProperty(default=True, name='Up')
    close_down: bpy.props.BoolProperty(default=True, name='Down')

    # cache props
    cache_folder: bpy.props.StringProperty(
        default='',
        name='Cache Folder',
        subtype='DIR_PATH'
    )

    # world props
    viscosity: bpy.props.FloatProperty(default=0.0, name='Viscosity', min=0.0)
    gravity: bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, -9.8),
        name='Gravity'
    )

    # emitter props
    velocity: bpy.props.FloatVectorProperty(
        default=(0, 0, 0), name='Velocity'
    )
    one_shot: bpy.props.BoolProperty(default=False, name='One Shot')
    is_enable: bpy.props.BoolProperty(default=True, name='Enable')
    particles_count: bpy.props.FloatProperty(
        default=1.0,
        name='Particles',
        min=0.001
    )
    emitter_jitter: bpy.props.FloatProperty(
        default=10.0,
        name='Jitter',
        min=0.0,
        max=10.0,
        precision=3
    )
    allow_overlapping: bpy.props.BoolProperty(
        default=False,
        name='Allow Overlapping'
    )
    emitter_seed: bpy.props.IntProperty(
        default=0,
        min=0,
        name='Seed'
    )
    max_number_of_particles: bpy.props.IntProperty(
        default=12000000,
        min=0,
        name='Max Number of Particles'
    )

    # collider props
    collider_friction: bpy.props.FloatProperty(
        default=0.0,
        name='Friction Coefficient',
        min=0.0,
        max=1.0,
        precision=3,
        subtype='FACTOR'
    )

    # create props
    create_mesh: bpy.props.BoolProperty(
        default=True,
        name='Create Mesh',
        update=create.update_mesh_object
    )
    mesh_object: bpy.props.StringProperty(default='', name='Mesh')
    create_particles: bpy.props.BoolProperty(
        default=True,
        name='Create Particles',
        update=create.update_par_object
    )
    particles_object: bpy.props.StringProperty(default='', name='Particles')


def register():
    bpy.utils.register_class(JetFluidsProperties)
    props = bpy.props.PointerProperty(type=JetFluidsProperties)
    JetFluidsProperties.bpy_type.jet_fluid = props


def unregister():
    del JetFluidsProperties.bpy_type.jet_fluid
    bpy.utils.unregister_class(JetFluidsProperties)
