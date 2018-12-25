
import bpy


class JetFluidsProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Object
    is_active = bpy.props.BoolProperty(default=False)
    items = [('APIC', 'APIC', ''), ]
    solver_type = bpy.props.EnumProperty(
        items=items, name='Fluid Solver', default='APIC'
    )
    resolution = bpy.props.IntProperty(default=30, name='Resolution')
    particles_count = bpy.props.FloatProperty(default=2.0, name='Particles', min=1.0)
    viscosity = bpy.props.FloatProperty(default=0.0, name='Viscosity')
    emitter = bpy.props.StringProperty(default='', name='Emitter')
    velocity = bpy.props.FloatVectorProperty(default=(0, 0, 0), name='Velocity')
    one_shot = bpy.props.BoolProperty(default=False, name='One Shot')
    collider = bpy.props.StringProperty(default='', name='Collider')
    show_particles = bpy.props.BoolProperty(default=True, name='Show Particles')
    cache_folder = bpy.props.StringProperty(default='', name='Cache Folder', subtype='DIR_PATH')


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
