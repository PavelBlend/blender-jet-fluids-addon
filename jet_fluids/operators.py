
import bpy


class JetFluidAdd(bpy.types.Operator):
    bl_idname = "jet_fluid.add"
    bl_label = "Add Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        obj.jet_fluid.is_active = True
        return {'FINISHED'}


class JetFluidRemove(bpy.types.Operator):
    bl_idname = "jet_fluid.remove"
    bl_label = "Remove Jet fluid object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.scene.objects.active
        obj.jet_fluid.is_active = False
        return {'FINISHED'}


def register():
    bpy.utils.register_class(JetFluidAdd)
    bpy.utils.register_class(JetFluidRemove)


def unregister():
    bpy.utils.unregister_class(JetFluidAdd)
    bpy.utils.unregister_class(JetFluidRemove)
