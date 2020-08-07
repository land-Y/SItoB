import bpy
from bpy.props import BoolProperty



def Tgl_HideOverray():
    ovl = bpy.context.space_data.overlay
    ovl.show_extras = not ovl.show_extras
    ovl.show_relationship_lines = not ovl.show_relationship_lines
    ovl.show_outline_selected = not ovl.show_outline_selected
    ovl.show_object_origins = not ovl.show_object_origins
    ovl.show_motion_paths = not ovl.show_motion_paths
    ovl.show_bones = not ovl.show_bones

    ovl.show_cursor = not ovl.show_cursor
    ovl.show_annotation = not ovl.show_annotation

def All_HideOverray():
    ovl = bpy.context.space_data.overlay
    ovl.show_extras = False
    ovl.show_relationship_lines = False
    ovl.show_outline_selected = False
    ovl.show_object_origins_all = False
    ovl.show_object_origins = False
    ovl.show_motion_paths = False
    ovl.show_bones = False

    ovl.show_cursor = False
    ovl.show_annotation = False


              
class Tgl_HideObjectType_OT_object(bpy.types.Operator):
    bl_idname = "view3d.tgl_hide_object_type"
    bl_label = "Toggle Hide Object Type"
 
    #処理本体
    def execute(self, context,):
        #ボーンが表示なら一旦すべて
        # ハイド
        ovl = bpy.context.space_data.overlay
        if ovl.show_bones == True:
            All_HideOverray()
        else:
            Tgl_HideOverray()
        return {'FINISHED'}
