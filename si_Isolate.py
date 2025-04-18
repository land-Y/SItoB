import bpy

def dontmovecam():
    try:
        oLit = list()
        oObj = bpy.context.selected_objects
        oCol = list()

        for o in bpy.context.scene.objects:
            if o.type == "LIGHT":
                oLit.append(o.name)
                oCol.append(o.name)
        for o in oObj:
            oCol.append(o.name)
        for o in oCol:
            obj = bpy.context.scene.objects.get(o)
            if obj:
                obj.select_set(True)

        # アクティブビューの取得
        area = bpy.context.space_data
        if area and area.type == 'VIEW_3D' and area.region_3d:
            rg3d = area.region_3d
            vDis = rg3d.view_distance
            vMrx = rg3d.view_matrix

            # ローカルビューに切り替え後、リージョンに距離とマトリックス入れ直す
            bpy.ops.view3d.localview()
            rg3d.view_distance = vDis
            rg3d.view_matrix = vMrx
        else:
            print("Warning: Not in a valid 3D View context")
            return {'CANCELLED'}

        for o in oLit:
            obj = bpy.context.scene.objects.get(o)
            if obj:
                obj.select_set(False)

        return {'FINISHED'}
    except Exception as e:
        print(f"Error in dontmovecam: {str(e)}")
        return {'CANCELLED'}

class si_isolate_OT_object(bpy.types.Operator):
    bl_idname = "view3d.si_isolate"
    bl_label = "Isolate Selected"

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D'

    def execute(self, context):
        return dontmovecam()

classes = (
    si_isolate_OT_object,
)