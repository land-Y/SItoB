import bpy

#ライトと選択中オブジェクトの合体。名前だけ抽出
def dontmovecam():

    oLit = list()
    oObj = bpy.context.selected_objects
    oCol = list()

    for o in bpy.context.scene.objects:
        if o.type== "LIGHT":
            oLit.append(o.name)
            oCol.append(o.name)
    for o in oObj:
        oCol.append(o.name)
    for o in oCol:
        obj = bpy.context.scene.objects.get(o)
        if obj: obj.select_set(True)

    #アクティブビューの取得
    area = bpy.context.space_data
    rg3d = area.region_3d
    vDis = rg3d.view_distance
    vMrx = rg3d.view_matrix

    #ローカルビューに切り替え後、リージョンに距離とマトリックス入れ直す
    bpy.ops.view3d.localview()
    rg3d.view_distance = vDis
    rg3d.view_matrix = vMrx

    for o in oLit:
        obj = bpy.context.scene.objects.get(o)
        if obj: obj.select_set(False)


class si_isolate_OT_object(bpy.types.Operator):
    bl_idname = "view3d.si_isolate"
    bl_label = "Isolate Selected"

    def execute(self, context):

        dontmovecam()

        return {'FINISHED'}