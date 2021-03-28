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
        ('APIC', 'APIC', ''),
        ('PIC', 'PIC', ''),
        ('FLIP', 'FLIP', '')
    ]
    solver_type: bpy.props.EnumProperty(
        items=items, name='Fluid Solver', default='PIC'
    )
    items = [
        ('SEMI_LAGRANGIAN', 'Semi-Lagrangian', ''),
        ('CUBIC_SEMI_LAGRANGIAN', 'Cubic Semi-Lagrangian', '')
    ]
    advection_solver_type: bpy.props.EnumProperty(
        items=items, name='Advection Solver', default='SEMI_LAGRANGIAN'
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
        items=items, name='Pressure Solver', default='SINGLE_PHASE'
    )
    resolution: bpy.props.IntProperty(default=30, name='Simulate Resolution')
    max_cfl: bpy.props.FloatProperty(default=5.0, name='Max CFL')
    compressed_linear_system: bpy.props.BoolProperty(
        default=False, name='Compressed Linear System'
    )
    fixed_substeps: bpy.props.BoolProperty(
        default=False, name='Fixed Substeps'
    )
    fixed_substeps_count: bpy.props.IntProperty(
        default=1, name='Substeps Count'
    )
    use_scene_fps: bpy.props.BoolProperty(default=True, name='Use Scene FPS')
    fps: bpy.props.FloatProperty(default=30.0, name='FPS')
    items = [
        ('TIMELINE', 'Timeline', ''),
        ('CUSTOM', 'Custom', '')
    ]
    frame_range_simulation: bpy.props.EnumProperty(
        items=items,
        name='Frame Range',
        default='TIMELINE'
    )
    frame_range_simulation_start: bpy.props.IntProperty(
        default=0,
        name='Start Frame',
        min=0
    )
    frame_range_simulation_end: bpy.props.IntProperty(
        default=50,
        name='End Frame',
        min=0
    )
    overwrite_simulation: bpy.props.BoolProperty(
        default=False, name='Overwrite'
    )

    # mesh generator properties
    resolution_mesh: bpy.props.IntProperty(default=30, name='Mesh Resolution')
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
        default=1.0, name='Kernel Radius', min=0.1, max=10.0
    )
    cut_off_density: bpy.props.FloatProperty(
        default=0.5, name='Cut Off Density'
    )
    position_smoothing_factor: bpy.props.FloatProperty(
        default=0.5, name='Position Smoothing Factor'
    )
    min_num_neighbors: bpy.props.IntProperty(
        default=25,
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
        ('TIMELINE', 'Timeline', ''),
        ('CUSTOM', 'Custom', ''),
        ('CURRENT_FRAME', 'Current Frame', '')
    ]
    frame_range_mesh: bpy.props.EnumProperty(
        items=items,
        name='Frame Range',
        default='TIMELINE'
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
    color_particles_search_radius: bpy.props.FloatProperty(
        default=0.1,
        name='Particles Search Radius',
        min=0.0
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
    viscosity: bpy.props.FloatProperty(default=0.0, name='Viscosity')
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
        default=0.0,
        name='Jitter'
    )
    allow_overlapping: bpy.props.BoolProperty(
        default=False,
        name='Allow Overlapping'
    )
    emitter_seed: bpy.props.IntProperty(
        default=0,
        name='Seed'
    )
    max_number_of_particles: bpy.props.IntProperty(
        default=12000000,
        name='Max Number of Particles'
    )

    # colors
    use_colors: bpy.props.BoolProperty(
        default=False,
        name='Use Colors'
    )
    items = [
        ('VERTEX_COLOR', 'Emitter Vertex Color', ''),
        ('SINGLE_COLOR', 'Domain Single Color', ''),
        ('TEXTURE', 'Texture', '')
    ]
    simmulate_color_type: bpy.props.EnumProperty(
        items=items,
        name='Color Type',
        default='VERTEX_COLOR'
    )
    particles_color: bpy.props.FloatVectorProperty(
        default=(1.0, 1.0, 1.0, 1.0),
        name='Particles Color',
        subtype='COLOR',
        size=4,
        max=1.0,
        min=0.0
    )
    color_vertex_search_radius: bpy.props.FloatProperty(
        default=0.1,
        name='Vertex Search Radius',
        min=0.0
    )
    particles_texture: bpy.props.StringProperty(
        default='',
        name='Particles Texture'
    )

    # collider props
    friction_coefficient: bpy.props.FloatProperty(
        default=0.0,
        name='Friction Coefficient',
        min=0.0
    )

    # create props
    create_mesh: bpy.props.BoolProperty(
        default=True,
        name='Create Mesh',
        update=create.update_mesh_object
    )
    mesh_object: bpy.props.StringProperty(default='', name='Mesh')
    create_particles: bpy.props.BoolProperty(
        default=False,
        name='Create Particles',
        update=create.update_par_object
    )
    particles_object: bpy.props.StringProperty(default='', name='Particles')

    # debug props
    show_particles: bpy.props.BoolProperty(
        default=False, name='Show Particles'
    )
    particle_size: bpy.props.IntProperty(
        default=3,
        name='Particle Size',
        min=1,
        max=10
    )
    items = [
        ('VELOCITY', 'Velocity', ''),
        ('SINGLE_COLOR', 'Single Color', ''),
        ('PARTICLE_COLOR', 'Particle Color', '')
    ]
    color_type: bpy.props.EnumProperty(
        items=items,
        name='Color',
        default='VELOCITY',
        update=create.update_particles_cache
    )
    color_1: bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 1.0),
        name='Color 1',
        subtype='COLOR',
        max=1.0,
        min=0.0
    )
    color_2: bpy.props.FloatVectorProperty(
        default=(0.0, 1.0, 1.0),
        name='Color 2',
        subtype='COLOR',
        max=1.0,
        min=0.0
    )
    max_velocity: bpy.props.FloatProperty(
        default=10.0,
        name='Max Velocity',
        min=0.001
    )
    print_debug_info: bpy.props.BoolProperty(
        default=True, name='Print Information to the Console'
    )
    write_log: bpy.props.BoolProperty(
        default=True, name='Write Log File'
    )

    # convert props
    items = [
        ('TIMELINE', 'Timeline', ''),
        ('CUSTOM', 'Custom', ''),
        ('CURRENT_FRAME', 'Current Frame', '')
    ]
    frame_range_convert: bpy.props.EnumProperty(
        items=items,
        name='Frame Range',
        default='TIMELINE'
    )
    frame_range_convert_start: bpy.props.IntProperty(
        default=0,
        name='Start Frame',
        min=0
    )
    frame_range_convert_end: bpy.props.IntProperty(
        default=50,
        name='End Frame',
        min=0
    )
    overwrite_convert: bpy.props.BoolProperty(
        default=False, name='Overwrite'
    )
    items = [
        ('VERTICES', 'Vertices', ''),
        ('PARTICLES', 'Particles', '')
    ]
    input_data_type: bpy.props.EnumProperty(
        items=items,
        name='Input Data Type',
        default='VERTICES'
    )
    input_vertices_object: bpy.props.StringProperty(default='', name='Input Object')


__CLASSES__ = [
    JetFluidsProperties,
]

def register():
    bpy.types.Scene.jet_fluid_domain_object = bpy.props.StringProperty()
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)
        class_.bpy_type.jet_fluid = bpy.props.PointerProperty(type=class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        del class_.bpy_type.jet_fluid
        bpy.utils.unregister_class(class_)
    del bpy.types.Scene.jet_fluid_domain_object
