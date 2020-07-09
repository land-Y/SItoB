import bpy


#SRTを初期値に戻す。回転はまだ何かリセットすべきものある？
def si_resetSRT(oDelta):
    for i in bpy.context.selected_objects:

        i.location[0] = 0
        i.location[1] = 0
        i.location[2] = 0
        
        i.rotation_euler[0] = 0
        i.rotation_euler[1] = 0
        i.rotation_euler[2] = 0
        i.rotation_quaternion[0] = 1
        i.rotation_quaternion[1] = 0
        i.rotation_quaternion[2] = 0
        i.rotation_quaternion[3] = 0
        i.rotation_axis_angle[0] = 0
        i.rotation_axis_angle[1] = 0
        i.rotation_axis_angle[2] = 0
        i.rotation_axis_angle[3] = 0
        
        i.scale[0] = 1
        i.scale[1] = 1
        i.scale[2] = 1
        
        #reset delta
        if oDelta == 1:
            i.delta_location[0] = 0
            i.delta_location[1] = 0
            i.delta_location[2] = 0
            
            i.delta_rotation_euler[0] = 0
            i.delta_rotation_euler[1] = 0
            i.delta_rotation_euler[2] = 0
            
            i.scale[0] = 1
            i.scale[1] = 1
            i.scale[2] = 1
        


class si_resetSRT_OT_object(bpy.types.Operator):
    bl_idname = "object.si_resetsrt"
    bl_label = "Reset All Transform and Delta"
    bl_description = "Reset All Transform and Delta"
    bl_options = {'REGISTER', 'UNDO'} 


    def execute(self, context,):
        si_resetSRT(1)
        return {'FINISHED'}