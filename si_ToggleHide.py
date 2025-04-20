import bpy
from bpy.props import StringProperty

# --- 設定 ---
prop_name = "SItoBHide"
scene_name = "Scene"
# --- 設定ここまで ---

# カスタムプロパティの登録
def register_properties():
    bpy.types.Scene.SItoBHide = StringProperty(
        name="SItoBHide",
        description="非表示オブジェクトのリスト",
        default=""
    )

def unregister_properties():
    del bpy.types.Scene.SItoBHide

class SI_OT_toggle_hide(bpy.types.Operator):
    bl_idname = "object.si_toggle_hide"
    bl_label = "SI Toggle Hide"
    bl_description = "選択したオブジェクトを非表示にし、非表示のオブジェクトを再表示します"
    bl_options = {'REGISTER', 'UNDO'}

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)

    def execute(self, context):
        # 対象シーンの取得と存在チェック
        target_scene = bpy.data.scenes.get(scene_name)

        if not target_scene:
            self.report({'ERROR'}, f"シーン '{scene_name}' が見つかりません。")
            return {'CANCELLED'}
        
        # 現在選択されているオブジェクトを取得
        selected_objects = context.selected_objects

        if selected_objects:
            # --- オブジェクトが選択されている場合の処理 ---
            object_names = []

            # 選択オブジェクトをループし、非表示処理と名前リスト作成
            for obj in selected_objects:
                object_names.append(obj.name)

                # hide_viewport が False なら True にする
                if obj.hide_viewport is False:
                    obj.hide_viewport = True
                # hide_render が False なら True にする
                if obj.hide_render is False:
                    obj.hide_render = True

            # オブジェクト名をカンマ区切りの文字列にする
            value_string = ",".join(object_names)

            # シーンにカスタムプロパティを上書き設定
            target_scene[prop_name] = value_string

            # 選択を解除 (Object Mode である必要がある)
            if context.mode == 'OBJECT':
                bpy.ops.object.select_all(action='DESELECT')

        else:
            # --- オブジェクトが選択されていない場合の処理 ---
            # カスタムプロパティが存在するか確認
            if prop_name in target_scene:
                value_string = target_scene.get(prop_name, "")

                # プロパティの値が空でないか確認
                if value_string:
                    # カンマで分割し、前後の空白を除去した名前のリストを作成
                    names_to_unhide = [name.strip() for name in value_string.split(',') if name.strip()]

                    if names_to_unhide:
                        # 念のため現在の選択をクリア (Object Mode である必要がある)
                        if context.mode == 'OBJECT':
                            bpy.ops.object.select_all(action='DESELECT')

                        found_count = 0
                        objects_to_select = []

                        # プロパティに記録された名前のオブジェクトを処理
                        for obj_name in names_to_unhide:
                            obj = bpy.data.objects.get(obj_name)
                            if obj:
                                obj.hide_viewport = False
                                obj.hide_render = False
                                objects_to_select.append(obj)
                                found_count += 1

                        # 見つかったオブジェクトを選択状態にする
                        if objects_to_select and context.mode == 'OBJECT':
                            context.view_layer.objects.active = objects_to_select[0]
                            for obj in objects_to_select:
                                obj.select_set(True)

        return {'FINISHED'}

class SI_OT_Show_Hidden_Objects(bpy.types.Operator):
    bl_idname = "object.si_show_hidden_objects"
    bl_label = "SI Show Hidden Objects"
    bl_description = "隠したオブジェクトを表示します（ビューポート＆レンダー）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # すべての隠されたオブジェクトを表示
        for obj in bpy.data.objects:
            if obj.hide_viewport or obj.hide_render:
                obj.hide_viewport = False
                obj.hide_render = False
                obj.select_set(True)
        
        self.report({'INFO'}, "すべての隠されたオブジェクトを表示しました")
        return {'FINISHED'}

class SI_OT_Hide_Unselected(bpy.types.Operator):
    bl_idname = "object.si_hide_unselected"
    bl_label = "SI Hide Unselected"
    bl_description = "選択されていないオブジェクトを隠します（ビューポート＆レンダー）"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # 現在選択されているオブジェクトを取得
        selected_objects = context.selected_objects
        hidden_count = 0

        # 選択されていないオブジェクトを隠す
        for obj in bpy.data.objects:
            if obj not in selected_objects:
                obj.hide_viewport = True
                obj.hide_render = True
                hidden_count += 1

        self.report({'INFO'}, f"{hidden_count}個のオブジェクトを隠しました")
        return {'FINISHED'}

classes = (
    SI_OT_toggle_hide,
    SI_OT_Show_Hidden_Objects,
    SI_OT_Hide_Unselected,
)

def register():
    register_properties()
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    unregister_properties()
