import bpy
from bpy.props import BoolProperty

def Tgl_HideObjTyp():
    #表示させたくないものはシャープでコメントアウトしておく
    area = bpy.context.space_data
    #area.show_object_viewport_mesh = not area.show_object_viewport_mesh
    area.show_object_viewport_curve = not area.show_object_viewport_curve
    area.show_object_viewport_surf = not area.show_object_viewport_surf
    area.show_object_viewport_meta = not area.show_object_viewport_meta
    area.show_object_viewport_font = not area.show_object_viewport_font
    #area.show_object_viewport_hair = not area.show_object_viewport_hair
    area.show_object_viewport_pointcloud = not area.show_object_viewport_pointcloud
    area.show_object_viewport_volume = not area.show_object_viewport_volume
    #area.show_object_viewport_grease_pencil = not area.show_object_viewport_grease_pencil
    area.show_object_viewport_armature = not area.show_object_viewport_armature
    #area.show_object_viewport_lattice = not area.show_object_viewport_lattice
    area.show_object_viewport_empty = not area.show_object_viewport_empty
    area.show_object_viewport_light = not area.show_object_viewport_light
    area.show_object_viewport_light_probe = not area.show_object_viewport_light_probe
    area.show_object_viewport_camera = not area.show_object_viewport_camera
    area.show_object_viewport_speaker = not area.show_object_viewport_speaker


#表示トグルするかはユーザー側でプリファレンス上で選択させておく？
#一括TrueとFalseメニューも必要か？
def Tgl_DisplayObjTyp():
    area = bpy.context.space_data
    area.show_object_viewport_mesh = True
    area.show_object_viewport_curve = True
    area.show_object_viewport_surf = True
    area.show_object_viewport_meta = True
    area.show_object_viewport_font = True
    area.show_object_viewport_hair = True
    area.show_object_viewport_pointcloud = True
    area.show_object_viewport_volume = True
    area.show_object_viewport_grease_pencil = True
    area.show_object_viewport_armature = True
    area.show_object_viewport_lattice = True
    area.show_object_viewport_empty = True
    area.show_object_viewport_light = True
    area.show_object_viewport_light_probe = True
    area.show_object_viewport_camera = True
    area.show_object_viewport_speaker = True

              
class Tgl_HideObjectType(bpy.types.Operator):
    bl_idname = "view3d.tgl_hide_object_type"
    bl_label = "Toggle Hide Object Type"
 
    #処理本体
    def execute(self, context,):
        #メッシュが表示になってなかったら一旦全部表示させる。
        area = bpy.context.space_data
        if area.show_object_viewport_mesh == False:
            Tgl_DisplayObjTyp()
        else:
            Tgl_HideObjTyp()
        return {'FINISHED'}
