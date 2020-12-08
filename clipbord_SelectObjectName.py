import bpy

class clipbord_select_object_OT_object(bpy.types.Operator):
    bl_idname = "view3d.clipbord_select_object"
    bl_label = "clipbord select object"
    
    def execute(self, context):

        #ボーンが選択が優先
        if bpy.context.active_bone:
            BoneName = bpy.context.active_bone.name
            bpy.context.window_manager.clipboard = BoneName
            print("clipboard! " + BoneName)
        
        #ボーン以外ならアクティブオブジェクト
        elif bpy.context.active_object:
            ObjName = bpy.context.active_object.name
            bpy.context.window_manager.clipboard = ObjName
            print("clipboard! " + ObjName)
    

        return {'FINISHED'}

