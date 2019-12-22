import os
import threading
import struct
import time

import bpy
import mathutils

from . import pyjet
from . import bake
from .utils import get_log_path


domain = None


def print_mesh_info(*print_params):
    global domain
    if domain.jet_fluid.print_debug_info:
        print(*print_params)
    if domain.jet_fluid.write_log:
        log_file_path = get_log_path(domain, '_jet_fluids_mesh.log')
        with open(log_file_path, 'a') as log_file:
            print(*print_params, file=log_file)


def create_solver(self, domain):
    res_x, res_y, res_z, orig_x, orig_y, orig_z, size_x, _ = bake.calc_res(
        self, domain
    )
    solv = bake.solvers[domain.jet_fluid.hybrid_solver_type](
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


def save_mesh(operator, surface_mesh, frame_index, particles, colors):
    start_time = time.time()
    print_mesh_info('Save mesh verts start')
    domain = operator.domain
    coef = domain.jet_fluid.resolution / domain.jet_fluid.resolution_mesh
    bin_mesh_data = bytearray()
    points_count = surface_mesh.numberOfPoints()
    bin_mesh_data.extend(struct.pack('I', points_count))

    if domain.jet_fluid.use_colors and domain.jet_fluid.simulation_method == 'HYBRID':
        kdtree = mathutils.kdtree.KDTree(len(particles))
        for index, par in enumerate(particles):
            kdtree.insert((par[0], par[2], par[1]), index)
        kdtree.balance()

    offset = (
        domain.bound_box[0][0] * domain.scale[0] + domain.location[0],
        domain.bound_box[0][1] * domain.scale[1] + domain.location[1],
        domain.bound_box[0][2] * domain.scale[2] + domain.location[2]
    )

    for point_index in range(points_count):
        point = surface_mesh.point(point_index)
        bin_mesh_data.extend(struct.pack(
            '3f', point.x * coef, point.y * coef, point.z * coef
        ))
        if domain.jet_fluid.use_colors and domain.jet_fluid.simulation_method == 'HYBRID':
            _, index, _ = kdtree.find((
                point[0] * coef + offset[0],
                point[2] * coef + offset[1],
                point[1] * coef + offset[2]
            ))
            color = colors[index]
            bin_mesh_data.extend(struct.pack(
                '4f', *color
            ))
        else:
            bin_mesh_data.extend(struct.pack(
                '4f', 0.0, 0.0, 0.0, 0.0
            ))
    print_mesh_info('Save mesh verts end')

    print_mesh_info('Save mesh tris start')
    triangles_count = surface_mesh.numberOfTriangles()
    bin_mesh_data.extend(struct.pack('I', triangles_count))
    for triangle_index in range(triangles_count):
        tris = surface_mesh.pointIndex(triangle_index)
        bin_mesh_data.extend(struct.pack('3I', tris.x, tris.y, tris.z))
    print_mesh_info('Save mesh tris end')

    print_mesh_info('Write mesh file start')
    file_path = '{0}mesh_{1:0>6}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        frame_index
    )
    file = open(file_path, 'wb')
    file.write(bin_mesh_data)
    file.close()
    print_mesh_info('Write mesh file end')
    print_mesh_info('Save mesh time: {0:.3}s'.format(time.time() - start_time))


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
    colors = []
    file_path = '{0}particles_{1:0>6}.bin'.format(
        bpy.path.abspath(domain.jet_fluid.cache_folder),
        frame_index
    )
    if not os.path.exists(file_path):
        print_mesh_info('Can\'t find particles file in {} frame'.format(frame_index))
        return points, colors
    print_mesh_info('Open particles file start')
    particles_file = open(file_path, 'rb')
    particles_data = particles_file.read()
    particles_file.close()
    print_mesh_info('Open particles file end')
    print_mesh_info('Read particles start')
    p = 0
    particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
    p += 4
    for particle_index in range(particles_count):
        particle_position = struct.unpack('3f', particles_data[p : p + 12])
        p += 36    # skip velocities, forces
        color = struct.unpack('4f', particles_data[p : p + 16])
        p += 16
        points.append(particle_position)
        if domain.jet_fluid.use_colors:
            colors.append(color)
    print_mesh_info('Read particles end')
    return points, colors


def bake_mesh(domain, solv, grid, frame_index):
    points, colors = read_particles(domain, frame_index)
    if not points:
        return None, points, colors
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
    return surface_mesh, points, colors


class JetFluidBakeMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_mesh"
    bl_label = "Bake Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        global domain
        domain = bpy.context.view_layer.objects.active
        log_path = get_log_path(domain, '_jet_fluids_mesh.log')
        with open(log_path, 'w') as log_file:
            pass
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
        elif domain.jet_fluid.frame_range_mesh == 'TIMELINE':
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
                surface_mesh, particles, colors = bake_mesh(domain, solv, grid, frame_index)
                if surface_mesh:
                    save_mesh(self, surface_mesh, frame_index, particles, colors)
                print_mesh_info('Generate mesh end:   frame {0:0>6}'.format(frame_index))
                print_mesh_info('Generate mesh time: {0:.3}s'.format(time.time() - frame_start_time))
                print_mesh_info('-' * 79)
        print_mesh_info('Total time: {0:.3}s'.format(time.time() - start_time))
        return {'FINISHED'}

    def invoke(self, context, event):
        thread = threading.Thread(target=self.execute, args=(context, ))
        thread.start()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBakeMesh)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeMesh)
