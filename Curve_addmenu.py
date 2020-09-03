import bpy

def ResetRadius(n)
bpy.ops.curve.radius_set(radius=n)

class si_del_subdiv_OT_object(bpy.types.Operator):
    bl_idname = "object.si_del_sudiv"
    bl_label = "Delete Subdivision"
    bl_description = "Subdivisions like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context):
        delete_subdiv()
        si_noactive_normal()
        return {'FINISHED'}


#自動化してから整列
bpy.ops.curve.handle_type_set(type='AUTOMATIC')
bpy.ops.curve.handle_type_set(type='ALIGNED')
