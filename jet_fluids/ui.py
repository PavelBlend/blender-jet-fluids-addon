import bpy


class JET_FLUID_PT_DomainPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'


class JET_FLUID_PT_ColliderPanel(bpy.types.Panel):
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
        lay.prop(jet, 'friction_coefficient')


class JET_FLUID_PT_EmitterPanel(bpy.types.Panel):
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
        lay.prop(jet, 'is_enable')
        lay.prop(jet, 'one_shot')
        lay.prop(jet, 'particles_count')
        lay.prop(jet, 'max_number_of_particles')
        lay.prop(jet, 'emitter_jitter')
        lay.prop(jet, 'emitter_seed')
        lay.prop(jet, 'allow_overlapping')
        lay.prop(jet, 'velocity')


class JET_FLUID_PT_SolversPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Solvers"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # solvers
        lay.prop(jet, 'simulation_method')
        if jet.simulation_method == 'HYBRID':
            lay.prop(jet, 'hybrid_solver_type')
            lay.prop(jet, 'advection_solver_type')
            lay.prop(jet, 'diffusion_solver_type')
            lay.prop(jet, 'pressure_solver_type')

            # settings
            lay.prop(jet, 'max_cfl')
            lay.prop(jet, 'compressed_linear_system')

            # substeps
            lay.prop(jet, 'fixed_substeps')
            row = lay.row()
            if not jet.fixed_substeps:
                row.active = False
            row.prop(jet, 'fixed_substeps_count')


class JET_FLUID_PT_BoundaryPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Boundary"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.label(text='Domain Close:')

        row = lay.row()
        row.prop(jet, 'bound_right')
        row.prop(jet, 'bound_left')

        row = lay.row()
        row.prop(jet, 'bound_front')
        row.prop(jet, 'bound_back')

        row = lay.row()
        row.prop(jet, 'bound_up')
        row.prop(jet, 'bound_down')

        # connectivity
        lay.label(text='Mesh Close:')

        row = lay.row()
        row.prop(jet, 'close_right')
        row.prop(jet, 'close_left')

        row = lay.row()
        row.prop(jet, 'close_front')
        row.prop(jet, 'close_back')

        row = lay.row()
        row.prop(jet, 'close_up')
        row.prop(jet, 'close_down')

        # connectivity
        lay.label(text='Mesh Connectivity:')

        row = lay.row()
        row.prop(jet, 'con_right')
        row.prop(jet, 'con_left')

        row = lay.row()
        row.prop(jet, 'con_front')
        row.prop(jet, 'con_back')

        row = lay.row()
        row.prop(jet, 'con_up')
        row.prop(jet, 'con_down')


class JET_FLUID_PT_WorldPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid World"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'viscosity')
        lay.prop(jet, 'gravity')


class JET_FLUID_PT_ColorPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Color"

    @classmethod
    def poll(cls, context):
        solver_object = context.object
        return solver_object.jet_fluid.simulation_method == 'HYBRID'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'use_colors')
        if jet.use_colors:
            lay.prop(jet, 'simmulate_color_type')
            if jet.simmulate_color_type == 'SINGLE_COLOR':
                lay.prop(jet, 'particles_color')


class JET_FLUID_PT_CreatePanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Create"

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
        if obj.jet_fluid.simulation_method == 'HYBRID':
            lay.prop(jet, 'create_particles')
            if jet.create_particles:
                lay.prop_search(jet, 'particles_object', bpy.data, 'objects')


class JET_FLUID_PT_ConvertPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Convert"

    @classmethod
    def poll(cls, context):
        solver_object = context.object
        return solver_object.jet_fluid.simulation_method == 'HYBRID'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # standart particle system
        split = lay.split(factor=0.75, align=True)
        split.operator('jet_fluid.create_particle_system')
        split.alert = True
        split.operator('jet_fluid.reset_physic_cache', text='Clear')

        lay.operator('jet_fluid.reload_particle_system')

        # frame range
        lay.prop(jet, 'frame_range_convert')
        if jet.frame_range_convert == 'CUSTOM':
            lay.prop(jet, 'frame_range_convert_start')
            lay.prop(jet, 'frame_range_convert_end')

        lay.operator('jet_fluid.convert_to_jet_particles')
        lay.prop(jet, 'input_data_type')
        lay.prop_search(jet, 'input_vertices_object', bpy.data, 'objects')

        lay.prop(jet, 'overwrite_convert')


class JET_FLUID_PT_DebugPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Debug"

    @classmethod
    def poll(cls, context):
        solver_object = context.object
        return solver_object.jet_fluid.simulation_method == 'HYBRID'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'print_debug_info')
        lay.prop(jet, 'write_log')
        lay.prop(jet, 'show_particles')
        if jet.show_particles:
            lay.prop(jet, 'particle_size')
            lay.prop(jet, 'color_type')
            row = lay.row()
            if jet.color_type != 'PARTICLE_COLOR':
                row.prop(jet, 'color_1', text='')
                if jet.color_type == 'VELOCITY':
                    row.prop(jet, 'color_2', text='')
                    lay.prop(jet, 'max_velocity')
        lay.operator('jet_fluid.remove_logs')


class JET_FLUID_PT_CachePanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Cache"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        lay.prop(jet, 'cache_folder')


class JET_FLUID_PT_MeshPanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Mesh"

    @classmethod
    def poll(cls, context):
        solver_object = context.object
        return solver_object.jet_fluid.simulation_method == 'HYBRID'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # bake mesh
        split = lay.split(factor=0.75, align=True)
        split.operator('jet_fluid.bake_mesh')
        split.alert = True
        split.operator('jet_fluid.reset_mesh', text="Reset")
        lay.prop(jet, 'resolution_mesh')
        lay.prop(jet, 'iso_value')
        lay.prop(jet, 'converter_type')
        if jet.converter_type == 'ANISOTROPICPOINTSTOIMPLICIT':
            lay.prop(jet, 'kernel_radius')
            lay.prop(jet, 'cut_off_density')
            lay.prop(jet, 'position_smoothing_factor')
            lay.prop(jet, 'min_num_neighbors')
            lay.prop(jet, 'is_output_sdf')
        elif jet.converter_type == 'SPHPOINTSTOIMPLICIT':
            lay.prop(jet, 'kernel_radius')
            lay.prop(jet, 'cut_off_density')
            lay.prop(jet, 'is_output_sdf')
        elif jet.converter_type == 'SPHERICALPOINTSTOIMPLICIT':
            lay.prop(jet, 'radius')
            lay.prop(jet, 'is_output_sdf')
        elif jet.converter_type == 'ZHUBRIDSONPOINTSTOIMPLICIT':
            lay.prop(jet, 'kernel_radius')
            lay.prop(jet, 'cut_off_threshold')
            lay.prop(jet, 'is_output_sdf')

        # frame range
        lay.prop(jet, 'frame_range_mesh')
        if jet.frame_range_mesh == 'CUSTOM':
            lay.prop(jet, 'frame_range_mesh_start')
            lay.prop(jet, 'frame_range_mesh_end')

        lay.prop(jet, 'overwrite_mesh')


class JET_FLUID_PT_SimulatePanel(JET_FLUID_PT_DomainPanel):
    bl_label = "Jet Fluid Simulate"
    bl_options = set()

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # object type
        lay.prop(jet, 'object_type')

        # bake particles
        split = lay.split(factor=0.75, align=True)
        if jet.simulation_method == 'HYBRID':
            split.operator('jet_fluid.bake_particles')
            split.alert = True
            split.operator('jet_fluid.reset_particles', text="Reset")
        else:
            split.operator('jet_fluid.bake_fluid')
            split.alert = True
            split.operator('jet_fluid.reset_fluid', text="Reset")

        lay.prop(jet, 'resolution')

        # fps
        lay.label(text='Time:')
        lay.prop(jet, 'use_scene_fps')
        row = lay.row()
        if jet.use_scene_fps:
            row.active = False
            row.prop(context.scene.render, 'fps')
        else:
            row.prop(jet, 'fps')

        # frame range
        lay.prop(jet, 'frame_range_simulation')
        if jet.frame_range_simulation == 'CUSTOM':
            lay.prop(jet, 'frame_range_simulation_start')
            lay.prop(jet, 'frame_range_simulation_end')

        lay.prop(jet, 'overwrite_simulation')


class JET_FLUID_PT_Panel(bpy.types.Panel):
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
    obj = context.object
    if not obj.type == 'MESH':
        return

    column = self.layout.column(align=True)
    split = column.split(factor=0.5)
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
    JET_FLUID_PT_Panel,
    JET_FLUID_PT_SimulatePanel,
    JET_FLUID_PT_MeshPanel,
    JET_FLUID_PT_SolversPanel,
    JET_FLUID_PT_BoundaryPanel,
    JET_FLUID_PT_CachePanel,
    JET_FLUID_PT_CreatePanel,
    JET_FLUID_PT_ConvertPanel,
    JET_FLUID_PT_WorldPanel,
    JET_FLUID_PT_ColorPanel,
    JET_FLUID_PT_DebugPanel,
    JET_FLUID_PT_EmitterPanel,
    JET_FLUID_PT_ColliderPanel
]


def register():
    bpy.types.PHYSICS_PT_add.append(add_jet_fluid_button)
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
    bpy.types.PHYSICS_PT_add.remove(add_jet_fluid_button)
