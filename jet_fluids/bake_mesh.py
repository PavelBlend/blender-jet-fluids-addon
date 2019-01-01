
import os
import threading
import struct

import bpy

from . import pyjet
from . import bake


class JetFluidBakeMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.bake_mesh"
    bl_label = "Bake Mesh"
    bl_options = {'REGISTER'}

    def execute(self, context):
        pyjet.Logging.mute()
        scn = context.scene
        domain = scn.objects.active
        if not domain.jet_fluid.cache_folder:
            self.report({'WARNING'}, 'Cache Folder not Specified!')
            return {'FINISHED'}
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = bake.calc_res(self, domain)
        solv = bake.solvers[domain.jet_fluid.solver_type](
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=domain_size_x
        )
        resolution_x, resolution_y, resolution_z, origin_x, origin_y, origin_z, domain_size_x, _ = bake.calc_res(self, domain, type='MESH')
        grid = pyjet.VertexCenteredScalarGrid3(
            resolution=(resolution_x, resolution_z, resolution_y),
            gridOrigin=(origin_x, origin_z, origin_y),
            domainSizeX=self.domain_size_x
        )
        for frame_index in range(scn.frame_start, scn.frame_end + 1):
            file_path = '{}mesh_{}.bin'.format(
                bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                frame_index
            )
            if os.path.exists(file_path):
                print('skip frame', frame_index)
                continue
            else:
                print('frame', frame_index)
                file_path = '{}particles_{}.bin'.format(
                    bpy.path.abspath(domain.jet_fluid.cache_folder),
                    frame_index
                )
                if not os.path.exists(file_path):
                    print('can\'t find particles file in {} frame'.format(frame_index))
                    continue
                print('open particles file')
                particles_file = open(file_path, 'rb')
                particles_data = particles_file.read()
                particles_file.close()
                print('read particles')
                p = 0
                particles_count = struct.unpack('I', particles_data[p : p + 4])[0]
                p += 4
                points = []
                for particle_index in range(particles_count):
                    particle_position = struct.unpack('3f', particles_data[p : p + 12])
                    p += 36    # skip velocities and forces
                    points.append(particle_position)
    
                print('create converter')
                converter = pyjet.SphPointsToImplicit3(2.0 * solv.gridSpacing.x, 0.5)
                print('convert')
                converter.convert(points, grid)
                print('meshing')
                surface_mesh = pyjet.marchingCubes(
                    grid,
                    (solv.gridSpacing.x, solv.gridSpacing.y, solv.gridSpacing.z),
                    (0, 0, 0),
                    0.0,
                    pyjet.DIRECTION_ALL
                )
                print('save verts')
                coef = self.domain.jet_fluid.resolution / self.domain.jet_fluid.resolution_mesh
                bin_mesh_data = bytearray()
                points_count = surface_mesh.numberOfPoints()
                bin_mesh_data.extend(struct.pack('I', points_count))
                for point_index in range(points_count):
                    point = surface_mesh.point(point_index)
                    bin_mesh_data.extend(struct.pack('3f', point.x * coef, point.y * coef, point.z * coef))
    
                print('save tris')
                triangles_count = surface_mesh.numberOfTriangles()
                bin_mesh_data.extend(struct.pack('I', triangles_count))
                for triangle_index in range(triangles_count):
                    tris = surface_mesh.pointIndex(triangle_index)
                    bin_mesh_data.extend(struct.pack('3I', tris.x, tris.y, tris.z))
    
                print('write file')
                file_path = '{}mesh_{}.bin'.format(
                    bpy.path.abspath(self.domain.jet_fluid.cache_folder),
                    frame_index
                )
                file = open(file_path, 'wb')
                file.write(bin_mesh_data)
                file.close()
                print('save mesh end')
        return {'FINISHED'}

    def invoke(self, context, event):
        thread = threading.Thread(target=self.execute, args=(context, ))
        thread.start()
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidBakeMesh)


def unregister():
    bpy.utils.unregister_class(JetFluidBakeMesh)
