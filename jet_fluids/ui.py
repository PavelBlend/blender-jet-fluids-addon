
import bpy


class JetFluidColliderPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'COLLIDER'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'object_type')


class JetFluidEmitterPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'EMITTER'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'object_type')
        lay.prop(jet, 'one_shot')
        lay.prop(jet, 'velocity')


class JetFluidBoundaryPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid Boundary"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()
        row.prop(jet, 'bound_right')
        row.prop(jet, 'bound_left')

        row = lay.row()
        row.prop(jet, 'bound_front')
        row.prop(jet, 'bound_back')

        row = lay.row()
        row.prop(jet, 'bound_up')
        row.prop(jet, 'bound_down')


class JetFluidWorldPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid World"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'viscosity')
        lay.prop(jet, 'gravity')


class JetFluidCreatePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid Create"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # mesh properties
        lay.prop(jet, 'create_mesh')
        if jet.create_mesh:
            lay.prop_search(jet, 'mesh_object', bpy.data, 'objects')

        # particles properties
        lay.prop(jet, 'create_particles')
        if jet.create_particles:
            lay.prop_search(jet, 'particles_object', bpy.data, 'objects')


class JetFluidDebugPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid Debug"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'show_particles')
        if jet.show_particles:
            lay.prop(jet, 'color_type')
            row = lay.row()
            row.prop(jet, 'color_1', text='')
            if jet.color_type == 'VELOCITY':
                row.prop(jet, 'color_2', text='')
                lay.prop(jet, 'max_velocity')


class JetFluidCachePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid Cache"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'cache_folder')


class JetFluidSimulatePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid Simulate"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # object type
        lay.prop(jet, 'object_type')

        # bake particles
        split = lay.split(percentage=0.75, align=True)
        split.operator('jet_fluid.bake_particles')
        split.alert = True
        split.operator('jet_fluid.reset_particles', text="Reset")

        # bake mesh
        split = lay.split(percentage=0.75, align=True)
        split.operator('jet_fluid.bake_mesh')
        split.alert = True
        split.operator('jet_fluid.reset_mesh', text="Reset")

        # simulation properties
        lay.prop(jet, 'solver_type')
        lay.prop(jet, 'advection_solver_type')
        lay.prop(jet, 'diffusion_solver_type')
        lay.prop(jet, 'pressure_solver_type')
        lay.prop(jet, 'resolution')
        lay.prop(jet, 'resolution_mesh')
        lay.prop(jet, 'particles_count')
        lay.prop(jet, 'max_cfl')
        lay.prop(jet, 'compressed_linear_system')

        # substeps
        lay.prop(jet, 'fixed_substeps')
        row = lay.row()
        if not jet.fixed_substeps:
            row.active = False
        row.prop(jet, 'fixed_substeps_count')

        # fps
        lay.prop(jet, 'use_scene_fps')
        row = lay.row()
        if jet.use_scene_fps:
            row.active = False
        row.prop(jet, 'fps')


class JetFluidPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'NONE'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'object_type')


def add_jet_fluid_button(self, context):
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


__CLASSES__ = [
    JetFluidPanel,
    JetFluidSimulatePanel,
    JetFluidBoundaryPanel,
    JetFluidCachePanel,
    JetFluidCreatePanel,
    JetFluidWorldPanel,
    JetFluidDebugPanel,
    JetFluidEmitterPanel,
    JetFluidColliderPanel
]


def register():
    bpy.types.PHYSICS_PT_add.append(add_jet_fluid_button)
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
    bpy.types.PHYSICS_PT_add.remove(add_jet_fluid_button)
