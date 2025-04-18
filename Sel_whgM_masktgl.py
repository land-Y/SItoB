import bpy

def sel_wheigtmaskmode(BoolToggle = False):
    #ウェイトペイントモードの時だけ実行できる
    oMode = bpy.context.mode
    if oMode == "PAINT_WEIGHT":
        bpy.ops.view3d.select('INVOKE_DEFAULT',toggle=BoolToggle)
        for Meshs in bpy.data.meshes:
            if Meshs.use_paint_mask == True:
                Meshs.use_paint_mask = False
                bpy.ops.view3d.select('INVOKE_DEFAULT',toggle=BoolToggle)
                Meshs.use_paint_mask = True
            if Meshs.use_paint_mask_vertex == True:
                Meshs.use_paint_mask_vertex = False
                bpy.ops.view3d.select('INVOKE_DEFAULT',toggle=BoolToggle)
                Meshs.use_paint_mask_vertex = True


class sel_wheigtmaskmode_OT_object(bpy.types.Operator):
    bl_idname = "view3d.sel_wheigtmaskmode"
    bl_label = "WeightMask mode Can SelectBone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel_wheigtmaskmode(BoolToggle = False)
        return {'FINISHED'}

class sel_wheigtmaskmode_tgl_OT_object(bpy.types.Operator):
    bl_idname = "view3d.sel_wheigtmaskmode_tgl"
    bl_label = "WeightMask mode Can SelectBone tgl"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel_wheigtmaskmode(BoolToggle = True)
        return {'FINISHED'}

classes = (
    sel_wheigtmaskmode_OT_object,
    sel_wheigtmaskmode_tgl_OT_object,
)