import bpy


def draw_prop(
        layout,
        prop_owner,
        prop_name,
        prop_label,
        expand=False,
        use_column=False,
        boolean=False
    ):
    row = layout.row(align=True)
    row.label(text=prop_label + ':')
    if use_column:
        value_layout = row.column(align=True)
    else:
        value_layout = row
    if expand:
        value_layout.prop(prop_owner, prop_name, expand=True)
    else:
        if boolean:
            prop_value = getattr(prop_owner, prop_name)
            if prop_value:
                value_layout.prop(prop_owner, prop_name, text='Yes', toggle=True)
            else:
                value_layout.prop(prop_owner, prop_name, text='No', toggle=True)
        else:
            value_layout.prop(prop_owner, prop_name, text='')


class DomainBasePanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'DOMAIN'


class JET_PT_Type(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid: Type"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'object_type', 'Fluid Type', expand=True, use_column=True)


class JET_PT_Collider(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid: Collider"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'COLLIDER'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'friction_coefficient', 'Friction Coefficient')


class JET_PT_Emitter(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "physics"
    bl_label = "Jet Fluid: Emitter"

    @classmethod
    def poll(cls, context):
        jet = context.object.jet_fluid
        return jet.is_active and jet.object_type == 'EMITTER'

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'is_enable', 'Enable', boolean=True)
        draw_prop(lay, jet, 'one_shot', 'One Shot', boolean=True)
        draw_prop(lay, jet, 'allow_overlapping', 'Allow Overlapping', boolean=True)
        draw_prop(lay, jet, 'particles_count', 'Particles Sampling')
        draw_prop(lay, jet, 'emitter_jitter', 'Particles Jitter')
        draw_prop(lay, jet, 'emitter_seed', 'Particles Jitter Seed')
        draw_prop(lay, jet, 'max_number_of_particles', 'Particles Max Count')
        draw_prop(lay, jet, 'velocity', 'Initial Velocity', use_column=True)


class JET_PT_Solvers(DomainBasePanel):
    bl_label = "Jet Fluid Solvers"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # solvers
        lay.prop(jet, 'solver_type')
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


class JET_PT_Boundary(DomainBasePanel):
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


class JET_PT_World(DomainBasePanel):
    bl_label = "Jet Fluid World"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'viscosity', 'Viscosity')
        draw_prop(lay, jet, 'gravity', 'Gravity', use_column=True)


class JET_PT_Color(DomainBasePanel):
    bl_label = "Jet Fluid Color"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'use_colors', 'Use Colors', boolean=True)
        if jet.use_colors:
            draw_prop(lay, jet, 'simmulate_color_type', 'Type', use_column=True, expand=True)
            if jet.simmulate_color_type == 'SINGLE_COLOR':
                draw_prop(lay, jet, 'particles_color', 'Particles Color')
            elif jet.simmulate_color_type == 'VERTEX_COLOR':
                draw_prop(lay, jet, 'color_vertex_search_radius', 'Vertex Search Radius')
            elif jet.simmulate_color_type == 'TEXTURE':
                row = lay.row(align=True)
                row.label(text='Texture:')
                row.prop_search(jet, 'particles_texture', bpy.data, 'textures', text='')


class JET_PT_Create(DomainBasePanel):
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
        lay.prop(jet, 'create_particles')
        if jet.create_particles:
            lay.prop_search(jet, 'particles_object', bpy.data, 'objects')


class JET_PT_Convert(DomainBasePanel):
    bl_label = "Jet Fluid Convert"

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


class JET_PT_Debug(DomainBasePanel):
    bl_label = "Jet Fluid Debug"

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


class JET_PT_Cache(DomainBasePanel):
    bl_label = "Jet Fluid Cache"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'cache_folder', 'Cache Folder')


class JET_PT_Mesh(DomainBasePanel):
    bl_label = "Jet Fluid Mesh"

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
        lay.prop(jet, 'color_particles_search_radius')


class JET_PT_Simulate(DomainBasePanel):
    bl_label = "Jet Fluid Simulate"
    bl_options = set()

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # object type

        # bake particles
        split = lay.split(factor=0.75, align=True)
        split.operator('jet_fluid.bake_particles')
        split.alert = True
        split.operator('jet_fluid.reset_particles', text="Reset")

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
    JET_PT_Type,
    JET_PT_Simulate,
    JET_PT_Mesh,
    JET_PT_Solvers,
    JET_PT_Boundary,
    JET_PT_Cache,
    JET_PT_Create,
    JET_PT_Convert,
    JET_PT_World,
    JET_PT_Color,
    JET_PT_Debug,
    JET_PT_Emitter,
    JET_PT_Collider
]


def register():
    bpy.types.PHYSICS_PT_add.append(add_jet_fluid_button)
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
    bpy.types.PHYSICS_PT_add.remove(add_jet_fluid_button)
