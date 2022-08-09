import bpy


def draw_prop(
        layout,
        prop_owner,
        prop_name,
        prop_label,
        expand=False,
        use_column=False,
        boolean=False,
        prop_search=None,
        active=True
    ):
    row = layout.row(align=True)
    if not active:
        row.active = False
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
        elif prop_search:
            value_layout.prop_search(prop_owner, prop_name, bpy.data, prop_search, text='')
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
        draw_prop(lay, jet, 'collider_friction', 'Friction')


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
    bl_label = "Jet Fluid: Solvers"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # solvers
        draw_prop(lay, jet, 'solver_type', 'Solver', expand=True, use_column=True)
        draw_prop(lay, jet, 'advection_solver_type', 'Advection Solver', expand=True, use_column=True)
        draw_prop(lay, jet, 'diffusion_solver_type', 'Diffusion Solver', expand=True, use_column=True)
        draw_prop(lay, jet, 'pressure_solver_type', 'Pressure Solver', expand=True, use_column=True)

        # settings
        draw_prop(lay, jet, 'compressed_linear_system', 'Compressed Linear System', boolean=True)
        draw_prop(lay, jet, 'fixed_substeps', 'Fixed Substeps', boolean=True)
        draw_prop(lay, jet, 'fixed_substeps_count', 'Substeps Count', active=jet.fixed_substeps)
        draw_prop(lay, jet, 'max_cfl', 'Max CFL')


class JET_PT_Boundary(DomainBasePanel):
    bl_label = "Jet Fluid: Boundary"

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
    bl_label = "Jet Fluid: World"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'viscosity', 'Viscosity')
        draw_prop(lay, jet, 'gravity', 'Gravity', use_column=True)


class JET_PT_Create(DomainBasePanel):
    bl_label = "Jet Fluid: Create"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # mesh properties
        draw_prop(lay, jet, 'create_mesh', 'Create Mesh', boolean=True)
        draw_prop(lay, jet, 'mesh_object', 'Mesh Object', prop_search='objects', active=jet.create_mesh)

        # particles properties
        draw_prop(lay, jet, 'create_particles', 'Create Particles', boolean=True)
        draw_prop(lay, jet, 'particles_object', 'Particles Object', prop_search='objects', active=jet.create_particles)


class JET_PT_Debug(DomainBasePanel):
    bl_label = "Jet Fluid: Debug"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        draw_prop(lay, jet, 'show_particles', 'Show Particles', boolean=True)
        draw_prop(lay, jet, 'particle_size', 'Particle Size', active=jet.show_particles)
        draw_prop(lay, jet, 'color_type', 'Color Mode', active=jet.show_particles, use_column=True, expand=True)

        if jet.color_type == 'VELOCITY':
            draw_prop(lay, jet, 'max_velocity', 'Max Velocity', active=jet.show_particles)
            draw_prop(lay, jet, 'color_1', 'Min Velocity Color', active=jet.show_particles)
            draw_prop(lay, jet, 'color_2', 'Max Velocity Color', active=jet.show_particles)
        else:
            draw_prop(lay, jet, 'color_1', 'Particle Color', active=jet.show_particles)


class JET_PT_Mesh(DomainBasePanel):
    bl_label = "Jet Fluid: Mesh"

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements
        row = lay.row()

        # bake mesh
        split = lay.split(factor=0.75, align=True)
        split.operator('jet_fluid.bake_mesh', text='Bake')
        split.alert = True
        split.operator('jet_fluid.reset_mesh', text="Reset")
        draw_prop(lay, jet, 'resolution_mesh', 'Resolution')
        draw_prop(lay, jet, 'overwrite_mesh', 'Overwrite', boolean=True)
        draw_prop(lay, jet, 'is_output_sdf', 'Out SDF', boolean=True)
        draw_prop(lay, jet, 'iso_value', 'Iso Value')

        # frame range
        scene = context.scene
        draw_prop(lay, jet, 'frame_range_mesh', 'Frame Range', expand=True, use_column=True)
        if jet.frame_range_mesh == 'SCENE':
            draw_prop(lay, scene, 'frame_start', 'Frame Start', active=False)
            draw_prop(lay, scene, 'frame_end', 'Frame End', active=False)
        elif jet.frame_range_mesh == 'CURRENT_FRAME':
            draw_prop(lay, scene, 'frame_current', 'Frame Start', active=False)
            draw_prop(lay, scene, 'frame_current', 'Frame End', active=False)
        else:
            draw_prop(lay, jet, 'frame_range_mesh_start', 'Frame Start')
            draw_prop(lay, jet, 'frame_range_mesh_end', 'Frame End')

        draw_prop(lay, jet, 'converter_type', 'Method', expand=True, use_column=True)
        if jet.converter_type == 'ANISOTROPICPOINTSTOIMPLICIT':
            draw_prop(lay, jet, 'kernel_radius', 'Kernel Radius')
            draw_prop(lay, jet, 'cut_off_density', 'Cut Off Density')
            draw_prop(lay, jet, 'position_smoothing_factor', 'Position Smoothing')
            draw_prop(lay, jet, 'min_num_neighbors', 'Min Neighbors Count')
        elif jet.converter_type == 'SPHPOINTSTOIMPLICIT':
            draw_prop(lay, jet, 'kernel_radius', 'Kernel Radius')
            draw_prop(lay, jet, 'cut_off_density', 'Cut Off Density')
        elif jet.converter_type == 'SPHERICALPOINTSTOIMPLICIT':
            draw_prop(lay, jet, 'radius', 'Radius')
        elif jet.converter_type == 'ZHUBRIDSONPOINTSTOIMPLICIT':
            draw_prop(lay, jet, 'kernel_radius', 'Kernel Radius')
            draw_prop(lay, jet, 'cut_off_threshold', 'Cut Off Threshold')


class JET_PT_Simulate(DomainBasePanel):
    bl_label = "Jet Fluid: Simulate"
    bl_options = set()

    def draw(self, context):
        obj = context.object
        jet = obj.jet_fluid
        lay = self.layout

        # create ui elements

        # object type

        # bake particles
        split = lay.split(factor=0.75, align=True)
        split.operator('jet_fluid.bake_particles', text='Bake')
        split.alert = True
        split.operator('jet_fluid.reset_particles', text="Reset")

        draw_prop(lay, jet, 'cache_folder', 'Cache Folder')
        draw_prop(lay, jet, 'resolution', 'Resolution')

        # fps
        draw_prop(lay, jet, 'overwrite_simulation', 'Overwrite', boolean=True)
        draw_prop(lay, jet, 'fps_mode', 'FPS Mode', expand=True, use_column=True)
        if jet.fps_mode == 'SCENE':
            draw_prop(lay, context.scene.render, 'fps', 'FPS', active=False)
        else:
            draw_prop(lay, jet, 'fps', 'FPS', active=True)

        # frame range
        draw_prop(lay, jet, 'frame_range_simulation', 'Frame Range', expand=True, use_column=True)
        if jet.frame_range_simulation == 'CUSTOM':
            draw_prop(lay, jet, 'frame_range_simulation_start', 'Frame Start')
            draw_prop(lay, jet, 'frame_range_simulation_end', 'Frame End')
        else:
            draw_prop(lay, context.scene, 'frame_start', 'Frame Start', active=False)
            draw_prop(lay, context.scene, 'frame_end', 'Frame End', active=False)


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
    JET_PT_Create,
    JET_PT_World,
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
