import os
import re
import time

import bpy


class JET_OT_ResetMesh(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_mesh"
    bl_label = "Reset Jet Fluid Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file in os.listdir(file_path):
            if re.search('(vert|tris)_[0-9]*.bin', file):
                os.remove(file_path + file)
        return {'FINISHED'}


class JET_OT_ResetParticles(bpy.types.Operator):
    bl_idname = "jet_fluid.reset_particles"
    bl_label = "Reset Jet Fluid Cache"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        file_path = bpy.path.abspath(obj.jet_fluid.cache_folder)
        if not os.path.exists(file_path):
            return {'FINISHED'}
        for file in os.listdir(file_path):
            if re.search('(pos|vel|force)_[0-9]*.bin', file):
                os.remove(file_path + file)
        return {'FINISHED'}


class JET_OT_Add(bpy.types.Operator):
    bl_idname = "jet_fluid.add"
    bl_label = "Add Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        obj.jet_fluid.is_active = True
        return {'FINISHED'}


class JET_OT_Remove(bpy.types.Operator):
    bl_idname = "jet_fluid.remove"
    bl_label = "Remove Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object
        obj.jet_fluid.is_active = False
        obj.jet_fluid.object_type = 'NONE'
        return {'FINISHED'}


__CLASSES__ = [
    JET_OT_Add,
    JET_OT_Remove,
    JET_OT_ResetParticles,
    JET_OT_ResetMesh
]


def register():
    for class_ in __CLASSES__:
        bpy.utils.register_class(class_)


def unregister():
    for class_ in reversed(__CLASSES__):
        bpy.utils.unregister_class(class_)
