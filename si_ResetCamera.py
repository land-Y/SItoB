import bpy
from mathutils import Matrix, Vector
from bpy.props import BoolProperty


#like softimage
view_matrix = Matrix([[1,  0.0, -0.0,   0.0], 
                    [0.0,  0.0,  1.0,   -1.7], 
                    [0.0, -1.0,  0.25, -15.0],
                    [0.0,  0.0,  0.0,   1.0],
                    ])

#charactor modeling
view_matrix1 = Matrix([[1,  0.0, -0.0,   0.0], 
                    [0.0,  0.0,  1.0,   -8.0], 
                    [0.0, -1.0,  0.25, -25.0],
                    [0.0,  0.0,  0.0,   1.0],
                    ])


class si_ResetCamera_OT_object(bpy.types.Operator):
    bl_idname = "view3d.si_reset_camera"
    bl_label = "Reset Camera"
    bl_description = "Reset Camera like Softimage"
    bl_options = {'REGISTER', 'UNDO'} 
    si_bool = BoolProperty(default=True, name = "Softimage or CharactorModeling", description = "Softimage or CharactorModeling")


    def execute(self, context,):
        #Softimageのリセットカメラに近い状態のマトリクス。
        #距離はdistanceで調整する。

        area = bpy.context.space_data.region_3d

        if self.si_bool:
            area.view_distance = 15
            area.view_matrix = view_matrix
        else:
            area.view_distance = 28
            area.view_matrix = view_matrix1

        #ショートカットに割り当てないとビューポート認知されない



        return {'FINISHED'}
