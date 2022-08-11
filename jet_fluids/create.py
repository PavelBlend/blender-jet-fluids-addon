import os
import numpy

import bpy

from . import utils


@utils.time_stats('Clear Fluid Geometry')
def clear_fluid_geometry(domain, mode):
    if mode == 'PART':
        # particles mode
        obj_name = domain.jet_fluid.particles_object
    elif mode == 'MESH':
        # mesh mode
        obj_name = domain.jet_fluid.mesh_object
    if obj_name:
        obj = bpy.data.objects.get(obj_name)
        if obj:
            if obj.type == 'MESH':
                obj.data.clear_geometry()


@utils.time_stats('Get Domain Objects')
def get_domain_objects():
    obj_names = {obj.name for obj in bpy.data.objects}
    domain_objs = set()
    for obj_name in obj_names:
        obj = bpy.data.objects.get(obj_name)
        if not obj:
            continue
        if obj.jet_fluid.is_active:
            if obj.jet_fluid.object_type == 'DOMAIN':
                domain_objs.add(obj)
    return domain_objs


@utils.time_stats('Update Geom Object')
def update_geom_object(mode):
    domains = get_domain_objects()
    for domain in domains:
        if mode == 'MESH':
            # mesh mode
            if domain.jet_fluid.create_mesh:
                create_mesh(domain)
            else:
                clear_fluid_geometry(domain, mode)
        elif mode == 'PART':
            # particles mode
            if domain.jet_fluid.create_particles:
                create_particles(domain)
            else:
                clear_fluid_geometry(domain, mode)


def update_mesh_object(self, context):
    update_geom_object('MESH')


def update_par_object(self, context):
    update_geom_object('PART')


@utils.time_stats('Get File Path')
def get_file_path(domain, mode, frame=None):
    cache_folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
    if frame is None:
        frame = bpy.context.scene.frame_current
    if mode == 'POS':
        base_name = 'pos'
    elif mode == 'VEL':
        base_name = 'vel'
    elif mode == 'FORCE':
        base_name = 'force'
    elif mode == 'COL':
        base_name = 'col'
    elif mode == 'VERT':
        base_name = 'vert'
    elif mode == 'TRIS':
        base_name = 'tris'
    file_path = '{0}{1}_{2:0>6}.bin'.format(cache_folder, base_name, frame)
    return file_path


@utils.time_stats('Create Geom Object')
def create_geom_object(domain, base_name, attr_name):
    mesh = bpy.data.meshes.new('jet_fluid_' + base_name)
    obj = bpy.data.objects.new('jet_fluid_' + base_name, mesh)
    setattr(domain.jet_fluid, attr_name, obj.name)
    bpy.context.scene.collection.objects.link(obj)
    return obj


@utils.time_stats('Get Array')
def get_array(file_path, array_type, swap=False):
    if not os.path.exists(file_path):
        return
    if array_type == 'FLOAT':
        data_type = numpy.float32
    elif array_type == 'INT':
        data_type = numpy.int32
    array = numpy.fromfile(file_path, dtype=data_type)
    array.shape = (array.shape[0] // 3, 3)
    if swap:
        swaped = []
        for element in array:
            swaped.append((element[0], element[2], element[1]))
        array = swaped
    return array


@utils.time_stats('Write Array')
def write_array(array, file_path, array_type, swap=True, offset=None):
    if array_type == 'FLOAT':
        data_type = numpy.float32
    elif array_type == 'INT':
        data_type = numpy.int32
    if swap:
        swaped = []
        for element in array:
            swaped.append((element[0], element[2], element[1]))
        array = swaped
    if offset:
        offset_array = []
        for element in array:
            offset_array.append((
                element[0] - offset[0],
                element[1] - offset[1],
                element[2] - offset[2]
            ))
        array = offset_array
    np_array = numpy.array(array, data_type)
    np_array.tofile(file_path)


@utils.time_stats('Get Geom Object')
def get_geom_object(domain, attr_name, base_name, verts_count):
    attr_value = getattr(domain.jet_fluid, attr_name)
    is_clear = False
    if not attr_value:
        obj = create_geom_object(domain, base_name, attr_name)
    else:
        obj = bpy.data.objects.get(attr_value)
        if obj:
            if verts_count != len(obj.data.vertices):
                obj.data.clear_geometry()
                is_clear = True
        else:
            obj = create_geom_object(domain, base_name, attr_name)
    return obj, is_clear


@utils.time_stats('Set Mesh Location')
def set_mesh_location(domain, obj):
    obj.location = (
        domain.bound_box[0][0] * domain.scale[0] + domain.location[0],
        domain.bound_box[0][1] * domain.scale[1] + domain.location[1],
        domain.bound_box[0][2] * domain.scale[2] + domain.location[2]
    )


@utils.time_stats('Set Par Location')
def set_par_location(domain, obj):
    obj.location = domain.location


@utils.time_stats('Create Particles')
def create_particles(domain):
    file_path = get_file_path(domain, 'POS')
    vertices = get_array(file_path, 'FLOAT')

    if vertices is None:
        clear_fluid_geometry(domain, 'PART')
        return

    par_object, is_clear = get_geom_object(
        domain,
        'particles_object',
        'particles',
        len(vertices)
    )

    if is_clear:
        par_object.data.from_pydata(vertices, (), ())
    else:
        vertices.shape = (vertices.shape[0] * 3)
        par_object.data.vertices.foreach_set('co', vertices)
        par_object.data.update()

    set_par_location(domain, par_object)


@utils.time_stats('Create Mesh')
def create_mesh(domain):
    vert_file = get_file_path(domain, 'VERT')
    vertices = get_array(vert_file, 'FLOAT')

    tris_file = get_file_path(domain, 'TRIS')
    triangles = get_array(tris_file, 'INT')

    if vertices is None or triangles is None:
        clear_fluid_geometry(domain, 'MESH')
        return

    mesh_object, _ = get_geom_object(domain, 'mesh_object', 'mesh', -1)
    mesh_object.data.from_pydata(vertices, (), triangles)

    for polygon in mesh_object.data.polygons:
        polygon.use_smooth = True

    set_mesh_location(domain, mesh_object)


@bpy.app.handlers.persistent
def import_geometry(scene):
    print('-' * 79)
    domains = get_domain_objects()
    for domain in domains:
        if domain.jet_fluid.create_particles:
            create_particles(domain)
        if domain.jet_fluid.create_mesh:
            create_mesh(domain)
    print('-' * 79)


def register():
    bpy.app.handlers.frame_change_pre.append(import_geometry)


def unregister():
    bpy.app.handlers.frame_change_pre.remove(import_geometry)
