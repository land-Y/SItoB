import bpy
from mathutils import Matrix, Vector
from bpy.props import BoolProperty

class si_ResetCamera_OT_object(bpy.types.Operator):
    bl_idname = "view3d.si_reset_camera"
    bl_label = "Reset Camera"
    bl_description = "Reset Camera like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 

    def execute(self, context,):
        #Softimageのリセットカメラに近い状態のマトリクス。
        #距離はdistanceで調整する。
        view_matrix = Matrix([[1,  0.0, -0.0,   0.0], 
                            [0.0,  0.0,  1.0,   -1.7], 
                            [0.0, -1.0,  0.25, -15.0],
                            [0.0,  0.0,  0.0,   1.0],
                            ])
        #ショートカットに割り当てないとビューポート認知されない
        area = bpy.context.space_data.region_3d
        area.view_distance = 15
        area.view_matrix = view_matrix


        return {'FINISHED'}
