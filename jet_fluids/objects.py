
import bpy

from . import create


class JetFluidsProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Object

    is_active = bpy.props.BoolProperty(default=False)

    # simulate props
    items = [
        ('APIC', 'APIC', ''),
        ('PIC', 'PIC', ''),
        ('FLIP', 'FLIP', '')
    ]
    solver_type = bpy.props.EnumProperty(
        items=items, name='Fluid Solver', default='PIC'
    )
    resolution = bpy.props.IntProperty(default=30, name='Simulate Resolution')
    resolution_mesh = bpy.props.IntProperty(default=30, name='Mesh Resolution')
    particles_count = bpy.props.FloatProperty(
        default=1.0,
        name='Particles',
        min=1.0
    )

    # cache props
    cache_folder = bpy.props.StringProperty(
        default='',
        name='Cache Folder',
        subtype='DIR_PATH'
    )

    # world props
    viscosity = bpy.props.FloatProperty(default=0.0, name='Viscosity')

    # emitter props
    emitter = bpy.props.StringProperty(default='', name='Emitter')
    velocity = bpy.props.FloatVectorProperty(default=(0, 0, 0), name='Velocity')
    one_shot = bpy.props.BoolProperty(default=False, name='One Shot')

    # collider props
    collider = bpy.props.StringProperty(default='', name='Collider')

    # create props
    create_mesh = bpy.props.BoolProperty(
        default=True,
        name='Create Mesh',
        update=create.update_par_object
    )
    mesh_object = bpy.props.StringProperty(default='', name='Mesh')
    create_particles = bpy.props.BoolProperty(
        default=False,
        name='Create Particles',
        update=create.update_par_object
    )
    particles_object = bpy.props.StringProperty(default='', name='Particles')

    # debug props
    show_particles = bpy.props.BoolProperty(default=True, name='Show Particles')
    items = [
        ('VELOCITY', 'Velocity', ''),
        ('SINGLE_COLOR', 'Single Color', '')
    ]
    color_type = bpy.props.EnumProperty(
        items=items,
        name='Color',
        default='VELOCITY',
        update=create.update_particles_cache
    )
    color_1 = bpy.props.FloatVectorProperty(
        default=(0.0, 0.0, 1.0),
        name='Color 1',
        subtype='COLOR',
        max=1.0,
        min=0.0
    )
    color_2 = bpy.props.FloatVectorProperty(
        default=(0.0, 1.0, 1.0),
        name='Color 2',
        subtype='COLOR',
        max=1.0,
        min=0.0
    )
    max_velocity = bpy.props.FloatProperty(
        default=10.0,
        name='Max Velocity',
        min=0.001
    )


__CLASSES__ = [
    JetFluidsProperties,
]

def register():
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)
        class_.bpy_type.jet_fluid = bpy.props.PointerProperty(type=class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        del class_.bpy_type.jet_fluid
        bpy.utils.unregister_class(class_)
