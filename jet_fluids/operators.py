import os
import re
import time

import bpy

from .utils import print_info, convert_time_to_string


LOGS_FILE_NAMES = (
    '_jet_fluids_convert.log',
    '_jet_fluids_mesh.log',
    '_jet_fluids_simulate.log'
)


class JET_FLUID_OT_RemoveLogs(bpy.types.Operator):
    bl_idname = "jet_fluid.remove_logs"
    bl_label = "Remove Logs"
    bl_options = {'REGISTER'}

    def execute(self, context):
        domain = context.object
        cache_folder = bpy.path.abspath(domain.jet_fluid.cache_folder)
        if not os.path.exists(cache_folder):
            return {'FINISHED'}
        for file in os.listdir(cache_folder):
            if file in LOGS_FILE_NAMES:
                os.remove(cache_folder + file)
        return {'FINISHED'}


class JET_FLUID_OT_ResetMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_mesh"
    bl_label = "Reset Jet Fluid Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file_ in os.listdir(file_path):
            if re.search('mesh_[0-9]*.bin', file_):
                os.remove(file_path + file_)
        return {'FINISHED'}


class JET_FLUID_OT_ResetParticles(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_particles"
    bl_label = "Reset Jet Fluid Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file_ in os.listdir(file_path):
            if re.search('particles_[0-9]*.bin', file_) or re.search('fluid_[0-9]*_00.bphys', file_):
                os.remove(file_path + file_)
        return {'FINISHED'}


class JET_FLUID_OT_Add(bpy.types.Operator):
    bl_idname = "jet_fluid.add"
    bl_label = "Add Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        obj.jet_fluid.is_active = True
        return {'FINISHED'}


class JET_FLUID_OT_Remove(bpy.types.Operator):
    bl_idname = "jet_fluid.remove"
    bl_label = "Remove Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        obj.jet_fluid.is_active = False
        obj.jet_fluid.object_type = 'NONE'
        return {'FINISHED'}


__CLASSES__ = [
    JET_FLUID_OT_Add,
    JET_FLUID_OT_Remove,
    JET_FLUID_OT_ResetParticles,
    JET_FLUID_OT_ResetMesh,
    JET_FLUID_OT_RemoveLogs
]


def register():
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
