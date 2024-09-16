import bpy

class OUTLINER_OT_si_toggle_hide(bpy.types.Operator):
    bl_idname = "outliner.si_toggle_hide"
    bl_label = "si Toggle Hide"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if context.area.type == 'OUTLINER':
            # アウトライナー上で実行する場合
            for item in context.selected_ids:
                if item.bl_rna.identifier == "Object":
                    obj = bpy.data.objects[item.name]
                    obj.hide_viewport = not obj.hide_viewport
                    obj.hide_render = obj.hide_viewport
        else:
            # ビューポート中で実行する場合
            selected_objects = context.selected_objects

            if not selected_objects:
                # 選択されたオブジェクトがない場合、非表示のオブジェクトを表示する
                for obj in context.view_layer.objects:
                    if obj.hide_viewport:
                        obj.hide_viewport = False
                        obj.hide_render = False
                        obj.select_set(True)
            else:
                # 選択されたオブジェクトの表示/非表示を切り替える
                for obj in selected_objects:
                    obj.hide_viewport = not obj.hide_viewport
                    obj.hide_render = obj.hide_viewport
                    obj.select_set(not obj.hide_viewport)

        return {'FINISHED'}
