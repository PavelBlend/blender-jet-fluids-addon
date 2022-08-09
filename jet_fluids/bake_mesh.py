import os
import threading
import time

import bpy
import mathutils

from . import pyjet
from . import bake
from . import create
from .utils import convert_time_to_string


domain = None


def print_mesh_info(*print_params):
    print(*print_params)


def create_solver(self, domain):
    res_x, res_y, res_z, orig_x, orig_y, orig_z, size_x, _ = bake.calc_res(
        self, domain
    )
    solv = bake.solvers[domain.jet_fluid.solver_type](
        resolution=(res_x, res_z, res_y),
        gridOrigin=(orig_x, orig_z, orig_y),
        domainSizeX=size_x
    )
    res_x, res_y, res_z, orig_x, orig_y, orig_z, size_x, _ = bake.calc_res(
        self, domain, type='MESH'
    )
    grid = pyjet.VertexCenteredScalarGrid3(
        resolution=(res_x, res_z, res_y),
        gridOrigin=(orig_x, orig_z, orig_y),
        domainSizeX=size_x
    )
    return solv, grid


def save_mesh(operator, surface_mesh, frame_index, particles):
    start_time = time.time()
    print_mesh_info('Save mesh verts start')
    domain = operator.domain
    coef = domain.jet_fluid.resolution / domain.jet_fluid.resolution_mesh
    points_count = surface_mesh.numberOfPoints()
    offset = (
        domain.bound_box[0][0] * domain.scale[0] + domain.location[0],
        domain.bound_box[0][1] * domain.scale[1] + domain.location[1],
        domain.bound_box[0][2] * domain.scale[2] + domain.location[2]
    )
    points = []
    for point_index in range(points_count):
        point = surface_mesh.point(point_index)
        points.extend((point.x * coef, point.z * coef, point.y * coef))
    verts_file_path = create.get_file_path(domain, 'VERT', frame=frame_index)
    create.write_array(points, verts_file_path, 'FLOAT', swap=False)
    print_mesh_info('Save mesh verts end')

    print_mesh_info('Save mesh tris start')
    triangles_count = surface_mesh.numberOfTriangles()
    faces = []
    for triangle_index in range(triangles_count):
        tris = surface_mesh.pointIndex(triangle_index)
        faces.extend((tris.x, tris.z, tris.y))
    faces_file_path = create.get_file_path(domain, 'TRIS', frame=frame_index)
    create.write_array(faces, faces_file_path, 'INT', swap=False)
    print_mesh_info('Save mesh tris end')

    print_mesh_info('Write mesh file end')
    print_mesh_info('Save mesh time: {0}'.format(
        convert_time_to_string(start_time)
    ))


def check_cache_file(domain, frame_index):
    file_path = '{0}mesh_{1:0>6}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        frame_index
    )
    if os.path.exists(file_path):
        return True
    else:
        return False


def read_particles(domain, frame_index):
    points = []
    file_path = create.get_file_path(domain, 'POS', frame_index)
    if not os.path.exists(file_path):
        print_mesh_info('Can\'t find particles file in {} frame'.format(frame_index))
        return points
    print_mesh_info('Read particles start')
    points = create.get_array(file_path, 'FLOAT', swap=True)
    offset_points = [
        (
            point[0] + domain.location[0],
            point[1] + domain.location[2],
            point[2] + domain.location[1]
        ) for point in points
    ]
    print_mesh_info('Read particles end')
    return offset_points


def bake_mesh(domain, solv, grid, frame_index):
    points = read_particles(domain, frame_index)
    if not points:
        return None, points
    print_mesh_info('Create converter start')
    if domain.jet_fluid.converter_type == 'ANISOTROPICPOINTSTOIMPLICIT':
        converter = pyjet.AnisotropicPointsToImplicit3(
            domain.jet_fluid.kernel_radius * solv.gridSpacing.x,
            domain.jet_fluid.cut_off_density,
            domain.jet_fluid.position_smoothing_factor,
            domain.jet_fluid.min_num_neighbors,
            domain.jet_fluid.is_output_sdf
        )
    elif domain.jet_fluid.converter_type == 'SPHPOINTSTOIMPLICIT':
        converter = pyjet.SphPointsToImplicit3(
            domain.jet_fluid.kernel_radius * solv.gridSpacing.x,
            domain.jet_fluid.cut_off_density,
            domain.jet_fluid.is_output_sdf
        )
    elif domain.jet_fluid.converter_type == 'SPHERICALPOINTSTOIMPLICIT':
        converter = pyjet.SphPointsToImplicit3(
            domain.jet_fluid.radius,
            domain.jet_fluid.is_output_sdf
        )
    elif domain.jet_fluid.converter_type == 'ZHUBRIDSONPOINTSTOIMPLICIT':
        converter = pyjet.ZhuBridsonPointsToImplicit3(
            domain.jet_fluid.kernel_radius * solv.gridSpacing.x,
            domain.jet_fluid.cut_off_threshold,
            domain.jet_fluid.is_output_sdf
        )
    print_mesh_info('Create converter end')
    print_mesh_info('Convert start')
    converter.convert(points, grid)
    print_mesh_info('Convert end')
    print_mesh_info('Meshing start')
    con_flag = bake.set_closed_domain_boundary_flag(domain, 'mesh_connectivity_boundary')
    close_flag = bake.set_closed_domain_boundary_flag(domain, 'mesh_closed_boundary')
    surface_mesh = pyjet.marchingCubes(
        grid,    # grid
        (solv.gridSpacing.x, solv.gridSpacing.y, solv.gridSpacing.z),    # gridSize
        (0, 0, 0),    # origin
        domain.jet_fluid.iso_value,    # isoValue
        close_flag,    # bndClose
        con_flag    # bndConnectivity
    )
    print_mesh_info('Meshing end')
    return surface_mesh, points


class JetFluidBakeMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_mesh"
    bl_label = "Bake Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global domain
        domain = bpy.context.view_layer.objects.active
        start_time = time.time()
        pyjet.Logging.mute()
        scn = context.scene
        if not domain.jet_fluid.cache_folder:
            self.report({'WARNING'}, 'Cache Folder not Specified!')
            return {'FINISHED'}
        solv, grid = create_solver(self, domain)

        if domain.jet_fluid.frame_range_mesh == 'CUSTOM':
            frame_start = domain.jet_fluid.frame_range_mesh_start
            frame_end = domain.jet_fluid.frame_range_mesh_end
        elif domain.jet_fluid.frame_range_mesh == 'SCENE':
            frame_start = context.scene.frame_start
            frame_end = context.scene.frame_end
        else:
            frame_start = context.scene.frame_current
            frame_end = context.scene.frame_current

        for frame_index in range(frame_start, frame_end + 1):
            has_cache = check_cache_file(domain, frame_index)
            if has_cache and not domain.jet_fluid.overwrite_mesh:
                print_mesh_info('Skip frame', frame_index)
            else:
                frame_start_time = time.time()
                print_mesh_info('Generate mesh start: frame {0:0>6}'.format(frame_index))
                surface_mesh, particles = bake_mesh(domain, solv, grid, frame_index)
                if surface_mesh:
                    save_mesh(self, surface_mesh, frame_index, particles)
                print_mesh_info('Generate mesh end:   frame {0:0>6}'.format(frame_index))
                print_mesh_info('Generate mesh time: {0}'.format(convert_time_to_string(frame_start_time)))
                print_mesh_info('-' * 79)
        print_mesh_info('Total time: {0}'.format(convert_time_to_string(start_time)))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.scene.jet_fluid_domain_object = context.object.name
        thread = threading.Thread(target=self.execute, args=(context, ))
        thread.start()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBakeMesh)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeMesh)
