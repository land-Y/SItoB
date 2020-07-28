import bpy

class si_isolate_OT_object(bpy.types.Operator): #ローカルビューを非ズームで実行する
    bl_idname = "view3d.si_isolate"
    bl_label = "Isolate Selected"

    def execute(self, context):
        area = bpy.context.space_data
        rg3d = area.region_3d
        vDis = rg3d.view_distance
        vMrx = rg3d.view_matrix

        #ローカルビューに切り替え後、リージョンに距離とマトリックス入れ直す
        bpy.ops.view3d.localview()
        rg3d.view_distance = vDis
        rg3d.view_matrix = vMrx

        #ローカルビューじゃなければNONEを返す。IF分岐で利用する
        #lovw = bpy.context.space_data.local_view
        return {'FINISHED'}