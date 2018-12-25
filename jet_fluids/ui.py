
import bpy


class JetFluidPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_category = "Jet Fluid"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        obj_props = context.scene.objects.active.jet_fluid
        return obj_props.is_active

    def draw(self, context):
        obj = context.scene.objects.active
        obj_props = obj.jet_fluid
        self.layout.operator('jet_fluid.bake')
        self.layout.prop(obj_props, 'solver_type')
        self.layout.prop(obj_props, 'resolution')
        self.layout.prop(obj_props, 'particles_count')
        self.layout.prop(obj_props, 'viscosity')
        self.layout.prop_search(obj_props, 'emitter', bpy.data, 'objects')
        self.layout.prop(obj_props, 'velocity')
        self.layout.prop(obj_props, 'one_shot')
        self.layout.prop_search(obj_props, 'collider', bpy.data, 'objects')
        self.layout.prop(obj_props, 'cache_folder')
        self.layout.prop(obj_props, 'show_particles')


def add_panel(self, context):
    obj = context.scene.objects.active
    if not obj.type == 'MESH':
        return

    column = self.layout.column(align=True)
    split = column.split(percentage=0.5)
    column_left = split.column()
    column_right = split.column()

    if obj.jet_fluid.is_active:
        column_right.operator(
                "jet_fluid.remove", 
                 text="Jet Fluid", 
                 icon='X'
        )
    else:
        column_right.operator(
            "jet_fluid.add", 
            text="Jet Fluid", 
            icon='MOD_FLUIDSIM'
        )


def register():
    bpy.types.PHYSICS_PT_add.append(add_panel)
    bpy.utils.register_class(JetFluidPanel)


def unregister():
    bpy.utils.unregister_class(JetFluidPanel)
    bpy.types.PHYSICS_PT_add.remove(add_panel)
